---
name: shorts-maker
description: This skill should be used when slicing 2-channel tech projects into vertical 9:16 YouTube Shorts with clear main-topic context, configs, thumbnails, and metadata.
version: 1.4.0
---

# Shorts Maker

Slice completed 16:9 tech projects (`projects/<project>/`) into high-retention vertical 9:16 YouTube Shorts for **Vắt Chanh Công Nghệ** (VI) and **Squeezing Tech** (EN) with clear Main Topic context, punchy pacing, and a clickable Related-Video funnel CTA.

## Core Rules

1. **Main Topic Clarity in Every Short (Bắt Buộc Rõ Chủ Đề Chính)**:
   - Viewers landing on Episode 2, 3, or 4 standalone must immediately grasp the **Main Topic**.
   - **Visual Anchor (`main_topic` + `badge`)**: Set `"main_topic"` in every episode of `shorts_config_{vi,en}.json`. `build_shorts.py` renders `MAIN_TOPIC • TẬP X/N` in the top pill and `Tập X/N • Cảnh Y/M` in the subtitle bar.
   - **Verbal Context Anchor (Cảnh Đầu Tập Tự Thân)**: The first scene in `scenes` of **every** Short must state the subject + angle directly (never open with *"Nhưng..."*, *"Thủ phạm thứ hai là..."*). Prepend Scene `1`/`2`/`3` if needed.
2. **High-Retention Pacing, SFX & Upbeat Shorts BGM (Chống Buồn Ngủ 3–5s Đầu)**:
   - Reuse existing `script_{vi,en}.txt`, `video_{vi,en}/` (or `imgs_{vi,en}/`), and `audio_{vi,en}/`.
   - `build_shorts.py` automatically trims dead silence, tightens narration to `1.18x` (+`3 kHz` vocal presence), layers `resources/sfx_whoosh.wav` (scene 1) & `sfx_pop.wav` (cuts), applies `1.12x` kinetic zoom, and mixes upbeat `resources/bgm_shorts.mp3` (`124 BPM`, `vol=0.13`, 1.0s fade-out).
3. **Outro Hook CTA (`1.0x`) & YouTube Related-Video Funnel (Cấm dán link URL chết)**:
   - YouTube disables clickable URLs in Shorts comments and descriptions. NEVER paste raw `https://youtu.be/...` links in `yt_pinned_comment` or `yt_description`.
   - Instead, direct viewers to tap the clickable **Related video (`▶` button at bottom-left above channel name)** linked in YouTube Studio.
   - `build_shorts.py` automatically appends a branded 9:16 Outro CTA card (`"XEM FULL VIDEO GỐC GÓC DƯỚI BÊN TRÁI!"` / `"▶ BẤM VIDEO LIÊN QUAN BÊN DƯỚI"`) using `resources/shorts_cta_{lang}.mp3` at **natural `1.0x` speed**.
4. **Approval Gate Before Rendering**: Propose the Shorts breakdown (3–4 episodes, `main_topic`, `title_line1/2`, duration `<55s`, and `scenes` list) and confirm with the user before rendering `.mp4`.
5. **Channel Isolation & Clean Prompts**:
   - **VI (`Vắt Chanh Công Nghệ`)**: Warm cream `#FAF7F2`, accents `#D35400`, `#7CB342`, `#F4C430`.
   - **EN (`Squeezing Tech`)**: Dark navy `#0B132B`, accents `#76FF03`, `#00E5FF`, `#FFB300`.
   - Every `thumb_prompt` must include the mandatory `Negative:` block (see `references/short-config-schema.md`) and end with `--ar 9:16`.

## Workflow

### Step 1: Audit Project Assets
Verify `projects/<project>/` contains:
- `script_vi.txt` and `script_en.txt`
- Media folder (`video_vi/` or `imgs_vi/`, `video_en/` or `imgs_en/`) with 1:1 count matching script lines
- Audio folder (`audio_vi/`, `audio_en/`) with `01_voice.mp3` .. `NN_voice.mp3`

### Step 2: Design Shorts Configs with Main Topic Anchor
Read `references/short-config-schema.md`. Group the 28–32 scenes into 3–4 focused Shorts episodes (each 6–8 scenes, ~35–55s):
- Define a unified `main_topic` across all episodes of the project.
- Verify the **first scene** of each episode introduces both the **Main Topic** and the **Episode Angle** naturally (prepend Scene 1/2/3/8 if needed).
- End each episode with a clear takeaway or conversational CTA scene.
- Write `projects/<project>/shorts_config_vi.json` and `projects/<project>/shorts_config_en.json`.

### Step 3: Validate & Render Shorts
Run dry-run validation first, then render:

```bash
python .agents/skills/shorts-maker/scripts/build_shorts.py <project> --lang vi --dry-run
python .agents/skills/shorts-maker/scripts/build_shorts.py <project> --lang vi
python .agents/skills/shorts-maker/scripts/build_shorts.py <project> --lang en
```

Use `--meta-only` to regenerate `*_thumb.jpg`, `*_dang_bai.txt`, and `TONG_HOP_DANG_SHORTS*.md` without re-rendering `.mp4`.

### Step 4: Verify Outputs
Confirm `projects/<project>/shorts_vi/` and `shorts_en/` contain for each episode:
- `<id>.mp4` (1080x1920 vertical Short with `MAIN_TOPIC • TẬP X/N` header and `Tập X/N • Cảnh Y/M` progress)
- `<id>_script.txt`, `<id>_thumb.jpg`, `<id>_dang_bai.txt`
- `TONG_HOP_DANG_SHORTS.md` (VI) / `TONG_HOP_DANG_SHORTS_EN.md` (EN)

## Bundled Resources
- `references/short-config-schema.md`: Config JSON schema including `main_topic`, Context Anchor rules, and YouTube Shorts SEO.
- `scripts/build_shorts.py`: Generic CLI builder rendering main-topic badges, progress labels, 9:16 videos, thumbnails, and metadata.
- `scripts/test_build_shorts.py`: Unit tests for config validation, `main_topic` badge formatting, and asset resolution.
