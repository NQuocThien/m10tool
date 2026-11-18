import io
import os
import re
import time
import wave
import base64
import asyncio
import subprocess
import numpy as np
import edge_tts
from google import genai
from google.genai import types
from .config import (
    DEFAULT_VOICE,
    FFMPEG_PATH,
    GEMINI_TTS_MODEL,
    GEMINI_TTS_FALLBACK_MODELS,
    GEMINI_STYLE_VI,
    GEMINI_STYLE_EN,
    SCENE_TAIL_PAD_SEC,
)


def load_script(script_path):
    """Reads script file and returns list of clean text lines."""
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script file not found: {script_path}")

    with open(script_path, "r", encoding="utf-8") as f:
        raw_lines = [line.strip() for line in f if line.strip()]

    clean_lines = []
    for line in raw_lines:
        # Strip leading numbers like '01.', '1.', '01 -', etc.
        cleaned = re.sub(r'^\d+[\.\-_:\s]+', '', line).strip()
        if cleaned:
            clean_lines.append(cleaned)

    return clean_lines


def _wav_bytes_to_mp3(wav_bytes, out_mp3):
    """Transcodes in-memory WAV bytes to MP3 using ffmpeg with subtle tail breathing room."""
    cmd = [
        FFMPEG_PATH,
        "-y",
        "-f", "wav",
        "-i", "pipe:0",
        "-af", f"apad=pad_dur={SCENE_TAIL_PAD_SEC}",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        out_mp3,
    ]
    res = subprocess.run(cmd, input=wav_bytes, capture_output=True)
    if res.returncode != 0 or not os.path.exists(out_mp3) or os.path.getsize(out_mp3) == 0:
        err_msg = res.stderr.decode("utf-8", errors="ignore")[-400:]
        raise RuntimeError(f"FFmpeg WAV->MP3 failed: {err_msg}")


def _pcm_to_wav_bytes(pcm_int16: np.ndarray, sample_rate: int, n_channels: int = 1) -> bytes:
    """Packs int16 numpy array into valid WAV file bytes."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_int16.astype(np.int16).tobytes())
    return buf.getvalue()


def _split_wav_by_lines(wav_bytes: bytes, texts: list[str]) -> list[bytes]:
    """
    Splits a multi-line synthesized WAV into individual WAV byte buffers for each line
    by locating the deepest silence valleys around expected word-count proportions.
    """
    if len(texts) <= 1:
        return [wav_bytes]

    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)

    samples = np.frombuffer(raw, dtype=np.int16)
    if nch > 1:
        samples_mono = samples.reshape(-1, nch).mean(axis=1).astype(np.float32)
    else:
        samples_mono = samples.astype(np.float32)

    total_frames = len(samples_mono)
    win = max(1, int(sr * 0.02))  # 20ms window
    n_win = total_frames // win
    if n_win < len(texts) * 5:
        # Fallback to proportional split if clip is unexpectedly short
        cuts = [int(total_frames * i / len(texts)) for i in range(len(texts) + 1)]
    else:
        rms = np.sqrt(np.mean(samples_mono[:n_win * win].reshape(n_win, win) ** 2, axis=1))
        kernel_size = 15  # 300ms smoothing window
        smooth_rms = np.convolve(rms, np.ones(kernel_size) / kernel_size, mode="same")

        weights = [max(1, len(t.split())) for t in texts]
        total_w = sum(weights)
        tot_sec = total_frames / sr

        cut_frames = [0]
        cum_w = 0
        for i in range(len(texts) - 1):
            cum_w += weights[i]
            exp_sec = (cum_w / total_w) * tot_sec
            prev_sec = cut_frames[-1] / sr
            min_sec = max(prev_sec + 0.6, exp_sec - 3.5)
            max_sec = min(tot_sec - 0.6 * (len(texts) - 1 - i), exp_sec + 3.5)

            lo = max(1, int(min_sec / 0.02))
            hi = min(n_win - 1, int(max_sec / 0.02))
            if hi <= lo:
                best_win = int(exp_sec / 0.02)
            else:
                # Slight distance penalty so we prefer the silence valley closest to expected boundary
                window_indices = np.arange(lo, hi)
                dist_penalty = np.abs(window_indices * 0.02 - exp_sec) * 4.0
                score = smooth_rms[lo:hi] + dist_penalty
                best_win = lo + int(np.argmin(score))

            cut_frames.append(min(total_frames, best_win * win))
        cut_frames.append(total_frames)
        cuts = cut_frames

    out_wavs = []
    for i in range(len(texts)):
        s_frame = cuts[i] * nch
        e_frame = cuts[i + 1] * nch
        chunk = samples[s_frame:e_frame]
        # Trim leading/trailing dead silence (< 80 amplitude) leaving 80ms pad
        if len(chunk) > sr // 5:
            mono_chunk = np.abs(chunk.reshape(-1, nch).mean(axis=1)) if nch > 1 else np.abs(chunk)
            active = np.where(mono_chunk > 80)[0]
            if len(active) > 0:
                pad = int(sr * 0.08)
                t_start = max(0, active[0] - pad) * nch
                t_end = min(len(chunk) // nch, active[-1] + pad) * nch
                if t_end > t_start:
                    chunk = chunk[t_start:t_end]
        out_wavs.append(_pcm_to_wav_bytes(chunk, sr, nch))
    return out_wavs


def _resolve_gemini_style(audio_dir, style):
    """Selects default narration style based on language directory if style is omitted."""
    if style:
        return style
    dir_name = os.path.basename(os.path.normpath(audio_dir)).lower()
    if dir_name.endswith("_en"):
        return GEMINI_STYLE_EN
    return GEMINI_STYLE_VI


def _create_fast_genai_client():
    """Creates a Gemini Client that does NOT silently sleep 3 hours on 429 Retry-After headers."""
    return genai.Client(
        http_options=types.HttpOptions(
            api_version="v1beta",
            timeout=60000,
            retry_options=types.HttpRetryOptions(attempts=1),
        )
    )


def _adapt_voice_and_content_for_model(model_name: str, text: str, voice_name: str, style: str):
    """Adapts voice name and speech_metadata annotations for models that don't support 3.8 extensions."""
    supports_38_features = "3.8" in model_name
    content_item = {"type": "text", "text": text}
    if supports_38_features and style:
        content_item["annotations"] = [{
            "type": "speech_metadata",
            "style": style,
        }]

    effective_voice = voice_name
    if not supports_38_features:
        # Older TTS models only accept standard prebuilt voices (Charon, Kore, Puck, Orus, Aoede, Sulafat, Sadaltager)
        standard_voices = {"Charon", "Kore", "Puck", "Orus", "Aoede", "Sulafat", "Sadaltager", "Fenrir", "Leda", "Zephyr"}
        if voice_name not in standard_voices:
            effective_voice = "Charon"

    return content_item, effective_voice


def _call_gemini_tts_with_fallback(client, text: str, voice_name: str, style: str, exhausted_models: set) -> tuple[bytes, str]:
    """
    Calls Gemini TTS across GEMINI_TTS_FALLBACK_MODELS, immediately failing over when a model
    hits 429 RateLimitError instead of hanging.
    """
    candidates = [m for m in GEMINI_TTS_FALLBACK_MODELS if m not in exhausted_models]
    if not candidates:
        candidates = list(GEMINI_TTS_FALLBACK_MODELS)

    last_err = None
    for model_name in candidates:
        content_item, eff_voice = _adapt_voice_and_content_for_model(model_name, text, voice_name, style)
        for attempt in range(1, 3):
            try:
                interaction = client.interactions.create(
                    model=model_name,
                    input=[{
                        "type": "user_input",
                        "content": [content_item],
                    }],
                    response_format={"type": "audio"},
                    generation_config={
                        "speech_config": [{"voice": eff_voice}],
                    },
                    timeout=50.0,
                )
                audio_obj = getattr(interaction, "output_audio", None)
                if not audio_obj or not getattr(audio_obj, "data", None):
                    raise RuntimeError(f"{model_name} returned empty output_audio")
                return base64.b64decode(audio_obj.data), f"{model_name}:{eff_voice}"
            except Exception as e:
                last_err = e
                err_str = str(e)
                if "429" in err_str or "RateLimit" in type(e).__name__ or "too_many_requests" in err_str.lower():
                    print(f"  [WARN] Model {model_name} chạm giới hạn 429 Quota -> chuyển ngay sang model dự phòng...", flush=True)
                    exhausted_models.add(model_name)
                    break
                if attempt < 2:
                    time.sleep(1.5)
                else:
                    print(f"  [WARN] Lỗi trên {model_name}: {err_str[:160]} -> thử model tiếp theo...", flush=True)
                    break

    raise RuntimeError(f"Tất cả Gemini TTS models đều lỗi hoặc hết quota: {last_err}")


def _synthesize_line_gemini(client, idx, total, text, voice_name, style, out_mp3, exhausted_models=None):
    """Synthesizes a single script line via Gemini TTS with auto model failover and saves as MP3."""
    if exhausted_models is None:
        exhausted_models = set()
    wav_bytes, used_label = _call_gemini_tts_with_fallback(client, text, voice_name, style, exhausted_models)
    _wav_bytes_to_mp3(wav_bytes, out_mp3)
    print(f"  [{idx:02d}/{total}] Generated {os.path.basename(out_mp3)} ({used_label})", flush=True)


def _synthesize_batch_gemini(client, batch_items, total, voice_name, style, exhausted_models, batch_size=5):
    """
    Synthesizes pending items in chunks of up to `batch_size` lines per API request
    so a 30-line script only consumes ~6 requests (preventing Free Tier 10 RPD exhaustion
    and keeping voice consistent across the entire video).
    """
    for start_i in range(0, len(batch_items), batch_size):
        chunk = batch_items[start_i:start_i + batch_size]
        if len(chunk) == 1:
            idx, text, out_mp3 = chunk[0]
            _synthesize_line_gemini(client, idx, total, text, voice_name, style, out_mp3, exhausted_models)
            continue

        texts = [item[1] for item in chunk]
        joined_text = "\n\n...\n\n".join(texts)
        idx_range = f"{chunk[0][0]:02d}..{chunk[-1][0]:02d}"
        print(f"  [Batch {idx_range}/{total:02d}] Đang tạo gộp {len(chunk)} câu thoại trong 1 request...", flush=True)

        try:
            wav_bytes, used_label = _call_gemini_tts_with_fallback(client, joined_text, voice_name, style, exhausted_models)
            split_wavs = _split_wav_by_lines(wav_bytes, texts)
            for (idx, _, out_mp3), line_wav in zip(chunk, split_wavs):
                _wav_bytes_to_mp3(line_wav, out_mp3)
                print(f"  [{idx:02d}/{total}] Generated {os.path.basename(out_mp3)} ({used_label})", flush=True)
        except Exception as e:
            print(f"  [WARN] Tạo gộp batch {idx_range} gặp lỗi ({e}), chuyển sang tạo từng câu...", flush=True)
            for idx, text, out_mp3 in chunk:
                _synthesize_line_gemini(client, idx, total, text, voice_name, style, out_mp3, exhausted_models)


async def _synthesize_line_edge(idx, total, text, voice, out_mp3, max_retries=8):
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            communicate = edge_tts.Communicate(text, voice)
            audio_chunk = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunk.extend(chunk["data"])

            if len(audio_chunk) > 0:
                with open(out_mp3, "wb") as f_out:
                    f_out.write(audio_chunk)
                print(f"  [{idx:02d}/{total}] Generated {os.path.basename(out_mp3)}", flush=True)
                await asyncio.sleep(0.5)
                return
            else:
                raise edge_tts.exceptions.NoAudioReceived("Received empty audio stream")
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                await asyncio.sleep(2.0 * attempt)
            else:
                raise last_err


async def _batch_generate_edge(items, total, voice):
    for idx, text, out_mp3 in items:
        await _synthesize_line_edge(idx, total, text, voice, out_mp3)


def generate_audio(script_path, audio_dir, voice=DEFAULT_VOICE, force=False, style=None):
    """
    Generates mp3 files for each line in script_path into audio_dir.
    Supports Gemini TTS ('gemini:<VoiceName>') and Edge TTS ('*-Neural').
    Returns list of dicts: [{'index': 1, 'text': '...', 'audio_path': '...'}]
    """
    os.makedirs(audio_dir, exist_ok=True)
    lines = load_script(script_path)

    results = []
    pending_items = []

    print(f"-> Generating voiceover ({len(lines)} lines) using voice: {voice}", flush=True)

    for idx, text in enumerate(lines, 1):
        out_mp3 = os.path.join(audio_dir, f"{idx:02d}_voice.mp3")
        needs_gen = force or not os.path.exists(out_mp3) or os.path.getsize(out_mp3) == 0
        if needs_gen:
            pending_items.append((idx, text, out_mp3))
        else:
            print(f"  [{idx:02d}/{len(lines)}] Cached {os.path.basename(out_mp3)}", flush=True)

    if pending_items:
        if voice.startswith("gemini:"):
            voice_name = voice.split(":", 1)[1]
            narration_style = _resolve_gemini_style(audio_dir, style)
            client = _create_fast_genai_client()
            exhausted_models = set()
            _synthesize_batch_gemini(
                client, pending_items, len(lines), voice_name, narration_style, exhausted_models, batch_size=5
            )
        else:
            asyncio.run(_batch_generate_edge(pending_items, len(lines), voice))
        print(f"  [OK] Generated {len(pending_items)} audio files successfully.", flush=True)

    full_audio = bytearray()
    for idx, text in enumerate(lines, 1):
        out_mp3 = os.path.join(audio_dir, f"{idx:02d}_voice.mp3")
        with open(out_mp3, "rb") as f_in:
            full_audio.extend(f_in.read())
        results.append({
            "index": idx,
            "text": text,
            "audio_path": out_mp3
        })

    master_mp3 = os.path.join(audio_dir, "full_voiceover.mp3")
    with open(master_mp3, "wb") as f_out:
        f_out.write(full_audio)

    return results


def synthesize_preview(text, out_mp3, voice=DEFAULT_VOICE, lang="vi", force=False):
    """Synthesizes a single preview line to out_mp3 using Gemini TTS or Edge TTS."""
    os.makedirs(os.path.dirname(out_mp3), exist_ok=True)
    if not force and os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 0:
        return out_mp3

    if voice.startswith("gemini:"):
        voice_name = voice.split(":", 1)[1]
        style = GEMINI_STYLE_EN if lang == "en" else GEMINI_STYLE_VI
        client = _create_fast_genai_client()
        _synthesize_line_gemini(client, 1, 1, text, voice_name, style, out_mp3)
    else:
        asyncio.run(_synthesize_line_edge(1, 1, text, voice, out_mp3))
    return out_mp3
