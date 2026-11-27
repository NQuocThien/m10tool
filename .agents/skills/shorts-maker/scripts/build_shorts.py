import argparse
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

# Resolve repo root (c:\Workspace2\Video) from .agents/skills/shorts-maker/scripts/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.config import (
    DEFAULT_BGM_VOLUME,
    DEFAULT_FPS,
    DEFAULT_VOICE,
    FFMPEG_PATH,
    PROJECTS_DIR,
    RESOURCES_DIR,
    SHORT_HOOK_BANNER_SEC,
    SHORT_IDEAL_MAX_SCENES,
    SHORT_MAX_DURATION_SEC,
)
from core.renderer import get_bgm_path
from core.sorter import get_sorted_images
from core.subtitles import generate_subtitles
from core.tts import generate_audio, load_script
import make_shorts as ms
import re
from PIL import Image, ImageDraw

REQUIRED_FIELDS = [
    "id",
    "badge",
    "title_line1",
    "title_line2",
    "accent_color",
    "scenes",
    "thumb_scene",
    "thumb_big_text",
    "thumb_sub_badge",
    "yt_titles",
    "yt_description",
    "yt_pinned_comment",
    "thumb_desc",
    "thumb_prompt",
]


def resolve_project_paths(proj_name, lang, media_dir_override=None, audio_dir_override=None):
    """
    Resolve script, media, audio, config, and output paths for both:
    - V3 Shorts-First projects (script_short_<lang>.txt + video_short_<lang>/ + audio_short_<lang>/)
    - Legacy / Long-form projects (script_<lang>.txt + video_<lang>/ + audio_<lang>/)
    """
    proj_dir = os.path.join(PROJECTS_DIR, proj_name)
    if not os.path.isdir(proj_dir):
        raise FileNotFoundError(f"Project not found: {proj_dir}")

    short_script = os.path.join(proj_dir, f"script_short_{lang}.txt")
    long_script = os.path.join(proj_dir, f"script_{lang}.txt")
    fallback_script = os.path.join(proj_dir, "script.txt")
    config_path = os.path.join(proj_dir, f"shorts_config_{lang}.json")

    # Determine max scene referenced in shorts_config so dual-stage projects pick the matching script
    max_cfg_sc = 0
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f_cfg:
                raw_cfgs = json.load(f_cfg)
            if isinstance(raw_cfgs, list):
                for c in raw_cfgs:
                    for s in c.get("scenes", []) + ([c["thumb_scene"]] if "thumb_scene" in c else []):
                        if isinstance(s, int) and s > max_cfg_sc:
                            max_cfg_sc = s
        except Exception:
            pass

    is_short_first = False
    if os.path.isfile(short_script):
        short_len = len(load_script(short_script))
        if max_cfg_sc > short_len and os.path.isfile(long_script):
            script_path = long_script
        else:
            script_path = short_script
            is_short_first = True
    elif os.path.isfile(long_script):
        script_path = long_script
    elif os.path.isfile(fallback_script):
        script_path = fallback_script
    else:
        raise FileNotFoundError(f"Script not found in {proj_dir} (checked script_short_{lang}.txt and script_{lang}.txt)")

    def _has_valid_media(d):
        if not os.path.isdir(d):
            return False
        exts = (".mp4", ".mov", ".m4v", ".webm", ".jpg", ".jpeg", ".png", ".webp")
        return any(f.lower().endswith(exts) for f in os.listdir(d))

    if media_dir_override:
        media_dir = media_dir_override if os.path.isabs(media_dir_override) else os.path.join(proj_dir, media_dir_override)
    else:
        candidates = (
            [f"video_short_{lang}", f"imgs_short_{lang}", f"video_{lang}", f"imgs_{lang}", "imgs-clean", "imgs"]
            if is_short_first
            else [f"video_{lang}", f"imgs_{lang}", "imgs-clean", "imgs", f"video_short_{lang}"]
        )
        media_dir = next(
            (os.path.join(proj_dir, c) for c in candidates if _has_valid_media(os.path.join(proj_dir, c))),
            None,
        )
        if not media_dir:
            media_dir = next(
                (os.path.join(proj_dir, c) for c in candidates if os.path.isdir(os.path.join(proj_dir, c))),
                None,
            )
    if not media_dir or not os.path.isdir(media_dir):
        raise FileNotFoundError(f"Media directory not found in {proj_dir}")

    if audio_dir_override:
        audio_dir = audio_dir_override if os.path.isabs(audio_dir_override) else os.path.join(proj_dir, audio_dir_override)
    else:
        if is_short_first:
            audio_dir = os.path.join(proj_dir, f"audio_short_{lang}")
        else:
            audio_candidates = [f"audio_{lang}", "audio"]
            audio_dir = next(
                (os.path.join(proj_dir, c) for c in audio_candidates if os.path.isdir(os.path.join(proj_dir, c))),
                os.path.join(proj_dir, f"audio_{lang}"),
            )

    config_path = os.path.join(proj_dir, f"shorts_config_{lang}.json")
    shorts_out_dir = os.path.join(proj_dir, f"shorts_{lang}")
    has_long_video = os.path.isfile(os.path.join(proj_dir, f"{proj_name}_{lang}.mp4"))
    return {
        "proj_dir": proj_dir,
        "script_path": script_path,
        "media_dir": media_dir,
        "audio_dir": audio_dir,
        "config_path": config_path,
        "shorts_out_dir": shorts_out_dir,
        "is_short_first": is_short_first,
        "has_long_video": has_long_video,
    }


def load_and_validate_configs(config_path, total_scenes, proj_name=None, lang="vi"):
    """Load shorts_config_<lang>.json (with legacy lfp_vs_ncm fallback) and validate required fields."""
    if not os.path.isfile(config_path):
        if proj_name == "lfp_vs_ncm":
            configs = ms.SHORTS_CONFIG_EN if lang == "en" else ms.SHORTS_CONFIG
        else:
            raise FileNotFoundError(f"Shorts config not found: {config_path}")
    else:
        with open(config_path, "r", encoding="utf-8") as f:
            configs = json.load(f)

    if not isinstance(configs, list) or not configs:
        raise ValueError("Shorts config must be a non-empty JSON array.")

    for idx, cfg in enumerate(configs, 1):
        missing = [k for k in REQUIRED_FIELDS if k not in cfg]
        if missing:
            raise ValueError(f"Episode #{idx} ({cfg.get('id', '?')}) missing fields: {missing}")
        if not cfg["scenes"]:
            raise ValueError(f"Episode {cfg['id']} has empty scenes list.")
        for sc in cfg["scenes"] + [cfg["thumb_scene"]]:
            if not isinstance(sc, int) or sc < 1 or sc > total_scenes:
                raise ValueError(f"Episode {cfg['id']} scene {sc} out of range 1..{total_scenes}")

    return configs


_WEAK_OPENER_PREFIXES = (
    "xét về bài toán",
    "với lộ trình",
    "trong bài toán",
    "điểm khác biệt rõ nhất",
    "khi mua xe máy điện, lầm tưởng",
    "trên cùng một chiếc xe",
    "thủ phạm thứ",
    "tiếp theo là",
)


_SPOILER_TITLE_PATTERNS = (
    "giống hệt nhau",
    "như nhau 100%",
    "câu trả lời là",
    "kết quả là",
)


def audit_shorts_retention_risks(configs, all_lines, all_media):
    """
    V3 Retention Risk Auditor:
    Detects static .jpg openers, duplicated scene[0], 100% static episodes, weak verbal hooks,
    over-length episodes (>38s / >7 scenes), banned 'TẬP X/N' labels, and spoiler/overlong titles.
    """
    vid_exts = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
    warnings = []
    seen_openers = {}

    for cfg in configs:
        ep_id = cfg["id"]
        scenes = cfg["scenes"]
        sc0 = scenes[0]

        # 1. Duplicate opening scene across episodes
        if sc0 in seen_openers:
            warnings.append(
                f"[RETENTION RISK] {ep_id}: Scene #{sc0:02d} duplicates opener of '{seen_openers[sc0]}'. "
                f"Returning viewers will think it is a repost and swipe away!"
            )
        else:
            seen_openers[sc0] = ep_id

        # 2. Opening scene is a static image instead of animated .mp4
        if 1 <= sc0 <= len(all_media):
            media0 = all_media[sc0 - 1]
            ext0 = os.path.splitext(media0)[1].lower()
            if ext0 not in vid_exts:
                warnings.append(
                    f"[RETENTION RISK] {ep_id}: Opening scene #{sc0:02d} ({os.path.basename(media0)}) is a STATIC image. "
                    f"First 3s of every Short should be an animated [VIDEO] .mp4 clip!"
                )

        # 3. 100% static slideshow check
        vid_count = sum(
            1 for sc in scenes
            if 1 <= sc <= len(all_media) and os.path.splitext(all_media[sc - 1])[1].lower() in vid_exts
        )
        if vid_count == 0:
            warnings.append(
                f"[RETENTION RISK] {ep_id}: 0 animated .mp4 clips across scenes {scenes} (100% static images)!"
            )

        # 4. Weak academic opener or missing concrete numbers in first spoken line
        if 1 <= sc0 <= len(all_lines):
            first_line = all_lines[sc0 - 1].strip()
            lower_line = first_line.lower()
            if any(lower_line.startswith(p) for p in _WEAK_OPENER_PREFIXES):
                warnings.append(
                    f"[RETENTION RISK] {ep_id}: Scene #{sc0:02d} opens with academic transition ('{first_line[:48]}...'). "
                    f"Use a shocking number or direct pain hook!"
                )
            elif not any(ch.isdigit() for ch in first_line):
                warnings.append(
                    f"[RETENTION TIP] {ep_id}: Opening scene #{sc0:02d} has no concrete number ('{first_line[:48]}...'). "
                    f"Adding a number in the first 3s boosts stop-scroll rate."
                )

        # 5. Scene count & estimated duration check (>38s kills APV on new channels)
        total_words = sum(len(all_lines[sc - 1].split()) for sc in scenes if 1 <= sc <= len(all_lines))
        # At 1.18x tightened Vietnamese TTS (~3.35 words/sec + 0.08s pad/scene)
        est_dur_sec = (total_words / 3.35) + len(scenes) * 0.12
        if len(scenes) > SHORT_IDEAL_MAX_SCENES or est_dur_sec > SHORT_MAX_DURATION_SEC:
            warnings.append(
                f"[RETENTION RISK] {ep_id}: Too long ({len(scenes)} scenes, ~{est_dur_sec:.1f}s est > {SHORT_MAX_DURATION_SEC:.0f}s target). "
                f"Trim to 5-7 crisp scenes (24-34s) so APV exceeds 85%!"
            )

        # 6. Ban 'TẬP 1/4' / 'EPISODE 1' badges that cause cold-feed viewers to swipe away
        for fld in ("badge", "title_line1", "thumb_sub_badge"):
            val = str(cfg.get(fld, ""))
            if re.search(r"(?i)\b(tập|tap|episode|part)\s*\d+", val):
                warnings.append(
                    f"[RETENTION RISK] {ep_id}: Field '{fld}' ('{val}') contains episode numbering. "
                    f"Cold Shorts viewers swipe away from multi-part labels — make each Short 100% standalone!"
                )
                break

        # 7. Audit YouTube titles for length (>72 chars) and answer-spoiling phrases
        for yt_t in cfg.get("yt_titles", []):
            clean_t = re.sub(r"(?i)#shorts\b", "", yt_t).strip()
            if len(clean_t) > 72:
                warnings.append(
                    f"[CTR TIP] {ep_id}: Title too long ({len(clean_t)} chars > 72, truncates on mobile): '{clean_t[:52]}...'"
                )
            if any(sp in clean_t.lower() for sp in _SPOILER_TITLE_PATTERNS):
                warnings.append(
                    f"[CURIOSITY RISK] {ep_id}: Title spoils the verdict upfront ('{clean_t[:55]}...'). Hide the answer to preserve Curiosity Gap!"
                )

    return warnings


def format_overlay_badge(cfg, ep_idx, total_eps, lang="vi"):
    """Format clean standalone topic badge (automatically strips legacy 'TẬP X/N' numbering)."""
    raw_badge = re.sub(r"(?i)\b(tập|tap|episode|ep|part)\s*\d+\s*(/\s*\d+)?\s*[•\-:|]*\s*", "", cfg.get("badge", "")).strip(" •-:|")
    main_topic = cfg.get("main_topic", "").strip()
    if main_topic and raw_badge and main_topic.upper() not in raw_badge.upper():
        return f"{main_topic.upper()} • {raw_badge}"
    return (main_topic.upper() or raw_badge or ("SQUEEZING TECH" if lang == "en" else "VẮT CHANH CÔNG NGHỆ"))


def format_step_label(ep_idx, total_eps, scene_order_idx, total_scenes_in_ep, lang="vi"):
    """Format subtitle card header right label with Episode + Scene progress."""
    if lang == "en":
        return f"Part {ep_idx}/{total_eps} • Scene {scene_order_idx}/{total_scenes_in_ep}"
    return f"Tập {ep_idx}/{total_eps} • Cảnh {scene_order_idx}/{total_scenes_in_ep}"


def _probe_audio_duration(audio_path):
    import re
    res = subprocess.run([FFMPEG_PATH, "-i", audio_path], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if not m:
        return 2.2
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def _prepare_punchy_short_audio(src_mp3, dst_mp3, speed=1.18, sfx_path=None):
    """Trim dead silence, tighten pacing (1.18x), boost vocal clarity, and layer subtle transition SFX."""
    voice_af = (
        f"silenceremove=start_periods=1:start_threshold=-42dB,"
        f"areverse,silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
        f"atempo={speed:.2f},"
        f"equalizer=f=3000:t=q:w=1.5:g=2.5,"
        f"apad=pad_dur=0.06"
    )
    if sfx_path and os.path.isfile(sfx_path):
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", src_mp3,
            "-i", sfx_path,
            "-filter_complex",
            f"[0:a]{voice_af}[v];[1:a]volume=0.35[sfx];[v][sfx]amix=inputs=2:duration=first:dropout_transition=0[aout]",
            "-map", "[aout]",
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            dst_mp3,
        ]
    else:
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", src_mp3,
            "-af", voice_af,
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            dst_mp3,
        ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0 or not os.path.isfile(dst_mp3) or os.path.getsize(dst_mp3) == 0:
        shutil.copyfile(src_mp3, dst_mp3)
    return dst_mp3


def render_short_outro_cta_clip(cfg, overlay_badge, lang, temp_dir, fps):
    """Render a ~2-2.5s Outro Hook CTA card directing viewers to the full video in pinned comment."""
    W, H = 1080, 1920
    is_en = (lang == "en")
    bg_rgba = (11, 19, 43, 255) if is_en else (250, 247, 242, 255)
    card_rgba = (19, 31, 66, 255) if is_en else (255, 253, 249, 255)
    text_main = (248, 250, 252, 255) if is_en else (28, 25, 23, 255)
    border_rgba = (0, 229, 255, 255) if is_en else (28, 25, 23, 255)
    accent_primary = (118, 255, 3, 255) if is_en else (211, 84, 0, 255)
    accent_yellow = (255, 179, 0, 255) if is_en else (244, 196, 48, 255)
    accent_green = (0, 229, 255, 255) if is_en else (124, 179, 66, 255)

    canvas = Image.new("RGBA", (W, H), bg_rgba)
    draw = ImageDraw.Draw(canvas)

    # Decorative corner circles
    draw.ellipse((-180, -180, 320, 320), fill=(accent_yellow[0], accent_yellow[1], accent_yellow[2], 55))
    draw.ellipse((W - 320, H - 360, W + 180, H + 140), fill=(accent_green[0], accent_green[1], accent_green[2], 50))

    # Top brand pill
    brand_text = "SQUEEZING TECH" if is_en else "VẮT CHANH CÔNG NGHỆ"
    pill_w, pill_h = 560, 84
    pill_x, pill_y = (W - pill_w) // 2, 240
    draw.rounded_rectangle((pill_x, pill_y, pill_x + pill_w, pill_y + pill_h), radius=42, fill=card_rgba, outline=border_rgba, width=4)
    logo_path = os.path.join(RESOURCES_DIR, "logo_vi.jpg")
    if not is_en and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA").resize((60, 60), Image.LANCZOS)
            mask = Image.new("L", (60, 60), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 60, 60), fill=255)
            canvas.paste(logo, (pill_x + 16, pill_y + 12), mask)
        except Exception:
            pass
    font_brand = ms._load_font(30, bold=True)
    draw.text((pill_x + pill_w // 2 + (24 if not is_en else 0), pill_y + pill_h // 2), brand_text, font=font_brand, fill=text_main, anchor="mm")

    # Main topic pill
    font_badge = ms._load_font(26, bold=True)
    main_topic = cfg.get("main_topic", overlay_badge).upper()
    bb = draw.textbbox((0, 0), main_topic, font=font_badge)
    bw = min(940, (bb[2] - bb[0]) + 64)
    bx, by = (W - bw) // 2, 365
    draw.rounded_rectangle((bx, by, bx + bw, by + 62), radius=31, fill=accent_primary, outline=border_rgba, width=3)
    draw.text((W // 2, by + 31), main_topic, font=font_badge, fill=(255, 255, 255, 255) if not is_en else (11, 19, 43, 255), anchor="mm")

    # Center CTA Card
    cx1, cy1, cx2, cy2 = 75, 560, W - 75, 1340
    draw.rounded_rectangle((cx1 + 10, cy1 + 12, cx2 + 10, cy2 + 12), radius=42, fill=border_rgba)
    draw.rounded_rectangle((cx1, cy1, cx2, cy2), radius=42, fill=card_rgba, outline=border_rgba, width=6)

    # Top yellow header bar inside card
    draw.rounded_rectangle((cx1 + 36, cy1 + 44, cx2 - 36, cy1 + 148), radius=24, fill=accent_yellow, outline=border_rgba, width=4)
    font_sub = ms._load_font(40, bold=True)
    hdr_txt = "WANT THE FULL BREAKDOWN?" if is_en else "MUỐN XEM TRỌN BỘ PHÂN TÍCH?"
    draw.text((W // 2, cy1 + 96), hdr_txt, font=font_sub, fill=(28, 25, 23, 255), anchor="mm")

    # Giant CTA headline
    font_big = ms._load_font(64, bold=True)
    line1 = "WATCH FULL VIDEO" if is_en else "XEM FULL VIDEO GỐC"
    line2 = "TAP RELATED LINK BELOW!" if is_en else "GÓC DƯỚI BÊN TRÁI!"
    draw.text((W // 2, cy1 + 295), line1, font=font_big, fill=accent_primary, anchor="mm")
    draw.text((W // 2, cy1 + 395), line2, font=font_big, fill=accent_green, anchor="mm")

    # Related video arrow pill button
    draw.rounded_rectangle((cx1 + 85, cy1 + 520, cx2 - 85, cy1 + 630), radius=55, fill=accent_primary, outline=border_rgba, width=5)
    font_btn = ms._load_font(36, bold=True)
    btn_txt = "▶ TAP RELATED VIDEO BELOW" if is_en else "▶ BẤM VIDEO LIÊN QUAN BÊN DƯỚI"
    draw.text((W // 2, cy1 + 575), btn_txt, font=font_btn, fill=(255, 255, 255, 255) if not is_en else (11, 19, 43, 255), anchor="mm")

    # Slogan footer
    font_slogan = ms._load_font(30, bold=True)
    slogan = "Extracting Value from Everyday Tech" if is_en else "Vắt sạch thông số, giữ lại cách dùng!"
    draw.text((W // 2, 1460), slogan, font=font_slogan, fill=text_main, anchor="mm")

    cta_png = os.path.join(temp_dir, "outro_cta.png")
    canvas.convert("RGB").save(cta_png, quality=96)

    cta_audio = os.path.join(RESOURCES_DIR, f"shorts_cta_{lang}.mp3")
    if os.path.isfile(cta_audio) and os.path.getsize(cta_audio) > 0:
        punchy_cta = os.path.join(temp_dir, f"punchy_cta_{lang}.mp3")
        _prepare_punchy_short_audio(cta_audio, punchy_cta, speed=1.22, sfx_path=None)
        cta_use_audio = punchy_cta if os.path.isfile(punchy_cta) else cta_audio
        cta_dur = max(1.5, min(2.2, _probe_audio_duration(cta_use_audio)))
        has_voice = True
    else:
        cta_use_audio = cta_audio
        cta_dur = 1.6
        has_voice = False

    total_frames = max(1, int(cta_dur * fps))
    step = 0.05 / max(1, total_frames)
    vf = (
        f"scale={W}:{H},zoompan=z='min(zoom+{step:.6f},1.05)':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={W}x{H}:fps={fps},format=yuv420p"
    )
    outro_mp4 = os.path.join(temp_dir, "short_outro_cta.mp4")

    if has_voice:
        cmd = [
            FFMPEG_PATH, "-y",
            "-loop", "1", "-t", f"{cta_dur:.3f}", "-i", cta_png,
            "-i", cta_use_audio,
            "-vf", vf,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest",
            outro_mp4,
        ]
    else:
        cmd = [
            FFMPEG_PATH, "-y",
            "-loop", "1", "-t", f"{cta_dur:.3f}", "-i", cta_png,
            "-f", "lavfi", "-t", f"{cta_dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", vf,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest",
            outro_mp4,
        ]

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg CTA outro error: {res.stderr[-300:]}")
    return outro_mp4, cta_dur


def build_shorts(proj_name, lang, paths, configs, skip_outro=True, force_outro=False, voice=None, force_tts=False):
    """
    V3 Shorts Builder:
    - Auto-synthesizes missing TTS audio directly from script_short_<lang>.txt / script_<lang>.txt
    - Auto-detects 9:16 Full-Bleed vs 16:9 Large Showcase per scene
    - Renders 3.2s Hook Banner on Scene 1 + 3-5 word dynamic pop-in captions
    - Defaults to Seamless Loop (skip_outro=True) to maximize APV > 85%
    """
    shorts_out_dir = paths["shorts_out_dir"]
    os.makedirs(shorts_out_dir, exist_ok=True)
    # Purge any orphan _temp_* folders left by killed renders
    for entry in os.listdir(shorts_out_dir):
        if entry.startswith("_temp_"):
            shutil.rmtree(os.path.join(shorts_out_dir, entry), ignore_errors=True)
    bg_hex = "#0B132B" if lang == "en" else "#FAF7F2"

    all_lines = load_script(paths["script_path"])
    all_media = get_sorted_images(paths["media_dir"])

    # Auto-generate TTS if any referenced scene audio is missing (enables 1-command Shorts-First workflow!)
    needed_scenes = sorted({sc for cfg in configs for sc in cfg["scenes"]})
    missing_audio = [
        sc for sc in needed_scenes
        if not os.path.isfile(os.path.join(paths["audio_dir"], f"{sc:02d}_voice.mp3"))
        or os.path.getsize(os.path.join(paths["audio_dir"], f"{sc:02d}_voice.mp3")) == 0
    ]
    if force_tts or missing_audio:
        eff_voice = voice or ("gemini:Charon" if lang == "en" else DEFAULT_VOICE)
        print(f"-> Auto-generating TTS audio in '{os.path.basename(paths['audio_dir'])}' using {eff_voice}...")
        generate_audio(paths["script_path"], paths["audio_dir"], voice=eff_voice, force=force_tts)

    generated = []
    total_eps = len(configs)

    for ep_idx, cfg in enumerate(configs, 1):
        short_id = cfg["id"]
        scene_nums = cfg["scenes"]
        overlay_badge = format_overlay_badge(cfg, ep_idx, total_eps, lang)
        has_related = bool(cfg.get("has_related_video", paths.get("has_long_video", False)))
        print(f"\n=== BUILDING SHORT V3 [{lang.upper()}]: {short_id} ({overlay_badge}) | scenes={scene_nums} ===")

        temp_dir = os.path.join(shorts_out_dir, f"_temp_{short_id}")
        os.makedirs(temp_dir, exist_ok=True)
        try:
            selected_audio = []
            selected_media = []
            sfx_whoosh = os.path.join(RESOURCES_DIR, "sfx_whoosh.wav")
            sfx_pop = os.path.join(RESOURCES_DIR, "sfx_pop.wav")
            for order_idx, sc_num in enumerate(scene_nums, 1):
                audio_p = os.path.join(paths["audio_dir"], f"{sc_num:02d}_voice.mp3")
                if not os.path.isfile(audio_p):
                    raise FileNotFoundError(f"Missing audio file: {audio_p}")
                punchy_audio = os.path.join(temp_dir, f"punchy_{order_idx:02d}.mp3")
                sfx_use = sfx_whoosh if order_idx == 1 else sfx_pop
                _prepare_punchy_short_audio(audio_p, punchy_audio, speed=1.18, sfx_path=sfx_use)
                selected_audio.append({
                    "index": order_idx,
                    "scene_num": sc_num,
                    "text": all_lines[sc_num - 1],
                    "audio_path": punchy_audio,
                })
                selected_media.append(all_media[sc_num - 1])

            srt_out = os.path.join(temp_dir, f"{short_id}.srt")
            enriched = generate_subtitles(selected_audio, srt_out)

            txt_out = os.path.join(shorts_out_dir, f"{short_id}_script.txt")
            scene_word = "Scene" if lang == "en" else "Cảnh"
            with open(txt_out, "w", encoding="utf-8") as f_txt:
                f_txt.write(f"# {overlay_badge} - {cfg['title_line1']}: {cfg['title_line2']}\n")
                for item in enriched:
                    f_txt.write(f"{item['index']:02d} ({scene_word} {item['scene_num']:02d}). {item['text']}\n")

            # Render Scene 01 3.2s Hook Banner once per episode
            hook_banner_png = os.path.join(temp_dir, "hook_banner_01.png")
            ms.render_hook_banner_png(
                hook_banner_png,
                cfg["title_line1"],
                cfg.get("title_line2", ""),
                badge_text=overlay_badge,
                lang=lang,
                accent_hex=cfg["accent_color"],
            )

            overlay_fn = ms.create_short_overlay_en if lang == "en" else ms.create_short_overlay
            total_sc = len(enriched)
            tasks = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                for i, item in enumerate(enriched):
                    order_idx = i + 1
                    mw, mh = ms.probe_media_dimensions(selected_media[i])
                    is_portrait = (mh > mw)
                    overlay_png = os.path.join(temp_dir, f"overlay_{order_idx:02d}.png")
                    box_rect = overlay_fn(
                        overlay_png,
                        overlay_badge,
                        cfg["title_line1"],
                        cfg["title_line2"],
                        subtitle_text="",  # Dynamic 3-5 word strips handle captions in V3
                        step_label=format_step_label(ep_idx, total_eps, order_idx, total_sc, lang),
                        accent_hex=cfg["accent_color"],
                        is_portrait=is_portrait,
                        has_related_video=has_related,
                    )
                    fut = executor.submit(
                        ms._render_short_scene,
                        order_idx,
                        selected_media[i],
                        item["audio_path"],
                        item["duration"],
                        overlay_png,
                        box_rect,
                        DEFAULT_FPS,
                        temp_dir,
                        bg_hex,
                        item["text"],
                        lang,
                        cfg["accent_color"],
                        hook_banner_png if order_idx == 1 else None,
                        SHORT_HOOK_BANNER_SEC,
                    )
                    tasks.append((order_idx, item["scene_num"], item["duration"], fut))

                clip_files = [fut.result() for _, _, _, fut in tasks]

            # Seamless Loop is NOW DEFAULT (skip_outro=True unless --with-outro is explicitly passed)
            use_outro = True if force_outro else ((not skip_outro) and (not cfg.get("skip_outro", True)))
            if not use_outro:
                outro_dur = 0.0
            else:
                outro_mp4, outro_dur = render_short_outro_cta_clip(cfg, overlay_badge, lang, temp_dir, DEFAULT_FPS)
                clip_files.append(outro_mp4)

            concat_txt = os.path.join(temp_dir, "concat.txt")
            with open(concat_txt, "w", encoding="utf-8") as f_cat:
                for c in clip_files:
                    f_cat.write(f"file '{c.replace(chr(92), '/')}'\n")

            raw_concat_mp4 = os.path.join(temp_dir, f"{short_id}_raw.mp4")
            output_mp4 = os.path.join(shorts_out_dir, f"{short_id}.mp4")
            cmd = [FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", raw_concat_mp4]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg concat error: {res.stderr[-300:]}")

            total_dur = enriched[-1]["end"] + outro_dur
            shorts_bgm = os.path.join(RESOURCES_DIR, "bgm_shorts.mp3")
            if os.path.isfile(shorts_bgm):
                bgm_path = shorts_bgm
                bgm_vol = 0.13
            else:
                bgm_path = get_bgm_path(lang=lang)
                bgm_vol = DEFAULT_BGM_VOLUME

            if bgm_path and os.path.isfile(bgm_path):
                fade_start = max(0.0, total_dur - 1.0)
                af_mix = (
                    f"[1:a]volume={bgm_vol},afade=t=out:st={fade_start:.2f}:d=1.0[bgm];"
                    f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
                )
                cmd_bgm = [
                    FFMPEG_PATH, "-y",
                    "-i", raw_concat_mp4,
                    "-stream_loop", "-1", "-i", bgm_path,
                    "-filter_complex", af_mix,
                    "-map", "0:v:0",
                    "-map", "[aout]",
                    "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    output_mp4,
                ]
                res_bgm = subprocess.run(cmd_bgm, capture_output=True, text=True, encoding="utf-8", errors="ignore")
                if res_bgm.returncode != 0:
                    shutil.copyfile(raw_concat_mp4, output_mp4)
            else:
                shutil.copyfile(raw_concat_mp4, output_mp4)

            size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
            print(f"[DONE] {os.path.basename(output_mp4)} | {total_dur:.1f}s | {size_mb:.2f} MB")
            generated.append((output_mp4, total_dur, size_mb))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    return generated


def generate_metadata_and_thumbnails(proj_name, lang, paths, configs):
    """Render 9:16 thumbnails and export *_dang_bai.txt + TONG_HOP_DANG_SHORTS*.md."""
    shorts_out_dir = paths["shorts_out_dir"]
    os.makedirs(shorts_out_dir, exist_ok=True)
    all_media = get_sorted_images(paths["media_dir"])
    summary_name = "TONG_HOP_DANG_SHORTS_EN.md" if lang == "en" else "TONG_HOP_DANG_SHORTS.md"
    summary_md_path = os.path.join(shorts_out_dir, summary_name)
    thumb_fn = ms.render_short_thumbnail_en if lang == "en" else ms.render_short_thumbnail

    md_lines = [
        f"# BỘ TIÊU ĐỀ, MÔ TẢ & THUMBNAIL ĐĂNG YOUTUBE SHORTS [{lang.upper()}] ({proj_name})",
        "",
        f"Tất cả file video `.mp4`, ảnh thu nhỏ `*_thumb.jpg` và nội dung đăng bài nằm tại `projects/{proj_name}/shorts_{lang}/`.",
        "",
    ]

    temp_dir = os.path.join(shorts_out_dir, "_temp_thumbs")
    os.makedirs(temp_dir, exist_ok=True)
    try:
        for idx, cfg in enumerate(configs, 1):
            short_id = cfg["id"]
            hero_media = all_media[cfg["thumb_scene"] - 1]
            thumb_jpg = os.path.join(shorts_out_dir, f"{short_id}_thumb.jpg")
            thumb_fn(cfg, hero_media, thumb_jpg, temp_dir)
            print(f"[THUMB OK] {os.path.basename(thumb_jpg)}")

            meta_txt = os.path.join(shorts_out_dir, f"{short_id}_dang_bai.txt")
            with open(meta_txt, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write(f"{cfg['badge']} — {cfg['title_line1']}\n")
                f.write(f"File Video    : {short_id}.mp4\n")
                f.write(f"File Thumbnail: {short_id}_thumb.jpg\n")
                f.write("=" * 60 + "\n\n")
                f.write("1. TIÊU ĐỀ GỢI Ý (Chọn 1 trong 3):\n")
                for t_i, t_str in enumerate(cfg["yt_titles"], 1):
                    f.write(f"   Phương án {t_i}: {t_str}\n")
                f.write("\n2. MÔ TẢ VIDEO:\n" + "-" * 60 + "\n")
                f.write(cfg["yt_description"] + "\n" + "-" * 60 + "\n\n")
                f.write(f"3. BÌNH LUẬN GHIM:\n   {cfg['yt_pinned_comment']}\n\n")
                f.write("4. MÔ TẢ ẢNH THU NHỎ & PROMPT AI:\n")
                f.write(f"   - Bố cục: {cfg['thumb_desc']}\n")
                f.write(f"   - Prompt AI (9:16): {cfg['thumb_prompt']}\n")

            md_lines.extend([
                "---",
                f"## {idx}. {cfg['badge']} (`{short_id}.mp4`)",
                f"- **File Video**: `{short_id}.mp4`",
                f"- **File Thumbnail**: `{short_id}_thumb.jpg`",
                f"- **File Text Đăng Bài**: `{short_id}_dang_bai.txt`",
                "",
                "### Tiêu đề gợi ý:",
                *[f"{i}. `{t}`" for i, t in enumerate(cfg["yt_titles"], 1)],
                "",
                "### Mô tả Video:",
                "```text",
                cfg["yt_description"],
                "```",
                "",
                "### Bình luận ghim:",
                f"> {cfg['yt_pinned_comment']}",
                "",
                "### Prompt Thumbnail AI (9:16):",
                "```text",
                cfg["thumb_prompt"],
                "```",
                "",
            ])
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    with open(summary_md_path, "w", encoding="utf-8") as f_md:
        f_md.write("\n".join(md_lines))
    print(f"[METADATA OK] {summary_md_path}")


def main():
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Build 9:16 YouTube Shorts for any project from shorts_config_<lang>.json")
    parser.add_argument("project", help="Project folder name inside projects/")
    parser.add_argument("--lang", choices=["vi", "en"], default="vi")
    parser.add_argument("--media-dir", default=None, help="Optional override for media directory")
    parser.add_argument("--audio-dir", default=None, help="Optional override for audio directory")
    parser.add_argument("--meta-only", action="store_true", help="Only render thumbnails and metadata")
    parser.add_argument("--no-outro", action="store_true", default=True, help="Seamless loop without separate outro card (Default in V3)")
    parser.add_argument("--with-outro", action="store_true", help="Append ~1.8s separate outro CTA card (disables seamless loop)")
    parser.add_argument("--voice", default=None, help="Optional TTS voice when auto-synthesizing missing Short audio")
    parser.add_argument("--force-tts", action="store_true", help="Force re-synthesizing TTS audio")
    parser.add_argument("--dry-run", action="store_true", help="Validate paths and config without rendering")
    args = parser.parse_args()

    paths = resolve_project_paths(args.project, args.lang, args.media_dir, args.audio_dir)
    all_lines = load_script(paths["script_path"])
    all_media = get_sorted_images(paths["media_dir"])
    if len(all_lines) != len(all_media):
        raise ValueError(f"Script lines ({len(all_lines)}) != media count ({len(all_media)})")

    configs = load_and_validate_configs(paths["config_path"], len(all_lines), proj_name=args.project, lang=args.lang)
    mode_tag = "SHORTS-FIRST 9:16" if paths.get("is_short_first") else "16:9 -> 9:16 SHOWCASE"
    print(f"[VALIDATED] {args.project} ({args.lang} | {mode_tag}): {len(all_lines)} scenes, {len(configs)} short(s)")

    retention_warnings = audit_shorts_retention_risks(configs, all_lines, all_media)
    for w in retention_warnings:
        print(f"  ! {w}")

    if args.dry_run:
        for cfg in configs:
            sc0 = cfg["scenes"][0]
            m0 = os.path.basename(all_media[sc0 - 1])
            mw, mh = ms.probe_media_dimensions(all_media[sc0 - 1])
            aspect = "9:16 Full-Bleed" if mh > mw else "16:9 Showcase"
            print(f"  - {cfg['id']}: scenes={cfg['scenes']} (opener=#{sc0:02d} {m0} [{aspect}]), thumb={cfg['thumb_scene']}")
        return

    skip_outro_flag = not args.with_outro
    if not args.meta_only:
        build_shorts(
            args.project,
            args.lang,
            paths,
            configs,
            skip_outro=skip_outro_flag,
            force_outro=args.with_outro,
            voice=args.voice,
            force_tts=args.force_tts,
        )
    generate_metadata_and_thumbnails(args.project, args.lang, paths, configs)


if __name__ == "__main__":
    main()
