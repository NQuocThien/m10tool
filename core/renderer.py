import os
import re
import shutil
import subprocess
from .config import FFMPEG_PATH, DEFAULT_FPS, DEFAULT_MAX_ZOOM, DEFAULT_SUB_STYLE

def detect_target_resolution(sample_image_path):
    """
    Detects whether input is landscape (16:9) or portrait (9:16)
    and returns appropriate (width, height) and subtitle styling.
    """
    cmd = [FFMPEG_PATH, "-i", sample_image_path]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    
    w, h = 1920, 1080
    for line in res.stderr.splitlines():
        if "Stream #0:0" in line:
            match = re.search(r'(\d{3,5})x(\d{3,5})', line)
            if match:
                orig_w, orig_h = int(match.group(1)), int(match.group(2))
                if orig_h > orig_w:
                    # Portrait (9:16 - TikTok / Shorts)
                    return (1080, 1920), (
                        "FontName=Arial,FontSize=18,"
                        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
                        "BorderStyle=1,Outline=1.5,Shadow=0.5,"
                        "MarginV=60,Bold=0,Alignment=2"
                    )
                else:
                    # Landscape (16:9 - YouTube / Web)
                    return (1920, 1080), DEFAULT_SUB_STYLE
                    
    return (w, h), DEFAULT_SUB_STYLE

def render_project(image_paths, enriched_items, srt_path, output_mp4, temp_dir=None):
    """
    Renders video clips for each image + audio pair with subtle Ken Burns motion,
    concatenates all clips, burns subtitles, and outputs final MP4.
    """
    if len(image_paths) != len(enriched_items):
        raise ValueError(
            f"Count mismatch: {len(image_paths)} images vs {len(enriched_items)} audio/script lines. "
            f"Please ensure 1 image per script line."
        )

    if temp_dir is None:
        temp_dir = os.path.join(os.path.dirname(output_mp4), "temp_render")
    os.makedirs(temp_dir, exist_ok=True)

    fps = DEFAULT_FPS
    max_zoom = DEFAULT_MAX_ZOOM
    delta_zoom = max_zoom - 1.00

    # Auto-detect orientation (16:9 vs 9:16)
    (target_w, target_h), sub_style = detect_target_resolution(image_paths[0])
    orientation = "16:9 Landscape" if target_w >= target_h else "9:16 Portrait"
    print(f"-> Auto-detected resolution: {target_w}x{target_h} ({orientation})")

    clip_files = []
    print(f"-> Rendering {len(image_paths)} scenes with subtle Ken Burns motion...")

    for i in range(len(image_paths)):
        idx = i + 1
        img_path = image_paths[i]
        item = enriched_items[i]
        audio_path = item["audio_path"]
        dur = item["duration"]
        clip_path = os.path.join(temp_dir, f"clip_{idx:02d}.mp4")

        total_frames = int(dur * fps)
        step = delta_zoom / max(1, total_frames)

        # Alternating motion: odd clips zoom in, even clips zoom out
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
            "-loop", "1", "-t", f"{dur:.3f}", "-i", img_path,
            "-i", audio_path,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            clip_path
        ]

        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg error on scene {idx}: {res.stderr[-300:]}")

        clip_files.append(clip_path)
        print(f"  [{idx:02d}/{len(image_paths)}] Rendered {dur:.2f}s -> {os.path.basename(clip_path)}")

    # 2. Concat all clips
    concat_txt = os.path.join(temp_dir, "concat_list.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in clip_files:
            c_clean = c.replace("\\", "/")
            f.write(f"file '{c_clean}'\n")

    unsubbed_video = os.path.join(temp_dir, "merged_unsubbed.mp4")
    print("-> Concatenating all scenes...")
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

    # 3. Burn sleek subtitles
    print("-> Burning compact subtitles onto final video...")
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
    vf_sub = f"subtitles='{srt_escaped}':force_style='{sub_style}'"

    cmd_sub = [
        FFMPEG_PATH, "-y",
        "-i", unsubbed_video,
        "-vf", vf_sub,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-c:a", "copy",
        output_mp4
    ]
    res = subprocess.run(cmd_sub, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg subtitle burn error: {res.stderr[-300:]}")

    # 4. Clean up temporary render folder
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass

    size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"\n[OK] Final video ready: {output_mp4} ({size_mb:.2f} MB)")
    return output_mp4
