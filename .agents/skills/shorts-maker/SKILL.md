---
name: shorts-maker
description: This skill should be used when slicing existing 2-channel tech projects into vertical 9:16 YouTube Shorts, generating shorts configs, thumbnails, and metadata.
version: 1.0.0
---

# Shorts Maker

Slice completed 16:9 tech projects (`projects/<project>/`) into vertical 9:16 YouTube Shorts for **Vắt Chanh Công Nghệ** (VI) and **Squeezing Tech** (EN).

## Core Rules

1. **Reuse Existing Media & Audio**: Slice scenes from existing `script_{vi,en}.txt`, `video_{vi,en}/` (or `imgs-clean/`, `imgs/`), and `audio_{vi,en}/` (or `audio/`). Do not regenerate voiceover or clips unless missing.
2. **Approval Gate Before Rendering**: Propose the Shorts breakdown (3–4 episodes, 6–8 scenes each, <60s) and confirm with user before writing `shorts_config_{vi,en}.json` and rendering `.mp4`.
3. **Channel Isolation**:
   - **VI (`Vắt Chanh Công Nghệ`)**: Warm cream `#FAF7F2`, accents `#D35400`, `#7CB342`, `#F4C430`.
   - **EN (`Squeezing Tech`)**: Dark navy `#0B132B`, accents `#76FF03`, `#00E5FF`, `#FFB300`.
4. **Clean AI Thumbnail Prompts**: Every `thumb_prompt` must include `--ar 9:16` and forbid text, watermarks, Google/Gemini logos, and AI stars.

## Workflow

### Step 1: Audit Project Assets
Verify `projects/<project>/` contains:
- `script_vi.txt` and `script_en.txt`
- Media folder (`video_vi/` or `imgs_vi/`, `video_en/` or `imgs-clean/` or `imgs/`) with 1:1 count matching script lines
- Audio folder (`audio_vi/`, `audio_en/` or `audio/`) with `01_voice.mp3` .. `NN_voice.mp3`

### Step 2: Design Shorts Configs
Read `references/short-config-schema.md`. Group the 25–30 scenes into 3–4 focused Shorts episodes (each 6–8 scenes, ~35–55s):
- Start each Short with a strong hook scene (often scenes `1–3` or a dramatic contrast scene).
- End with a clear takeaway or CTA scene.
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
- `<id>.mp4` (1080x1920 vertical Short, <60s)
- `<id>_script.txt`
- `<id>_thumb.jpg`
- `<id>_dang_bai.txt`
- `TONG_HOP_DANG_SHORTS.md` (VI) / `TONG_HOP_DANG_SHORTS_EN.md` (EN)

## Bundled Resources
- `references/short-config-schema.md`: Config JSON schema, accent colors, and YouTube Shorts SEO/thumbnail rules.
- `scripts/build_shorts.py`: Generic CLI builder reusing `make_shorts.py` layout/thumbnail renderers for any project.
- `scripts/test_build_shorts.py`: Unit tests for config validation and asset path resolution.
