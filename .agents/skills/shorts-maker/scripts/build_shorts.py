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

from core.config import DEFAULT_FPS, FFMPEG_PATH, PROJECTS_DIR
from core.sorter import get_sorted_images
from core.subtitles import generate_subtitles
from core.tts import load_script
import make_shorts as ms

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
    """Resolve script, media, audio, config, and output paths for any project."""
    proj_dir = os.path.join(PROJECTS_DIR, proj_name)
    if not os.path.isdir(proj_dir):
        raise FileNotFoundError(f"Project not found: {proj_dir}")

    script_path = os.path.join(proj_dir, f"script_{lang}.txt")
    if not os.path.isfile(script_path):
        fallback_script = os.path.join(proj_dir, "script.txt")
        if os.path.isfile(fallback_script):
            script_path = fallback_script
        else:
            raise FileNotFoundError(f"Script not found: {script_path}")

    if media_dir_override:
        media_dir = media_dir_override if os.path.isabs(media_dir_override) else os.path.join(proj_dir, media_dir_override)
    else:
        candidates = (
            [f"video_{lang}", f"imgs_{lang}", "imgs-clean", "imgs"]
            if lang == "en"
            else [f"video_{lang}", f"imgs_{lang}", "imgs"]
        )
        media_dir = next(
            (os.path.join(proj_dir, c) for c in candidates if os.path.isdir(os.path.join(proj_dir, c))),
            None,
        )
    if not media_dir or not os.path.isdir(media_dir):
        raise FileNotFoundError(f"Media directory not found in {proj_dir}")

    if audio_dir_override:
        audio_dir = audio_dir_override if os.path.isabs(audio_dir_override) else os.path.join(proj_dir, audio_dir_override)
    else:
        audio_candidates = [f"audio_{lang}", "audio"]
        audio_dir = next(
            (os.path.join(proj_dir, c) for c in audio_candidates if os.path.isdir(os.path.join(proj_dir, c))),
            None,
        )
    if not audio_dir or not os.path.isdir(audio_dir):
        raise FileNotFoundError(f"Audio directory not found in {proj_dir}")

    config_path = os.path.join(proj_dir, f"shorts_config_{lang}.json")
    shorts_out_dir = os.path.join(proj_dir, f"shorts_{lang}")
    return {
        "proj_dir": proj_dir,
        "script_path": script_path,
        "media_dir": media_dir,
        "audio_dir": audio_dir,
        "config_path": config_path,
        "shorts_out_dir": shorts_out_dir,
    }


def load_and_validate_configs(config_path, total_scenes):
    """Load shorts_config_<lang>.json and validate required fields and scene bounds."""
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Shorts config not found: {config_path}")

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


def format_overlay_badge(cfg, ep_idx, total_eps, lang="vi"):
    """Format badge text so viewer immediately sees Main Topic + Episode progress."""
    raw_badge = cfg["badge"].strip()
    main_topic = cfg.get("main_topic", "").strip()
    if main_topic and main_topic.upper() not in raw_badge.upper():
        return f"{main_topic.upper()} • {raw_badge}"
    return raw_badge


def format_step_label(ep_idx, total_eps, scene_order_idx, total_scenes_in_ep, lang="vi"):
    """Format subtitle card header right label with Episode + Scene progress."""
    if lang == "en":
        return f"Part {ep_idx}/{total_eps} • Scene {scene_order_idx}/{total_scenes_in_ep}"
    return f"Tập {ep_idx}/{total_eps} • Cảnh {scene_order_idx}/{total_scenes_in_ep}"


def build_shorts(proj_name, lang, paths, configs):
    """Render vertical 9:16 Short videos for all configured episodes."""
    shorts_out_dir = paths["shorts_out_dir"]
    os.makedirs(shorts_out_dir, exist_ok=True)
    bg_hex = "#0B132B" if lang == "en" else "#FAF7F2"

    all_lines = load_script(paths["script_path"])
    all_media = get_sorted_images(paths["media_dir"])
    generated = []
    total_eps = len(configs)

    for ep_idx, cfg in enumerate(configs, 1):
        short_id = cfg["id"]
        scene_nums = cfg["scenes"]
        overlay_badge = format_overlay_badge(cfg, ep_idx, total_eps, lang)
        print(f"\n=== BUILDING SHORT [{lang.upper()}]: {short_id} ({overlay_badge}) | scenes={scene_nums} ===")

        temp_dir = os.path.join(shorts_out_dir, f"_temp_{short_id}")
        os.makedirs(temp_dir, exist_ok=True)
        try:
            selected_audio = []
            selected_media = []
            for order_idx, sc_num in enumerate(scene_nums, 1):
                audio_p = os.path.join(paths["audio_dir"], f"{sc_num:02d}_voice.mp3")
                if not os.path.isfile(audio_p):
                    raise FileNotFoundError(f"Missing audio file: {audio_p}")
                selected_audio.append({
                    "index": order_idx,
                    "scene_num": sc_num,
                    "text": all_lines[sc_num - 1],
                    "audio_path": audio_p,
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

            overlay_fn = ms.create_short_overlay_en if lang == "en" else ms.create_short_overlay
            total_sc = len(enriched)
            tasks = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                for i, item in enumerate(enriched):
                    order_idx = i + 1
                    overlay_png = os.path.join(temp_dir, f"overlay_{order_idx:02d}.png")
                    box_rect = overlay_fn(
                        overlay_png,
                        overlay_badge,
                        cfg["title_line1"],
                        cfg["title_line2"],
                        subtitle_text=item["text"],
                        step_label=format_step_label(ep_idx, total_eps, order_idx, total_sc, lang),
                        accent_hex=cfg["accent_color"],
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
                    )
                    tasks.append((order_idx, item["scene_num"], item["duration"], fut))

                clip_files = [fut.result() for _, _, _, fut in tasks]

            concat_txt = os.path.join(temp_dir, "concat.txt")
            with open(concat_txt, "w", encoding="utf-8") as f_cat:
                for c in clip_files:
                    f_cat.write(f"file '{c.replace(chr(92), '/')}'\n")

            output_mp4 = os.path.join(shorts_out_dir, f"{short_id}.mp4")
            cmd = [FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", output_mp4]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg concat error: {res.stderr[-300:]}")

            total_dur = enriched[-1]["end"]
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
    parser.add_argument("--dry-run", action="store_true", help="Validate paths and config without rendering")
    args = parser.parse_args()

    paths = resolve_project_paths(args.project, args.lang, args.media_dir, args.audio_dir)
    all_lines = load_script(paths["script_path"])
    all_media = get_sorted_images(paths["media_dir"])
    if len(all_lines) != len(all_media):
        raise ValueError(f"Script lines ({len(all_lines)}) != media count ({len(all_media)})")

    configs = load_and_validate_configs(paths["config_path"], len(all_lines))
    print(f"[VALIDATED] {args.project} ({args.lang}): {len(all_lines)} scenes, {len(configs)} shorts")

    if args.dry_run:
        for cfg in configs:
            print(f"  - {cfg['id']}: scenes={cfg['scenes']}, thumb={cfg['thumb_scene']}")
        return

    if not args.meta_only:
        build_shorts(args.project, args.lang, paths, configs)
    generate_metadata_and_thumbnails(args.project, args.lang, paths, configs)


if __name__ == "__main__":
    main()
