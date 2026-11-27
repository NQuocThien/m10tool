---
name: shorts-maker
description: Primary Stage-1 skill in V3 workflow. Produces standalone 24-34s Full-Bleed 9:16 Probe Shorts (or slices 1-2 standalone Shorts from 16:9 projects) with 3.2s Hook banners, 3-5 word dynamic captions, and Seamless Loop.
version: 3.0.0
---

# Shorts Maker V3 — Standalone 9:16 Probe & Smart Showcase

Primary Stage-1 skill for **Vắt Chanh Công Nghệ (VI)**:
- **Mode 1 (Default — Shorts-First Probe)**: Build **1 standalone `9:16` Full-Bleed Short (`24–34s`, 6–7 scenes)** per topic to validate demand (`>2,000 views`, `APV > 75%`) before producing Long-form.
- **Mode 2 (Smart Repurpose)**: Slice **at most 1–2 standalone Shorts (`<35s`)** from a `16:9` project (blurred ambient backdrop + `1048x740` hero + dynamic captions).

## Core Rules (Mandatory)
1. **Strict `24–34s` Target (`6–7` Lines, `10–15` Words/Line)**: Hard cap `<38s` (`<=7` scenes).
2. **Ban Episode Numbering (`TẬP X/4`)**: Never put `Tập 1/4`, `Part 1`, `Episode 1` in `badge`, `title_line1`, or `thumb_sub_badge`.
3. **3.2s Hook + Dynamic 3–5 Word Captions + Seamless Loop**:
   - `make_shorts.py` V3 shows the Hook Banner ONLY in `0..3.2s` of Scene 01, pops 3–5 word highlighted captions at `y=1205..1475`, and defaults to `skip_outro: true` (`--no-outro`).
4. **20% Real-World Proof + 80% 2D Vector Cutaway (`--ar 9:16`) + Micro Sub Cue**:
   - Scene `01` `[VIDEO]`: Close-up physical symptom + moving nerdy lemon mascot.
   - Scenes `02–05`: 2D cutaway anatomy (`1 [VIDEO]` + `3 [IMG]`, `--ar 9:16`).
   - Scene `06` `[VIDEO]`: Pocket rule + **1.5s Subscribe cue** (*"Đăng ký Vắt Chanh để không mất tiền oan vì thông số ảo..."*) bridging back into Scene 01.

## Mode 1 Workflow (Standalone 9:16 Probe)
1. **Stage 1 (Stop Gate)**: Draft `6–7` lines (`10–15` words/line) + Curiosity-Gap title (`<65 chars`, zero spoilers). Wait for user approval.
2. **Stage 2**: Run `python make_video.py --new-short <slug>`. Save `script_short_vi.txt`, `prompts_short_vi_video.txt` (`--ar 9:16`), `prompts_short_vi_img.txt` (`--ar 9:16`), and `shorts_config_vi.json` (`references/short-config-schema.md`).
3. **Stage 3**: Place media (`01_..06_`) into `video_short_vi/`, then audit & render (auto-generates TTS!):
   ```bash
   python .agents/skills/shorts-maker/scripts/build_shorts.py <slug> --lang vi --dry-run
   python .agents/skills/shorts-maker/scripts/build_shorts.py <slug> --lang vi
   ```
