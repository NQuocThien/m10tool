---
name: video-maker
description: Stage-2 Long-Form Deep-Dive skill in V3 workflow. Expands proven winning Shorts (>2,000 views & APV >75%) into high-retention 24-28 scene 16:9 videos (0s Intro, dynamic pacing <7s/scene, high-contrast 16:9 thumbnail).
version: 3.0.0
---

# Video Maker V3 — High-Retention 16:9 Deep Dive (Winner Expansion)

Expand proven Shorts topics (or user-selected flagship topics in the **Điện – Di động – Xe điện** pillar) into crisp **3.5 – 4.2 minute (`24–28` scene)** Full HD `16:9` videos that open directly on the Hook at `00:00` and auto-generate high-contrast thumbnails.

## Core Rules (Mandatory for Long-Form CTR & Retention)

1. **When to Run `video-maker`**:
   - In V3 Shorts-First workflow, run `video-maker` when a Probe Short proves strong audience demand (`>2,000 views`, `APV > 75%`), OR when the user explicitly asks for a `16:9` Long-form video.
   - Do **NOT** simply stretch the exact same 6 Short images into 5 minutes — add **real-world failure cases, comparative benchmarks, and deeper physical cutaways** so viewers clicking `Related Video` from the Short feel rewarded immediately!
2. **Zero Dead Intro at `00:00` (`use_intro=False` Default)**:
   - `make_video.py` V3 starts directly at `00:00` on **Scene 01 `[VIDEO]`** (no 3-second static logo card killing Autoplay retention!).
   - Keep every spoken line tight (`10–16 words/line`, `24–28 lines` total) so average scene duration stays **`5.5 – 7.0s`** (`3.5 – 4.2 min` total), never dragging `10–11s` on a static image.
3. **Script Approval Gate**:
   - Read `references/script-writing-guide.md` first.
   - Present the `24–28` line script + 3 Curiosity-Gap `16:9` Titles (`<55 chars`) + 2-line Thumbnail Big Text, and **STOP for user approval** before generating prompts.
4. **Visual Variety (20% Real-World Context + 80% 2D Cutaway + Moving Mascot)**:
   - Allocate **6–8 `[VIDEO]` (`.mp4`) scenes**: Scene `01` (00:00 Cold Open Hook), each major section starter, climax mechanism test, plus custom-tailored Outro scenes (`N-1` Survey & `N` Brand Sign-off). Every `[VIDEO]` prompt MUST include the moving nerdy lemon mascot interacting with the hardware.
   - Insert a **Mid-Roll Value Subscribe Cue** around Scene `14–16` (middle of video, while retention is still high) rather than waiting until the final 5 seconds.
   - Follow `references/channel-vi.md` color palette (`#FAF7F2`) and append the verbatim `Negative:` block (banning AI text/watermarks/stars).
5. **Mandatory High-Contrast 16:9 Custom Thumbnail**:
   - `make_video.py` auto-renders `thumbnail_vi.jpg` with a dark left contrast scrim + giant `96–104px` 2-line Curiosity Text (`--thumb-top` & `--thumb-bottom`). Never upload a Long-form video without a high-contrast thumbnail!

---

## 3-Stage Execution Workflow

### Stage 1: Draft Crisp `24–28` Line Script & Packaging (Stop Gate)
1. Draft `24–28` lines (`10–16` words/line):
   - **Scenes `01–03` (00:00 Cold Open)**: Shocking Cost/Physics Paradox -> Hidden Culprit -> Open Loop Payoff Promise.
   - **3–4 Crisp Body Sections (`Scenes 04 .. N-3`)**: Physical mechanism cutaways + real-world test benchmarks + 1 mid-roll 1-sentence value Subscribe cue.
   - **Final 3 Scenes**: Memorable numeric Pocket Rule -> Concrete user comment question -> Brand sign-off.
2. Propose **Curiosity-Gap Title (`<55 chars`)** + **`--thumb-top` / `--thumb-bottom` (max 3–4 words/line)**.
3. **STOP GATE**: Wait for user confirmation.

### Stage 2: Save Script & Generate `16:9` Hybrid Prompts
1. Ensure project folder exists (`python make_video.py --new <project>` if not already created via `--new-short`).
2. Save `script_vi.txt`, `prompts_vi_video.txt` (`6–8 [VIDEO] --ar 16:9`), and `prompts_vi_img.txt` (`16–20 [IMG] --ar 16:9`).

### Stage 3: Render 16:9 Video + Auto-Thumbnail + Link Winning Short
1. Place media in `video_vi/` (`01_..NN_`) (keep AI provenance marks intact; enable YouTube's altered/synthetic content label when uploading).
2. Render 0s-Intro video + high-contrast thumbnail:
   ```bash
   python make_video.py <project> --lang vi --thumb-top "<3-4 CHỮ ĐẦU>" --thumb-bottom "<3-4 CHỮ NHẤN>"
   ```
3. Generate `youtube_vi.md`, and remind user to link the Probe Short's **Related Video (`▶`)** to this full breakdown!

## References
- Script pacing, mid-roll sub trigger & packaging rules: `references/script-writing-guide.md`
- VI Channel visual prompts (`--ar 16:9` & `--ar 9:16`): `references/channel-vi.md`
