# Shorts Config Schema (`shorts_config_<lang>.json`)

Array of 3–4 episode objects. Each object maps directly to `build_shorts.py` / `make_shorts.py` rendering and metadata generation.

## Required & Recommended Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Filename slug, e.g. `short_01_lab_vs_real_range` |
| `main_topic` | string | **(Strongly Recommended)** Overarching topic of the full video (18–32 chars), e.g. `PIN XE ĐIỆN: CÔNG BỐ vs THỰC TẾ` or `SO GĂNG PIN LFP vs NCM`. Rendered in the top badge of every Short so viewers know the main theme immediately. |
| `badge` | string | Episode number & sub-angle, e.g. `TẬP 1/4 • BẪY PHÒNG LAB` / `EP 1/4 • LAB VS REALITY` |
| `title_line1` | string | Short bold header (20–30 chars), e.g. `XE ĐIỆN CÔNG BỐ 200 KM` |
| `title_line2` | string | Subtitle hook (25–42 chars), e.g. `Vì Sao Thực Tế Chỉ Đi Được 130 Km?` |
| `accent_color` | string | Hex accent from channel palette (below) |
| `scenes` | int[] | 1-based scene numbers from `script_<lang>.txt` (6–8 items, total <60s) |
| `thumb_scene` | int | 1-based scene number used as hero visual in `*_thumb.jpg` |
| `thumb_big_text` | string | 2-line hook text on thumbnail (`\n` separated, uppercase, 2–4 words/line) |
| `thumb_sub_badge` | string | Short top badge on thumbnail (include main topic + episode) |
| `yt_titles` | string[] | 3 high-CTR YouTube Shorts titles ending with `#shorts` (must include main topic keyword) |
| `yt_description` | string | Series context line (`📌 Chuỗi: [Chủ đề chính] - Tập X/4`) + bullet takeaways + CTA + hashtags |
| `yt_pinned_comment` | string | Engaging question for comment section |
| `thumb_desc` | string | Visual layout description of the thumbnail |
| `thumb_prompt` | string | 9:16 AI image prompt matching channel style, ending with anti-watermark/logo flags |

## Channel Palettes

### VI — Vắt Chanh Công Nghệ (`shorts_config_vi.json`)
- Background: `#FAF7F2` (Warm Cream)
- Allowed `accent_color`: `#D35400` (Terracotta), `#7CB342` (Lime Green), `#F4C430` (Golden Lemon)
- Thumbnail prompt style: `Vertical 9:16 YouTube Shorts thumbnail, 2D flat vector editorial tech infographic on a warm cream background (#FAF7F2), clean rounded charcoal line art (#1C1917), no text, no watermark --ar 9:16`

### EN — Squeezing Tech (`shorts_config_en.json`)
- Background: `#0B132B` (Dark Navy)
- Allowed `accent_color`: `#76FF03` (Neon Lime), `#00E5FF` (Electric Cyan), `#FFB300` (Amber)
- Thumbnail prompt style: `Vertical 9:16 YouTube Shorts thumbnail, minimalist 2D flat vector tech infographic on a dark navy blue background (#0B132B), sharp glowing geometric vector line art, high contrast, no text, no watermark, no google logo, no gemini logo, no star icon --no 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 9:16`

## Slicing & Main-Topic Context Guidelines
1. **3-Layer Main Topic Visibility**:
   - **Layer 1 (Top Overlay Pill)**: `main_topic` + `badge` stays visible 100% of the time at the top of the 9:16 frame (`PIN XE ĐIỆN: CÔNG BỐ VS THỰC TẾ • TẬP 3/4`).
   - **Layer 2 (First Spoken Scene)**: Scene `scenes[0]` of every episode must explicitly mention the main subject (never start an episode with a dangling line like *"Thủ phạm thứ ba là..."* without prepending a context scene such as Scene `1`, `3`, or `8`).
   - **Layer 3 (Subtitle Card Progress & Description)**: Subtitle header shows `Tập X/4 • Cảnh Y/M`, and `yt_description` states the series name and episode number.
2. Keep each Short between **30s and 58s** (typically 6–8 scenes).
3. Verify `len(script) == len(media)` before running `build_shorts.py`.
