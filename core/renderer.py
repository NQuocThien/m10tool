import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from .config import (
    FFMPEG_PATH, DEFAULT_FPS, DEFAULT_MAX_ZOOM, DEFAULT_SUB_STYLE,
    INTRO_EN_PATH, INTRO_VI_PATH, GLOBAL_INTRO_PATH
)

def get_intro_path(lang="vi"):
    if lang == "vi" and os.path.exists(INTRO_VI_PATH):
        return INTRO_VI_PATH
    elif lang == "en" and os.path.exists(INTRO_EN_PATH):
        return INTRO_EN_PATH
    elif os.path.exists(INTRO_EN_PATH):
        return INTRO_EN_PATH
    elif os.path.exists(GLOBAL_INTRO_PATH):
        return GLOBAL_INTRO_PATH
    elif os.path.exists(INTRO_VI_PATH):
        return INTRO_VI_PATH
    return None

def detect_target_resolution(sample_image_path):
    cmd = [FFMPEG_PATH, "-i", sample_image_path]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    
    w, h = 1920, 1080
    for line in res.stderr.splitlines():
        if "Stream #0:0" in line:
            match = re.search(r'(\d{3,5})x(\d{3,5})', line)
            if match:
                orig_w, orig_h = int(match.group(1)), int(match.group(2))
                if orig_h > orig_w:
                    return (1080, 1920), (
                        "FontName=Arial,FontSize=18,"
                        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
                        "BorderStyle=1,Outline=1.5,Shadow=0.5,"
                        "MarginV=60,Bold=0,Alignment=2"
                    )
                else:
                    return (1920, 1080), DEFAULT_SUB_STYLE
                    
    return (w, h), DEFAULT_SUB_STYLE

def prepare_intro_clip(intro_src, target_w, target_h, fps, temp_dir):
    """Normalizes intro video to match exact resolution, fps, and audio standard (48kHz stereo) for seamless concat."""
    norm_intro = os.path.join(temp_dir, "intro_normalized.mp4")
    cmd = [
        FFMPEG_PATH, "-y",
        "-i", intro_src,
        "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},fps={fps},format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        norm_intro
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode == 0:
        return norm_intro
    return None

def _render_single_scene(idx, media_path, item, target_w, target_h, fps, max_zoom, temp_dir, video_exts):
    audio_path = item["audio_path"]
    dur = item["duration"]
    clip_path = os.path.join(temp_dir, f"clip_{idx:02d}.mp4")
    is_vid = os.path.splitext(media_path)[1].lower() in video_exts

    if is_vid:
        vf = (
            f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},"
            f"fps={fps},format=yuv420p"
        )
        cmd = [
            FFMPEG_PATH, "-y",
            "-stream_loop", "-1",
            "-t", f"{dur:.3f}",
            "-i", media_path,
            "-i", audio_path,
            "-vf", vf,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest",
            clip_path
        ]
    else:
        total_frames = int(dur * fps)
        delta_zoom = max_zoom - 1.00
        step = delta_zoom / max(1, total_frames)

        if idx % 2 == 1:
            zoom_expr = f"min(zoom+{step:.6f},{max_zoom})"
        else:
            zoom_expr = f"max({max_zoom}-on*{step:.6f},1.00)"

        vf = (
            f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},"
            f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={target_w}x{target_h}:fps={fps},"
            f"format=yuv420p"
        )

        cmd = [
            FFMPEG_PATH, "-y",
            "-loop", "1", "-t", f"{dur:.3f}", "-i", media_path,
            "-i", audio_path,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest",
            clip_path
        ]

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg error on scene {idx}: {res.stderr[-300:]}")

    return clip_path

def render_project(image_paths, enriched_items, srt_path, output_mp4, temp_dir=None, use_intro=True, lang="vi", intro_path=None):
    if len(image_paths) != len(enriched_items):
        raise ValueError(
            f"Count mismatch: {len(image_paths)} media files vs {len(enriched_items)} audio/script lines. "
            f"Please ensure 1 media item per script line."
        )

    if temp_dir is None:
        temp_dir = os.path.join(os.path.dirname(output_mp4), "temp_render")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        fps = DEFAULT_FPS
        max_zoom = DEFAULT_MAX_ZOOM

        (target_w, target_h), sub_style = detect_target_resolution(image_paths[0])
        orientation = "16:9 Landscape" if target_w >= target_h else "9:16 Portrait"
        print(f"-> Auto-detected resolution: {target_w}x{target_h} ({orientation})")

        # 1. Check & prepare Intro if enabled
        intro_clip = None
        if intro_path is None:
            intro_path = get_intro_path(lang=lang)

        if use_intro and intro_path and os.path.exists(intro_path):
            print(f"🎬 Chuẩn hóa Intro video [{lang.upper()}]: {os.path.basename(intro_path)}...")
            intro_clip = prepare_intro_clip(intro_path, target_w, target_h, fps, temp_dir)
            if intro_clip:
                print("  [OK] Đã chuẩn hóa Intro khớp độ phân giải và audio.")

        # 2. Render scenes with multithreading
        video_exts = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
        has_videos = any(os.path.splitext(p)[1].lower() in video_exts for p in image_paths)
        mode_label = "video clips & motion" if has_videos else "images with subtle Ken Burns"
        print(f"-> Rendering {len(image_paths)} scenes using {mode_label}...")

        workers = min(4, os.cpu_count() or 2)
        tasks = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for i in range(len(image_paths)):
                idx = i + 1
                future = executor.submit(
                    _render_single_scene,
                    idx, image_paths[i], enriched_items[i],
                    target_w, target_h, fps, max_zoom, temp_dir, video_exts
                )
                tasks.append((idx, future))

            clip_files = []
            for idx, future in tasks:
                clip_path = future.result()
                clip_files.append(clip_path)
                dur = enriched_items[idx - 1]["duration"]
                print(f"  [{idx:02d}/{len(image_paths)}] Rendered {dur:.2f}s -> {os.path.basename(clip_path)}")

        # 3. Concat content scenes first
        concat_txt = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for c in clip_files:
                c_clean = c.replace("\\", "/")
                f.write(f"file '{c_clean}'\n")

        unsubbed_video = os.path.join(temp_dir, "merged_unsubbed.mp4")
        print("-> Concatenating content scenes...")
        cmd_concat = [
            FFMPEG_PATH, "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_txt,
            "-c", "copy",
            unsubbed_video
        ]
        res = subprocess.run(cmd_concat, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg concat error: {res.stderr[-300:]}")

        # 4. Burn subtitles onto content scenes
        print("-> Burning compact subtitles onto content video...")
        subbed_content = os.path.join(temp_dir, "content_with_sub.mp4")
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        vf_sub = f"subtitles='{srt_escaped}':force_style='{sub_style}'"

        cmd_sub = [
            FFMPEG_PATH, "-y",
            "-i", unsubbed_video,
            "-vf", vf_sub,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-c:a", "copy",
            subbed_content
        ]
        res = subprocess.run(cmd_sub, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg subtitle burn error: {res.stderr[-300:]}")

        # 5. Prepend Intro if available
        if intro_clip:
            print("🎬 Ghép Intro vào đầu video thành phẩm...")
            final_concat_txt = os.path.join(temp_dir, "final_concat.txt")
            with open(final_concat_txt, "w", encoding="utf-8") as f:
                f.write(f"file '{intro_clip.replace(chr(92), '/')}'\n")
                f.write(f"file '{subbed_content.replace(chr(92), '/')}'\n")

            cmd_final = [
                FFMPEG_PATH, "-y",
                "-f", "concat", "-safe", "0",
                "-i", final_concat_txt,
                "-c", "copy",
                output_mp4
            ]
            res = subprocess.run(cmd_final, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            if res.returncode != 0:
                shutil.copyfile(subbed_content, output_mp4)
        else:
            shutil.copyfile(subbed_content, output_mp4)

        size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
        print(f"\n[OK] Final video ready: {output_mp4} ({size_mb:.2f} MB)")
        return output_mp4

    finally:
        # Guarantee cleanup even on error
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
