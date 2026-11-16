# Shorts Config Schema (`shorts_config_<lang>.json`)

Array of 3–4 episode objects. Each object maps directly to `make_shorts.py` rendering and metadata generation.

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Filename slug, e.g. `short_01_five_range_thieves` |
| `badge` | string | Uppercase pill badge, e.g. `TẬP 1 • BẪY QUẢNG CÁO` / `EPISODE 1 • LAB VS REALITY` |
| `title_line1` | string | Short bold header (20–30 chars), e.g. `XE ĐIỆN CÔNG BỐ 200 KM` |
| `title_line2` | string | Subtitle hook (25–42 chars), e.g. `Vì Sao Thực Tế Chỉ Đi Được 120 Km?` |
| `accent_color` | string | Hex accent from channel palette (below) |
| `scenes` | int[] | 1-based scene numbers from `script_<lang>.txt` (6–8 items, total <60s) |
| `thumb_scene` | int | 1-based scene number used as hero visual in `*_thumb.jpg` |
| `thumb_big_text` | string | 2-line hook text on thumbnail (`\n` separated, uppercase, 2–4 words/line) |
| `thumb_sub_badge` | string | Short top badge on thumbnail |
| `yt_titles` | string[] | 3 high-CTR YouTube Shorts titles ending with `#shorts` |
| `yt_description` | string | Hook + bullet takeaways + comment CTA + channel subscribe + hashtags |
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

## Slicing Guidelines
1. Keep each Short between **30s and 58s** (typically 6–8 scenes from a 30-scene script).
2. Ensure `scenes` flow logically as a standalone story: Hook -> Explanation/Contrast -> Practical Takeaway/CTA.
3. Verify `len(script) == len(media)` before running `build_shorts.py`.
