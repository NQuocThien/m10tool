"""Shorts 9:16 graphics & per-scene renderer used by the V3 pipeline (.agents/skills/shorts-maker/scripts/build_shorts.py)."""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

from core.config import (
    FFMPEG_PATH,
    RESOURCES_DIR,
    HIGHLIGHT_UNITS,
    HIGHLIGHT_KEYWORDS,
    SHORT_HOOK_BANNER_SEC,
    SHORT_WORDS_PER_CAPTION,
)
from core.subtitles import compute_caption_cue_timings

import re


_HIGHLIGHT_UNITS = HIGHLIGHT_UNITS
_HIGHLIGHT_KEYWORDS = HIGHLIGHT_KEYWORDS


def probe_media_dimensions(media_path):
    """Fast aspect-ratio detector for images and videos; returns (width, height)."""
    ext = os.path.splitext(media_path)[1].lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
        try:
            with Image.open(media_path) as im:
                return im.size
        except Exception:
            return (1920, 1080)

    cmd = [FFMPEG_PATH, "-i", media_path]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    for line in res.stderr.splitlines():
        if "Video:" in line or "Stream #0:" in line:
            m = re.search(r"(\d{3,5})x(\d{3,5})", line)
            if m:
                return (int(m.group(1)), int(m.group(2)))
    return (1920, 1080)


def _load_font(size, bold=True):
    font_candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def _wrap_text_lines(draw, text, font, max_width):
    words = text.split()
    lines = []
    cur = []
    for w in words:
        test_line = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) <= max_width or not cur:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def _blend_rgba(base_rgba, tint_rgba, alpha_ratio):
    r = int(base_rgba[0] * (1 - alpha_ratio) + tint_rgba[0] * alpha_ratio)
    g = int(base_rgba[1] * (1 - alpha_ratio) + tint_rgba[1] * alpha_ratio)
    b = int(base_rgba[2] * (1 - alpha_ratio) + tint_rgba[2] * alpha_ratio)
    return (r, g, b, 255)


def _parse_step_progress(step_label):
    """Extract (current_scene, total_scenes) from step_label like 'Tập 1/4 • Cảnh 3/6'."""
    if not step_label:
        return (0, 0)
    matches = re.findall(r"(\d+)\s*/\s*(\d+)", step_label)
    if not matches:
        return (0, 0)
    cur_s, tot_s = matches[-1]
    return (int(cur_s), int(tot_s))


def _classify_highlight_words(words):
    """Return boolean list marking numeric tokens, units, and key tech terms for visual pop."""
    flags = [False] * len(words)
    for i, raw_w in enumerate(words):
        clean_w = raw_w.strip(".,!?:;\"'()[]{}—–-")
        lower_w = clean_w.lower()
        if not clean_w:
            continue
        if any(ch.isdigit() for ch in clean_w) or lower_w in _HIGHLIGHT_KEYWORDS:
            flags[i] = True
        elif lower_w in _HIGHLIGHT_UNITS and i > 0 and flags[i - 1]:
            flags[i] = True
    return flags


def _draw_highlighted_subtitle_line(
    draw,
    line_str,
    lx,
    ly,
    font,
    normal_fill,
    highlight_fill,
    pill_fill=None,
):
    """Draw a subtitle line while highlighting numeric tokens and key tech keywords."""
    words = line_str.split()
    if not words:
        return
    flags = _classify_highlight_words(words)
    if not any(flags):
        draw.text((lx, ly), line_str, font=font, fill=normal_fill)
        return

    # Group consecutive highlighted tokens into a single unified pill (e.g. '150 nghìn', '3 lõi')
    spans = []
    idx = 0
    while idx < len(words):
        flag = flags[idx]
        j = idx + 1
        while j < len(words) and flags[j] == flag:
            j += 1
        spans.append((idx, j, flag))
        idx = j

    for s_i, e_i, is_hi in spans:
        prefix = " ".join(words[:s_i]) + (" " if s_i > 0 else "")
        span_str = " ".join(words[s_i:e_i])
        px = lx + (draw.textbbox((0, 0), prefix, font=font)[2] if prefix else 0)
        wb = draw.textbbox((px, ly), span_str, font=font)
        if is_hi:
            if pill_fill:
                draw.rounded_rectangle(
                    (wb[0] - 8, wb[1] - 4, wb[2] + 8, wb[3] + 4),
                    radius=12,
                    fill=pill_fill,
                )
            draw.text((px, ly), span_str, font=font, fill=highlight_fill)
        else:
            draw.text((px, ly), span_str, font=font, fill=normal_fill)


def render_hook_banner_png(
    output_png,
    title_line1,
    title_line2="",
    badge_text="",
    accent_hex="#D35400",
):
    """
    Renders a 1080x300 RGBA scroll-stopping Hook Banner displayed ONLY during the first ~3.2s
    of Scene 01, then hidden so full visual storytelling takes over without PowerPoint clutter.
    """
    BW, BH = 1080, 236
    img = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    accent_clean = accent_hex.lstrip("#")
    accent_rgb = tuple(int(accent_clean[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    is_yellow = accent_clean.upper() in {"F4C430", "FFB300"}

    card_bg = (28, 25, 23, 240)
    border_col = (244, 196, 48, 255)
    t1_col = accent_rgb if is_yellow else (244, 196, 48, 255)
    t2_col = (248, 250, 252, 255)

    cx1, cy1, cx2, cy2 = 36, 8, BW - 36, BH - 12
    draw.rounded_rectangle((cx1 + 4, cy1 + 6, cx2 + 4, cy2 + 6), radius=26, fill=(0, 0, 0, 110))
    draw.rounded_rectangle((cx1, cy1, cx2, cy2), radius=26, fill=card_bg, outline=border_col, width=4)

    y_cursor = cy1 + 18
    clean_badge = re.sub(r"(?i)\b(tập|tap|episode|ep|part)\s*\d+\s*(/\s*\d+)?\s*[•\-:|]*\s*", "", badge_text or "").strip(" •-:|")
    if clean_badge:
        f_b = _load_font(20, bold=True)
        bb = draw.textbbox((0, 0), clean_badge.upper(), font=f_b)
        pw = min(cx2 - cx1 - 60, (bb[2] - bb[0]) + 36)
        px = (BW - pw) // 2
        draw.rounded_rectangle((px, y_cursor, px + pw, y_cursor + 34), radius=17, fill=accent_rgb)
        bfg = (20, 18, 16, 255) if is_yellow else (255, 255, 255, 255)
        draw.text((BW // 2, y_cursor + 17), clean_badge.upper()[:46], font=f_b, fill=bfg, anchor="mm")
        y_cursor += 44
    else:
        y_cursor += 12

    f_t1 = _load_font(45, bold=True)
    while f_t1.size > 32 and draw.textbbox((0, 0), title_line1, font=f_t1)[2] > (cx2 - cx1 - 44):
        f_t1 = _load_font(f_t1.size - 4, bold=True)
    draw.text((BW // 2, y_cursor + 24), title_line1, font=f_t1, fill=t1_col, anchor="mm")
    y_cursor += 58

    if title_line2:
        f_t2 = _load_font(31, bold=True)
        while f_t2.size > 23 and draw.textbbox((0, 0), title_line2, font=f_t2)[2] > (cx2 - cx1 - 48):
            f_t2 = _load_font(f_t2.size - 3, bold=True)
        draw.text((BW // 2, y_cursor + 18), title_line2, font=f_t2, fill=t2_col, anchor="mm")

    img.save(output_png, "PNG")
    return output_png


def render_caption_strip_png(
    output_png,
    cue_text,
    accent_hex="#D35400",
):
    """
    Renders a compact 1080x270 RGBA dynamic pop-in caption pill (3-5 words per beat).
    Positioned in the safe zone (y=1205..1475), above YouTube Shorts bottom metadata UI.
    """
    CW, CH = 1080, 270
    img = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    if not cue_text or not cue_text.strip():
        img.save(output_png, "PNG")
        return output_png

    draw = ImageDraw.Draw(img)
    font_cap = _load_font(52, bold=True)
    max_w = CW - 140
    lines = _wrap_text_lines(draw, cue_text.strip(), font_cap, max_w)
    if len(lines) > 2:
        font_cap = _load_font(44, bold=True)
        lines = _wrap_text_lines(draw, cue_text.strip(), font_cap, max_w)

    line_h = 68 if font_cap.size >= 50 else 58
    line_widths = [draw.textbbox((0, 0), ln, font=font_cap)[2] for ln in lines]
    box_w = min(CW - 64, max(line_widths) + 76)
    box_h = len(lines) * line_h + 42
    bx1 = (CW - box_w) // 2
    by1 = (CH - box_h) // 2
    bx2 = bx1 + box_w
    by2 = by1 + box_h

    pill_bg = (24, 21, 19, 232)
    pill_border = (244, 196, 48, 235)
    normal_fg = (255, 255, 255, 255)
    hi_fg = (24, 21, 19, 255)
    hi_pill = (244, 196, 48, 255)

    draw.rounded_rectangle((bx1 + 4, by1 + 6, bx2 + 4, by2 + 6), radius=28, fill=(0, 0, 0, 115))
    draw.rounded_rectangle((bx1, by1, bx2, by2), radius=28, fill=pill_bg, outline=pill_border, width=3)

    start_y = by1 + 21
    for idx_l, ln in enumerate(lines):
        lw = draw.textbbox((0, 0), ln, font=font_cap)[2]
        lx = (CW - lw) // 2
        ly = start_y + idx_l * line_h
        _draw_highlighted_subtitle_line(
            draw,
            ln,
            lx,
            ly,
            font_cap,
            normal_fill=normal_fg,
            highlight_fill=hi_fg,
            pill_fill=hi_pill,
        )

    img.save(output_png, "PNG")
    return output_png


def _build_short_chrome_overlay(
    output_png,
    step_label="",
    accent_hex="#D35400",
    is_portrait=True,
    has_related_video=False,
    static_subtitle_fallback="",
):
    """
    V3 Minimal Chrome Overlay (1080x1920 RGBA):
    - Mode A (is_portrait=True, 9:16 native): 100% Full-Bleed (0, 0, 1080, 1920)
    - Mode B (is_portrait=False, 16:9 source): Large 1048x740 center showcase (16, 370, 1048, 740)
    """
    W, H = 1080, 1920
    accent_clean = accent_hex.lstrip("#")
    accent_rgb = tuple(int(accent_clean[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if is_portrait:
        for y in range(180):
            a = int(88 * ((1.0 - y / 180.0) ** 1.5))
            draw.line([(0, y), (W, y)], fill=(12, 12, 14, a))
        vx, vy, vw, vh = 0, 0, W, H
    else:
        vx, vy, vw, vh = 16, 398, 1048, 740
        border_col = (28, 25, 23, 255)
        draw.rounded_rectangle(
            (vx - 3, vy - 3, vx + vw + 3, vy + vh + 3),
            radius=28,
            fill=(0, 0, 0, 0),
            outline=border_col,
            width=6,
        )

    # 1. Slim Top Progress Bar (y = 54..64)
    cur_sc, tot_sc = _parse_step_progress(step_label)
    if tot_sc > 0:
        prog_ratio = max(0.08, min(1.0, cur_sc / tot_sc))
        pb_x1, pb_y1, pb_x2, pb_y2 = 42, 54, W - 42, 64
        draw.rounded_rectangle((pb_x1, pb_y1, pb_x2, pb_y2), radius=5, fill=(255, 255, 255, 95))
        fill_w = int((pb_x2 - pb_x1) * prog_ratio)
        draw.rounded_rectangle((pb_x1, pb_y1, pb_x1 + fill_w, pb_y2), radius=5, fill=accent_rgb)

    # 2. Compact Brand Watermark Pill (y = 80..134)
    pill_w, pill_h = 450, 54
    pill_x = (W - pill_w) // 2
    pill_y = 80
    pill_bg = (255, 253, 249, 222)
    pill_outline = (28, 25, 23, 210)
    brand_fg = (28, 25, 23, 255)

    draw.rounded_rectangle(
        (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
        radius=27,
        fill=pill_bg,
        outline=pill_outline,
        width=2,
    )
    logo_path = os.path.join(RESOURCES_DIR, "logo_vi.jpg")
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA").resize((38, 38), Image.LANCZOS)
            mask = Image.new("L", (38, 38), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 38, 38), fill=255)
            img.paste(logo, (pill_x + 12, pill_y + 8), mask)
        except Exception:
            pass
    f_brand = _load_font(22, bold=True)
    draw.text((pill_x + 62, pill_y + 14), "VẮT CHANH CÔNG NGHỆ", font=f_brand, fill=brand_fg)

    if static_subtitle_fallback:
        tmp_cap = output_png + "._cap_preview.png"
        try:
            render_caption_strip_png(tmp_cap, static_subtitle_fallback, accent_hex=accent_hex)
            if os.path.exists(tmp_cap):
                cap_im = Image.open(tmp_cap).convert("RGBA")
                img.alpha_composite(cap_im, (0, 1205))
        finally:
            if os.path.exists(tmp_cap):
                try:
                    os.remove(tmp_cap)
                except Exception:
                    pass

    if has_related_video and tot_sc > 0 and cur_sc == tot_sc:
        cta_w, cta_h = 780, 54
        cta_x, cta_y = (W - cta_w) // 2, 1490
        cta_fill = (211, 84, 0, 240)
        cta_fg = (255, 255, 255, 255)
        draw.rounded_rectangle((cta_x, cta_y, cta_x + cta_w, cta_y + cta_h), radius=27, fill=cta_fill, outline=(255, 255, 255, 220), width=2)
        f_cta = _load_font(24, bold=True)
        cta_txt = "▶ BẤM VIDEO LIÊN QUAN GÓC DƯỚI XEM BẢN ĐẦY ĐỦ"
        draw.text((W // 2, cta_y + cta_h // 2), cta_txt, font=f_cta, fill=cta_fg, anchor="mm")

    img.save(output_png, "PNG")
    return (vx, vy, vw, vh)


def create_short_overlay(
    output_png,
    badge_text,
    title_line1,
    title_line2,
    subtitle_text="",
    step_label="",
    accent_hex="#D35400",
    is_portrait=True,
    has_related_video=False,
):
    """V3 VI Short Chrome Overlay: Full-bleed (0,0,1080,1920) for 9:16 or large showcase (16,370,1048,740) for 16:9."""
    preview_chunk = subtitle_text.split(".")[0][:42] if subtitle_text else ""
    return _build_short_chrome_overlay(
        output_png,
        step_label=step_label,
        accent_hex=accent_hex,
        is_portrait=is_portrait,
        has_related_video=has_related_video,
        static_subtitle_fallback=preview_chunk,
    )


def _render_short_scene(
    order_idx,
    media_path,
    audio_path,
    dur,
    overlay_png,
    box_rect,
    fps,
    temp_dir,
    bg_hex="#FAF7F2",
    subtitle_text="",
    accent_hex="#D35400",
    hook_banner_png=None,
    hook_duration=SHORT_HOOK_BANNER_SEC,
):
    vx, vy, vw, vh = box_rect
    is_full_bleed = (vw == 1080 and vh == 1920)
    clip_path = os.path.join(temp_dir, f"short_clip_{order_idx:02d}.mp4")
    ext = os.path.splitext(media_path)[1].lower()
    is_vid = ext in {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}

    cues = compute_caption_cue_timings(subtitle_text, dur, max_words=SHORT_WORDS_PER_CAPTION) if subtitle_text else []
    cue_pngs = []
    for c_idx, cue in enumerate(cues):
        if not cue["text"].strip():
            continue
        c_png = os.path.join(temp_dir, f"sc{order_idx:02d}_cap_{c_idx:02d}.png")
        render_caption_strip_png(c_png, cue["text"], accent_hex=accent_hex)
        cue_pngs.append((c_png, cue["start"], cue["end"]))

    filter_parts = []
    if is_vid:
        if is_full_bleed:
            filter_parts.append(
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={fps}[basev]"
            )
        else:
            tint_alpha = "0.76"
            filter_parts.append(
                f"[0:v]fps={fps},split=2[vsrc1][vsrc2];"
                f"[vsrc1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:4[blur];"
                f"color=c={bg_hex}@{tint_alpha}:s=1080x1920:r={fps}[tint];"
                f"[blur][tint]overlay=0:0:shortest=1[amb];"
                f"[vsrc2]scale={vw}:{vh}:force_original_aspect_ratio=increase,crop={vw}:{vh}[fg];"
                f"[amb][fg]overlay={vx}:{vy}:shortest=1[basev]"
            )
    else:
        total_frames = max(1, int(dur * fps))
        max_zoom = 1.14
        step = (max_zoom - 1.00) / max(1, total_frames)
        if order_idx % 2 == 1:
            zoom_expr = f"min(zoom+{step:.6f},{max_zoom})"
        else:
            zoom_expr = f"max({max_zoom}-on*{step:.6f},1.00)"
        pan_sign = "+" if (order_idx % 4 in (1, 2)) else "-"
        x_expr = f"iw/2-(iw/zoom/2){pan_sign}(iw-iw/zoom)*0.20*(on/{max(1, total_frames)})"

        if is_full_bleed:
            filter_parts.append(
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"zoompan=z='{zoom_expr}':x='{x_expr}':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1080x1920:fps={fps}[basev]"
            )
        else:
            tint_alpha = "0.76"
            filter_parts.append(
                f"[0:v]split=2[isrc1][isrc2];"
                f"[isrc1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:4[blur];"
                f"color=c=#000000:s=1080x1920:r={fps}:d={dur:.3f}[bg0];"
                f"[bg0][blur]overlay=0:0:eof_action=repeat[bg1];"
                f"color=c={bg_hex}@{tint_alpha}:s=1080x1920:r=1[tint];"
                f"[bg1][tint]overlay=0:0:eof_action=repeat[amb];"
                f"[isrc2]scale={vw}:{vh}:force_original_aspect_ratio=increase,crop={vw}:{vh},"
                f"zoompan=z='{zoom_expr}':x='{x_expr}':y='ih/2-(ih/zoom/2)':d={total_frames}:s={vw}x{vh}:fps={fps}[fg];"
                f"[amb][fg]overlay={vx}:{vy}:shortest=1[basev]"
            )

    extra_inputs = ["-i", overlay_png]
    cur_label = "v_chr"
    filter_parts.append(f"[basev][2:v]overlay=0:0:eof_action=repeat[{cur_label}]")
    next_in_idx = 3

    if hook_banner_png and os.path.isfile(hook_banner_png):
        extra_inputs.extend(["-i", hook_banner_png])
        nxt_label = "v_hk"
        end_hk = min(dur, float(hook_duration))
        filter_parts.append(
            f"[{cur_label}][{next_in_idx}:v]overlay=0:152:eof_action=repeat:enable='between(t,0,{end_hk:.2f})'[{nxt_label}]"
        )
        cur_label = nxt_label
        next_in_idx += 1

    for c_idx, (c_png, c_start, c_end) in enumerate(cue_pngs):
        extra_inputs.extend(["-i", c_png])
        nxt_label = f"v_c{c_idx}"
        enable_expr = (
            f"between(t,{c_start:.3f},{c_end:.3f})"
            if c_idx == len(cue_pngs) - 1
            else f"gte(t,{c_start:.3f})*lt(t,{c_end:.3f})"
        )
        filter_parts.append(
            f"[{cur_label}][{next_in_idx}:v]overlay=0:1205:eof_action=repeat:enable='{enable_expr}'[{nxt_label}]"
        )
        cur_label = nxt_label
        next_in_idx += 1

    filter_parts.append(f"[{cur_label}]format=yuv420p[outv]")
    filter_complex = ";".join(filter_parts)

    cmd = [FFMPEG_PATH, "-y"]
    if is_vid:
        cmd.extend(["-stream_loop", "-1", "-t", f"{dur:.3f}", "-i", media_path])
    else:
        cmd.extend(["-i", media_path])
    cmd.extend(["-i", audio_path])
    cmd.extend(extra_inputs)
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-shortest",
        clip_path,
    ])

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg error on short scene {order_idx}: {res.stderr[-450:]}")
    return clip_path


def render_short_thumbnail(cfg, hero_video_path, output_jpg, temp_dir):
    """
    Render ảnh Thumbnail 1080x1920 (9:16) bắt mắt chuẩn YouTube Shorts cho từng tập:
    - Trích xuất frame nét nhất từ cảnh đắt giá nhất (thumb_scene) trong video_vi
    - Thiết kế Poster dọc với chữ Hook siêu to, độ tương phản cao để thu hút lượt bấm (CTR)
    """
    W, H = 1080, 1920
    bg_cream = (250, 247, 242, 255)      # #FAF7F2
    charcoal = (28, 25, 23, 255)         # #1C1917
    card_white = (255, 253, 249, 255)    # #FFFDF9
    lemon_yellow = (244, 196, 48, 255)   # #F4C430
    terracotta = (211, 84, 0, 255)       # #D35400
    lime_green = (124, 179, 66, 255)     # #7CB342

    accent_hex = cfg["accent_color"].lstrip("#")
    accent_rgb = tuple(int(accent_hex[i:i+2], 16) for i in (0, 2, 4)) + (255,)

    raw_frame_jpg = os.path.join(temp_dir, "hero_frame.jpg")
    if os.path.exists(raw_frame_jpg):
        try:
            os.remove(raw_frame_jpg)
        except Exception:
            pass
    ext = os.path.splitext(hero_video_path)[1].lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp"}:
        Image.open(hero_video_path).convert("RGB").save(raw_frame_jpg, quality=96)
    else:
        for ss_t in ("00:00:02.50", "00:00:00.10"):
            subprocess.run(
                [FFMPEG_PATH, "-y", "-ss", ss_t, "-i", hero_video_path, "-frames:v", "1", "-update", "1", raw_frame_jpg],
                capture_output=True,
            )
            if os.path.exists(raw_frame_jpg) and os.path.getsize(raw_frame_jpg) > 0:
                break

    canvas = Image.new("RGBA", (W, H), bg_cream)
    draw = ImageDraw.Draw(canvas)

    # Vòng tròn trang trí nền
    draw.ellipse((-150, -150, 300, 300), fill=(244, 196, 48, 50))
    draw.ellipse((W - 300, H - 420, W + 160, H + 40), fill=(124, 179, 66, 45))

    # 1. Header Thương hiệu (y = 95..180)
    logo_path = os.path.join(RESOURCES_DIR, "logo_vi.jpg")
    pill_w, pill_h = 540, 80
    pill_x = (W - pill_w) // 2
    pill_y = 95
    draw.rounded_rectangle(
        (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
        radius=40,
        fill=card_white,
        outline=charcoal,
        width=4,
    )
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA").resize((60, 60), Image.LANCZOS)
            mask = Image.new("L", (60, 60), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 60, 60), fill=255)
            canvas.paste(logo, (pill_x + 14, pill_y + 10), mask)
        except Exception:
            pass
    font_brand = _load_font(29, bold=True)
    draw.text((pill_x + 88, pill_y + 23), "VẮT CHANH CÔNG NGHỆ", font=font_brand, fill=charcoal)

    # 2. Sub-badge tập (y = 215..275)
    sub_badge = cfg.get("thumb_sub_badge", cfg["badge"])
    font_badge = _load_font(28, bold=True)
    bb = draw.textbbox((0, 0), sub_badge, font=font_badge)
    bw = (bb[2] - bb[0]) + 56
    bh = 56
    bx = (W - bw) // 2
    by = 215
    draw.rounded_rectangle(
        (bx + 4, by + 5, bx + bw + 4, by + bh + 5),
        radius=28,
        fill=(28, 25, 23, 40),
    )
    draw.rounded_rectangle(
        (bx, by, bx + bw, by + bh),
        radius=28,
        fill=accent_rgb,
        outline=charcoal,
        width=3,
    )
    badge_fg = charcoal if accent_hex.upper() == "F4C430" else (255, 255, 255, 255)
    draw.text((bx + 28, by + 11), sub_badge, font=font_badge, fill=badge_fg)

    # 3. Khung ảnh Hero Minh Họa Phóng To ở giữa (y = 310..1120 -> 1016x810)
    vx1, vy1, vx2, vy2 = 32, 310, W - 32, 1120
    vw, vh = vx2 - vx1, vy2 - vy1
    draw.rounded_rectangle(
        (vx1 + 8, vy1 + 10, vx2 + 8, vy2 + 10),
        radius=32,
        fill=(28, 25, 23, 55),
    )
    if os.path.exists(raw_frame_jpg):
        hero_img = Image.open(raw_frame_jpg).convert("RGBA")
        # Phóng nhẹ giữ tâm để hình ảnh pin to, rõ trên thumbnail điện thoại
        hw, hh = hero_img.size
        scale = max(vw / hw, vh / hh)
        new_w, new_h = int(hw * scale), int(hh * scale)
        hero_resized = hero_img.resize((new_w, new_h), Image.LANCZOS)
        crop_x = (new_w - vw) // 2
        crop_y = (new_h - vh) // 2
        hero_cropped = hero_resized.crop((crop_x, crop_y, crop_x + vw, crop_y + vh))

        mask_v = Image.new("L", (vw, vh), 0)
        ImageDraw.Draw(mask_v).rounded_rectangle((0, 0, vw, vh), radius=28, fill=255)
        canvas.paste(hero_cropped, (vx1, vy1), mask_v)

    draw.rounded_rectangle(
        (vx1, vy1, vx2, vy2),
        radius=28,
        fill=None,
        outline=charcoal,
        width=7,
    )

    # 4. Banner Hook Chữ Siêu To phía dưới (y = 1165..1640)
    bx1, by1, bx2, by2 = 36, 1165, W - 36, 1640
    draw.rounded_rectangle(
        (bx1 + 8, by1 + 10, bx2 + 8, by2 + 10),
        radius=32,
        fill=(28, 25, 23, 50),
    )
    draw.rounded_rectangle(
        (bx1, by1, bx2, by2),
        radius=32,
        fill=card_white,
        outline=charcoal,
        width=6,
    )

    # Vẽ dải màu vàng chanh điểm nhấn trên đầu thẻ chữ
    draw.rounded_rectangle(
        (bx1 + 36, by1 + 26, bx2 - 36, by1 + 120),
        radius=20,
        fill=lemon_yellow,
        outline=charcoal,
        width=3,
    )
    font_top_hook = _load_font(48, bold=True)
    t1_str = cfg["title_line1"]
    t1_b = draw.textbbox((0, 0), t1_str, font=font_top_hook)
    draw.text(((W - (t1_b[2] - t1_b[0])) // 2, by1 + 44), t1_str, font=font_top_hook, fill=charcoal)

    # Chữ Big Hook 2 dòng
    big_lines = cfg.get("thumb_big_text", cfg["title_line2"]).split("\n")
    font_big = _load_font(66, bold=True)
    for idx_b, bline in enumerate(big_lines):
        bb_line = draw.textbbox((0, 0), bline, font=font_big)
        if (bb_line[2] - bb_line[0]) > (bx2 - bx1 - 48):
            font_big = _load_font(56, bold=True)
            bb_line = draw.textbbox((0, 0), bline, font=font_big)
        lw = bb_line[2] - bb_line[0]
        ly = by1 + 155 + idx_b * 96
        fill_col = terracotta if idx_b == 0 else lime_green
        draw.text(((W - lw) // 2, ly), bline, font=font_big, fill=fill_col)

    # Phụ đề nhỏ cuối thẻ
    font_sub = _load_font(34, bold=True)
    sub_str = cfg["title_line2"]
    sb = draw.textbbox((0, 0), sub_str, font=font_sub)
    draw.text(((W - (sb[2] - sb[0])) // 2, by2 - 74), sub_str, font=font_sub, fill=charcoal)

    canvas.convert("RGB").save(output_jpg, "JPEG", quality=95)
    return output_jpg
