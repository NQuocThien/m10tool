import os
import re
import asyncio
import edge_tts
from .config import DEFAULT_VOICE

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

async def _synthesize_line(idx, total, text, voice, out_mp3, max_retries=8):
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

async def _batch_generate(items, total, voice):
    for idx, text, out_mp3 in items:
        await _synthesize_line(idx, total, text, voice, out_mp3)

def generate_audio(script_path, audio_dir, voice=DEFAULT_VOICE, force=False):
    """
    Generates mp3 files for each line in script_path into audio_dir.
    Returns list of dicts: [{'index': 1, 'text': '...', 'audio_path': '...'}]
    """
    os.makedirs(audio_dir, exist_ok=True)
    lines = load_script(script_path)
    
    results = []
    pending_items = []
    
    print(f"-> Generating voiceover ({len(lines)} lines) using voice: {voice}")
    
    for idx, text in enumerate(lines, 1):
        out_mp3 = os.path.join(audio_dir, f"{idx:02d}_voice.mp3")
        needs_gen = force or not os.path.exists(out_mp3) or os.path.getsize(out_mp3) == 0
        if needs_gen:
            pending_items.append((idx, text, out_mp3))
        else:
            print(f"  [{idx:02d}/{len(lines)}] Cached {os.path.basename(out_mp3)}")

    if pending_items:
        asyncio.run(_batch_generate(pending_items, len(lines), voice))
        print(f"  [OK] Generated {len(pending_items)} audio files successfully.")

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
