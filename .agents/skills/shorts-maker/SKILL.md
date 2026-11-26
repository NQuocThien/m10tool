---
name: shorts-maker
description: This skill should be used when slicing 2-channel tech projects into vertical 9:16 YouTube Shorts with clear main-topic context, configs, thumbnails, and metadata.
version: 1.5.0
---

# Shorts Maker

Slice completed 16:9 tech projects (`projects/<project>/`) into high-retention vertical 9:16 YouTube Shorts for **Vắt Chanh Công Nghệ (VI)** with animated `.mp4` openers, concrete number hooks, highlighted subtitles, distinct per-episode visual accents, and a Related-Video funnel CTA. *(EN channel `Squeezing Tech` is paused; only generate `shorts_config_en.json` or run `--lang en` when explicitly requested.)*

## Core Rules (Anti-Swipe & High Retention)

1. **Unique Animated `.mp4` Opener + Shocking Number Hook per Short**:
   - **No Static Image Openers**: Scene `scenes[0]` of EVERY Short episode MUST be an animated `.mp4` video clip (`[VIDEO]`), NEVER a static `.jpg`/`.png`.
   - **No Duplicate Openers Across Episodes**: NEVER prepend the exact same `Scene 01` to Episode 2, 3, and 4 (returning viewers immediately swipe away thinking it is a duplicate upload). Each episode must open on its own unique `[VIDEO]` scene (`01` for Ep 1, and the animated cluster starter/climax scene for Ep 2, 3, 4).
   - **Verbal Hook in First 3s (`scenes[0]`)**: The first spoken scene of every episode MUST state a **Shocking Number / Costly Pain + Main Topic + Angle** (never open with academic transitions like *"Xét về bài toán..."*, *"Với lộ trình..."*, *"Điểm khác biệt nằm ở..."*, or *"Nhưng..."*). If a cluster starter is a static `.jpg` or weak transition, open the Short with that cluster's animated `.mp4` climax scene (`[VIDEO]`) first as a Cold Open Hook, then follow with the explanation scenes!
2. **Main Topic Clarity & Episode Visual Differentiation (Chống Mù Mẫu Thị Giác)**:
   - Set `"main_topic"` in every episode of `shorts_config_{vi,en}.json`. `build_shorts.py` renders `MAIN_TOPIC • TẬP X/N` in the top pill and `Tập X/N • Cảnh Y/M` + a dynamic **Scene Progress Bar** below the `1048x590` 16:9 viewport.
   - Assign a **distinct `accent_color`** to each episode (`#D35400`, `#F4C430`, `#7CB342` for VI; `#00E5FF`, `#76FF03`, `#FFB300` for EN) so `make_shorts.py` tints the header card, title, and progress bar differently per episode.
   - `make_shorts.py` automatically highlights numbers, units, and key tech terms in the subtitle box.
3. **High-Retention Pacing, In-Scene Final Banner & Fast Outro CTA (`~1.8s`)**:
   - `build_shorts.py` trims silence, tightens narration to `1.18x` (+`3 kHz` presence), layers `sfx_whoosh.wav` (scene 1) & `sfx_pop.wav` (cuts), applies `1.15x` kinetic zoom on static scenes, and mixes `bgm_shorts.mp3` (`124 BPM`, `vol=0.13`).
   - On the final content scene (`Cảnh N/N`), `make_shorts.py` renders an in-scene banner (`▶ BẤM VIDEO LIÊN QUAN GÓC DƯỚI ĐỂ XEM FULL`), followed by a fast `~1.8s` punchy Outro CTA card (`1.22x` tightened `shorts_cta_{lang}.mp3`). Pass `--no-outro` (or `"skip_outro": true`) when a 100% seamless loop is desired.
   - NEVER paste raw URLs in `yt_pinned_comment` or `yt_description`; always point to the clickable `▶` Related Video button.
4. **Approval Gate Before Rendering**: Run `--dry-run` first to audit retention risks, propose the 3–4 episodes breakdown, and confirm with the user before rendering `.mp4`.

## Workflow

### Step 1: Audit Project Assets
Verify `projects/<project>/` contains `script_{vi,en}.txt`, `video_{vi,en}/` (1:1 count matching script), and `audio_{vi,en}/`. Check which scene numbers in `video_{vi,en}/` are animated `.mp4` clips.

### Step 2: Design Shorts Configs (`shorts_config_{vi,en}.json`)
Read `references/short-config-schema.md`. Group scenes into 3–4 episodes (6–8 scenes each, ~32–48s):
- Ensure `scenes[0]` of every episode is a unique `.mp4` clip with a strong numeric/pain hook. (Use the cluster's `.mp4` climax scene as `scenes[0]` Cold Open if the cluster's first sentence is a `.jpg`!).
- Rotate `accent_color` across episodes so consecutive Shorts look visually distinct on the feed.

### Step 3: Validate Retention Audit & Render Shorts
Run `--dry-run` to execute `audit_shorts_retention_risks` before rendering:

```bash
python .agents/skills/shorts-maker/scripts/build_shorts.py <project> --lang vi --dry-run
python .agents/skills/shorts-maker/scripts/build_shorts.py <project> --lang vi
```

Use `--meta-only` to regenerate `*_thumb.jpg`, `*_dang_bai.txt`, and `TONG_HOP_DANG_SHORTS*.md`. Use `--no-outro` to omit the separate outro clip for seamless looping.

## Bundled Resources
- `references/short-config-schema.md`: Config JSON schema, Cold-Open `.mp4` slicing strategy, and SEO rules.
- `scripts/build_shorts.py`: CLI builder with automatic retention risk auditing, 9:16 video rendering, thumbnails, and metadata.
- `scripts/test_build_shorts.py`: Unit tests for config validation, retention risk audit, badge formatting, and asset resolution.
