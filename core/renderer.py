import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import (
    FFMPEG_PATH, DEFAULT_FPS, DEFAULT_MAX_ZOOM, DEFAULT_SUB_STYLE,
    INTRO_EN_PATH, INTRO_VI_PATH, GLOBAL_INTRO_PATH,
    BGM_VI_PATH, BGM_EN_PATH, GLOBAL_BGM_PATH, DEFAULT_BGM_VOLUME
)

def get_bgm_path(lang="vi"):
    if lang == "vi" and os.path.exists(BGM_VI_PATH):
        return BGM_VI_PATH
    elif lang == "en" and os.path.exists(BGM_EN_PATH):
        return BGM_EN_PATH
    elif os.path.exists(GLOBAL_BGM_PATH):
        return GLOBAL_BGM_PATH
    return None
from .motion_25d import prepare_25d_layers

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
                        "FontName=Segoe UI,FontSize=18,"
                        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
                        "BorderStyle=1,Outline=1.6,Shadow=0.8,"
                        "MarginV=60,Bold=1,Alignment=2"
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

def _render_single_scene(idx, media_path, item, target_w, target_h, fps, max_zoom, temp_dir, video_exts, motion_25d=False, cache_25d_dir=None, precomputed_25d=None):
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
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "19",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest",
            clip_path
        ]
    else:
        total_frames = max(1, int(dur * fps))
        fg_path, bg_path = (None, None)
        if precomputed_25d is not None:
            fg_path, bg_path = precomputed_25d
        elif motion_25d and cache_25d_dir:
            try:
                fg_path, bg_path = prepare_25d_layers(media_path, target_w, target_h, cache_25d_dir)
            except Exception as e:
                print(f"  [WARN] 2.5D split failed on scene {idx}, using Ken Burns: {e}", flush=True)
                fg_path, bg_path = (None, None)

        if fg_path and bg_path:
            pan_dir = 1 if idx % 2 == 1 else -1
            bg_z = f"1.00+0.07*(on/{total_frames})"
            bg_x = f"(iw-iw/zoom)/2+{pan_dir}*(iw-iw/zoom)/2*(on/{total_frames})"
            bg_y = "(ih-ih/zoom)/2"

            fg_z = f"if(lt(on,6),1.06-0.04*(on/6),1.02+0.05*((on-6)/{max(1, total_frames - 6)}))"
            fg_x = "(iw-iw/zoom)/2"
            fg_y = "(ih-ih/zoom)/2+6*sin(2*PI*on/60)"

            filter_complex = (
                f"[0:v]zoompan=z='{bg_z}':x='{bg_x}':y='{bg_y}':d={total_frames}:s={target_w}x{target_h}:fps={fps}[bg];"
                f"[1:v]zoompan=z='{fg_z}':x='{fg_x}':y='{fg_y}':d={total_frames}:s={target_w}x{target_h}:fps={fps},format=rgba[fg];"
                f"[bg][fg]overlay=0:0:shortest=1,format=yuv420p[v]"
            )
            cmd = [
                FFMPEG_PATH, "-y",
                "-i", bg_path,
                "-i", fg_path,
                "-i", audio_path,
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-map", "2:a:0",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "19",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                "-shortest",
                clip_path
            ]
        else:
            effective_zoom = max(max_zoom, 1.035)
            delta_zoom = effective_zoom - 1.00
            step = delta_zoom / total_frames

            if idx % 2 == 1:
                zoom_expr = f"min(zoom+{step:.6f},{effective_zoom})"
            else:
                zoom_expr = f"max({effective_zoom}-on*{step:.6f},1.00)"

            vf = (
                f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},"
                f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={target_w}x{target_h}:fps={fps},"
                f"format=yuv420p"
            )

            cmd = [
                FFMPEG_PATH, "-y",
                "-i", media_path,
                "-i", audio_path,
                "-vf", vf,
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "19",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                "-shortest",
                clip_path
            ]

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg error on scene {idx}: {res.stderr[-300:]}")

    return clip_path

def render_project(image_paths, enriched_items, srt_path, output_mp4, temp_dir=None, use_intro=True, lang="vi", intro_path=None, motion_25d=False):
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
        print(f"-> Auto-detected resolution: {target_w}x{target_h} ({orientation})", flush=True)

        # 1. Check & prepare Intro if enabled
        intro_clip = None
        if intro_path is None:
            intro_path = get_intro_path(lang=lang)

        if use_intro and intro_path and os.path.exists(intro_path):
            print(f"🎬 Chuẩn hóa Intro video [{lang.upper()}]: {os.path.basename(intro_path)}...", flush=True)
            intro_clip = prepare_intro_clip(intro_path, target_w, target_h, fps, temp_dir)
            if intro_clip:
                print("  [OK] Đã chuẩn hóa Intro khớp độ phân giải và audio.", flush=True)

        # 2. Render scenes with multithreading
        video_exts = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
        has_videos = any(os.path.splitext(p)[1].lower() in video_exts for p in image_paths)
        cache_25d_dir = os.path.join(os.path.dirname(output_mp4), "cache_25d") if motion_25d else None

        # Pre-compute 2.5D layers sequentially before FFmpeg worker pool to prevent ONNX + FFmpeg CPU contention
        precomputed_25d_map = {}
        if motion_25d and cache_25d_dir:
            static_indices = [i for i, p in enumerate(image_paths) if os.path.splitext(p)[1].lower() not in video_exts]
            if static_indices:
                print(f"-> Chuẩn bị lớp 2.5D Parallax cho {len(static_indices)} ảnh tĩnh...", flush=True)
                for count_i, i in enumerate(static_indices, 1):
                    idx = i + 1
                    try:
                        fg_p, bg_p = prepare_25d_layers(image_paths[i], target_w, target_h, cache_25d_dir)
                        precomputed_25d_map[i] = (fg_p, bg_p)
                        mode_tag = "2.5D" if (fg_p and bg_p) else "Ken Burns"
                        print(f"  [2.5D {count_i:02d}/{len(static_indices):02d}] Cảnh {idx:02d}: {os.path.basename(image_paths[i])} ({mode_tag})", flush=True)
                    except Exception as e:
                        print(f"  [WARN] 2.5D split failed on scene {idx}, using Ken Burns: {e}", flush=True)
                        precomputed_25d_map[i] = (None, None)

        if motion_25d:
            mode_label = "video clips & 2.5D parallax images" if has_videos else "2.5D parallax (rembg + Ken Burns)"
        else:
            mode_label = "video clips & motion" if has_videos else "images with Ken Burns"
        print(f"-> Rendering {len(image_paths)} scenes using {mode_label}...", flush=True)

        workers = min(4, os.cpu_count() or 2)
        total_scenes = len(image_paths)
        future_to_idx = {}
        clip_map = {}
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for i in range(total_scenes):
                idx = i + 1
                future = executor.submit(
                    _render_single_scene,
                    idx, image_paths[i], enriched_items[i],
                    target_w, target_h, fps, max_zoom, temp_dir, video_exts,
                    motion_25d, cache_25d_dir, precomputed_25d_map.get(i)
                )
                future_to_idx[future] = idx

            done_count = 0
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                clip_path = future.result()
                clip_map[idx] = clip_path
                done_count += 1
                dur = enriched_items[idx - 1]["duration"]
                print(f"  [{done_count:02d}/{total_scenes:02d}] Rendered scene {idx:02d} ({dur:.2f}s) -> {os.path.basename(clip_path)}", flush=True)

            clip_files = [clip_map[idx] for idx in range(1, total_scenes + 1)]

        # 3. Concat content scenes first
        concat_txt = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for c in clip_files:
                c_clean = c.replace("\\", "/")
                f.write(f"file '{c_clean}'\n")

        unsubbed_video = os.path.join(temp_dir, "merged_unsubbed.mp4")
        print("-> Concatenating content scenes...", flush=True)
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

        # 4. Burn subtitles onto content scenes (and mix optional BGM if present)
        print("-> Burning compact subtitles onto content video...", flush=True)
        subbed_content = os.path.join(temp_dir, "content_with_sub.mp4")
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        vf_sub = f"subtitles='{srt_escaped}':force_style='{sub_style}'"

        bgm_path = get_bgm_path(lang=lang)
        if bgm_path:
            print(f"🎵 Mixing background music ({os.path.basename(bgm_path)}, vol={DEFAULT_BGM_VOLUME})...", flush=True)
            total_content_dur = enriched_items[-1]["end"] if enriched_items else 60.0
            fade_start = max(0.0, total_content_dur - 1.5)
            af_mix = (
                f"[1:a]volume={DEFAULT_BGM_VOLUME},afade=t=out:st={fade_start:.2f}:d=1.5[bgm];"
                f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
            cmd_sub = [
                FFMPEG_PATH, "-y",
                "-i", unsubbed_video,
                "-stream_loop", "-1", "-i", bgm_path,
                "-vf", vf_sub,
                "-filter_complex", af_mix,
                "-map", "0:v:0",
                "-map", "[aout]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                subbed_content
            ]
        else:
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
            print("🎬 Ghép Intro vào đầu video thành phẩm...", flush=True)
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
        print(f"\n[OK] Final video ready: {output_mp4} ({size_mb:.2f} MB)", flush=True)
        return output_mp4

    finally:
        # Guarantee cleanup even on error
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
