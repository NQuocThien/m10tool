# Shorts Config Schema (`shorts_config_<lang>.json`)

Array of 3–4 episode objects mapping directly to `build_shorts.py` and `make_shorts.py`.

## Required & Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Filename slug, e.g. `short_01_lab_vs_real_range` |
| `main_topic` | string | **(Mandatory)** Overarching topic of the full video (18–32 chars), e.g. `PIN THỂ RẮN: BẪY CHỜ ĐỢI 2032`. Rendered in the top badge of every Short. |
| `badge` | string | Episode number & sub-angle, e.g. `TẬP 1/4 • BẪY PHÒNG LAB` / `EP 1/4 • LAB VS REALITY` |
| `title_line1` | string | Short bold header (18–28 chars), tinted with `accent_color` |
| `title_line2` | string | Subtitle hook (24–42 chars) |
| `accent_color` | string | Hex accent rotated across episodes to break template fatigue |
| `scenes` | int[] | 1-based scene numbers from `script_<lang>.txt` (6–8 items). **`scenes[0]` MUST be a unique `.mp4` clip!** |
| `thumb_scene` | int | 1-based scene number used as hero visual in `*_thumb.jpg` |
| `thumb_big_text` | string | 2-line hook text on thumbnail (`\n` separated, uppercase, 2–4 words/line) |
| `thumb_sub_badge` | string | Short top badge on thumbnail (include main topic + episode) |
| `yt_titles` | string[] | 3 high-CTR YouTube Shorts titles ending with `#shorts` |
| `yt_description` | string | Series context line + bullet takeaways + CTA pointing to clickable `▶` Related Video button (NO raw URLs) + hashtags |
| `yt_pinned_comment` | string | CTA pointing to clickable `▶` Related Video button at bottom-left (NO raw URLs) + engaging question |
| `thumb_desc` | string | Visual layout description of the thumbnail |
| `thumb_prompt` | string | 9:16 AI image prompt matching channel style, ending with mandatory `Negative:` block & `--ar 9:16` |
| `skip_outro` | bool | *(Optional)* Set `true` to skip the `~1.8s` outro card and rely solely on the final scene's in-scene CTA pill for seamless loop |

## Anti-Swipe Slicing Strategy (Cold-Open `.mp4` Technique)

When slicing a hybrid project (where only 5–6 scenes are `.mp4` and 20+ scenes are `.jpg`):
1. **Never start a Short with a `.jpg` static image**: If Cluster 2 spans scenes `[10, 11, 12, 13, 14, 15]` and only Scene `13` (or `14`) is an animated `.mp4` climax clip while Scene `10` is a `.jpg`, **place the `.mp4` climax scene first as a Cold Open Hook**: e.g. `scenes: [13, 10, 11, 12, 14, 15]` (provided the verbal flow works as a teaser hook + explanation), OR ensure Scene `10` was generated as `[VIDEO] .mp4`.
2. **Never repeat `Scene 01` as `scenes[0]` across multiple episodes**: Only Episode 1 may open with `Scene 01`. Episodes 2, 3, and 4 must each have their own distinct opening scene so subscribers don't swipe away thinking they already watched it.
3. **Rotate `accent_color` across the 4 episodes**:
   - **VI (`#FAF7F2`)**: Ep 1 `#D35400` (Terracotta), Ep 2 `#F4C430` (Golden Lemon), Ep 3 `#7CB342` (Lime Green), Ep 4 `#D35400` or `#7CB342`.
   - **EN (`#0B132B`)**: Ep 1 `#00E5FF` (Electric Cyan), Ep 2 `#76FF03` (Neon Lime), Ep 3 `#FFB300` (Amber), Ep 4 `#76FF03` or `#00E5FF`.

## Channel Palettes & Mandatory Negative Suffix

Attach verbatim to every `thumb_prompt`:
```text
Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo.
```

- **VI Motorbike Keyword Rule**: Always use `sit-down Vespa-style electric moped motorbike with padded saddle seat` + `--no kick scooter, stand-up scooter`.
