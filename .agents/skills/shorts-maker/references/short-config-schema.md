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
| `yt_description` | string | Series context line (`📌 Chuỗi: [Chủ đề chính] - Tập X/4`) + bullet takeaways + CTA pointing to the clickable `▶` Related Video button (NO raw URLs) + hashtags |
| `yt_pinned_comment` | string | CTA pointing to the clickable `▶` Related Video button at bottom-left (NO raw URLs) + engaging question |
| `thumb_desc` | string | Visual layout description of the thumbnail |
| `thumb_prompt` | string | 9:16 AI image prompt matching channel style, ending with mandatory `Negative:` block & `--ar 9:16` |

## Channel Palettes & Mandatory Negative Suffix

Attach verbatim to every `thumb_prompt`:
```text
Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo.
```

### VI — Vắt Chanh Công Nghệ (`shorts_config_vi.json`)
- Background: `#FAF7F2` (Warm Cream)
- Allowed `accent_color`: `#D35400` (Terracotta), `#7CB342` (Lime Green), `#F4C430` (Golden Lemon)
- Motorbike keyword rule: Always use `sit-down Vespa-style electric moped motorbike with padded saddle seat` + `--no kick scooter, stand-up scooter`.

### EN — Squeezing Tech (`shorts_config_en.json`)
- Background: `#0B132B` (Dark Navy)
- Allowed `accent_color`: `#76FF03` (Neon Lime), `#00E5FF` (Electric Cyan), `#FFB300` (Amber)

## High-Retention Pacing & Slicing Guidelines
1. **3-Layer Main Topic Visibility**:
   - **Layer 1 (Top Overlay Pill)**: `main_topic` + `badge` visible 100% of the time (`MAIN_TOPIC • TẬP X/4`).
   - **Layer 2 (First Spoken Scene)**: Scene `scenes[0]` of every episode explicitly states the main subject.
   - **Layer 3 (Outro Hook CTA at `1.0x`)**: `build_shorts.py` appends a `~2.5s` branded CTA card using `resources/shorts_cta_{lang}.mp3` at **natural `1.0x` speed** (no speedup on outro hook).
2. **Pacing Target**: Keep each Short between **35s and 50s** after `1.18x` content tightening + `~2.5s` `1.0x` Outro Hook (total strictly `< 58s`).
3. **Audio Assets**: Place `resources/bgm_shorts.mp3` (124 BPM upbeat), `resources/sfx_whoosh.wav`, `resources/sfx_pop.wav`, and `resources/shorts_cta_{vi,en}.mp3` (1.0x speed).
4. Verify `len(script) == len(media)` before running `build_shorts.py`.
