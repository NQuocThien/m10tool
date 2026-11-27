# Shorts Config Schema V3 (`shorts_config_<lang>.json`)

Array of **1 standalone Short object** (Shorts-First Mode 1) or **1–2 standalone Short objects** (Repurpose Mode 2).

## Fields
- `id`: Filename slug (e.g. `short_01_gan_charger_trap`)
- `main_topic`: Concise topic tag (`14–28 chars`). **NO `TẬP 1/4`!**
- `badge`: Sub-angle tag (`12–24 chars`, e.g. `BÓC MẼ PHẦN CỨNG`). **NO `TẬP 1/4`!**
- `title_line1`: 3.2s Hook Banner Line 1 (`16–26 chars`)
- `title_line2`: 3.2s Hook Banner Line 2 (`20–38 chars`)
- `accent_color`: `#D35400`, `#F4C430`, or `#7CB342` (VI)
- `scenes`: `5–7` 1-based scene ints (`24–34s` total, hard cap `<38s`). `scenes[0]` MUST be `.mp4`!
- `thumb_scene`: 1-based hero scene int
- `thumb_big_text`: 2-line `\n`-separated uppercase hook (`2–4 words/line`)
- `thumb_sub_badge`: Top thumbnail badge (`VẮT CHANH CÔNG NGHỆ`) — **NO `TẬP 1/4`!**
- `skip_outro`: `true` (default V3 Seamless Loop)
- `has_related_video`: `false` in Stage-1 Probe; set `true` once `16:9` Long-form video is published
- `yt_titles`: 3 Curiosity-Gap titles (`<65 chars` + `#shorts`), never spoiling verdict upfront
- `yt_description`, `yt_pinned_comment`, `thumb_desc`, `thumb_prompt` (`--ar 9:16` + mandatory `Negative:` block)
