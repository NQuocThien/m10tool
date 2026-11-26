---
name: video-maker
description: This skill should be used when writing natural scripts, generating 2-channel visual prompts (VI/EN), and producing tech videos for Vắt Chanh Công Nghệ & Squeezing Tech.
version: 2.4.0
---

# Video Maker - Vắt Chanh Công Nghệ (VI-First)

Produce high-retention 30-scene tech scripts (ready for 4 standalone Shorts), generate hybrid prompts, and render Full HD 16:9 videos for **Vắt Chanh Công Nghệ (VI)**. *(EN channel `Squeezing Tech` is paused; only generate EN assets if user explicitly requests `--en`.)*

## Core Rules (Mandatory)

1. **Script Approval Gate (Chốt Kịch Bản Trước - Tạo Prompt Sau)**:
   - NEVER generate image/video prompts before user approves the script.
   - Complete Stage 1 (draft script + show 4 Shorts cluster hooks) and wait for confirmation before Stage 2.
2. **Scroll-Stopping Hooks for Intro & All 4 Shorts Clusters**:
   - Read `references/script-writing-guide.md` before drafting.
   - **Intro (Scenes 01–03)**: 3 beats — *Shocking Number/Paradox -> Core Mechanism Reveal -> Open Loop Payoff Promise* (ban *"Chắc hẳn bạn từng..."*).
   - **4 Body Clusters (Scenes 04 to N-3)**: Every cluster starter (e.g., Scenes `04`, `10`, `16`, `22`) is the **0-second opener of a Short**. It MUST be a **Self-Contained Hook (Shocking Number / Costly Pain + Main Topic + Cluster Angle)**.
   - **Ban Academic Transitions**: NEVER open a cluster with *"Xét về bài toán..."*, *"Với lộ trình..."*, *"Trong bài toán..."*, *"Điểm khác biệt nằm ở..."*, *"Khi mua..., lầm tưởng là..."*, or *"Thủ phạm thứ hai là..."*.
   - **Pacing & Numbers**: Use internal punctuation (`.`, ` — `) for Gemini TTS (`voice_5mxlq1k9luls` / `Charon`) weight; write numbers as digits + units (`200 km`, `65%`, `150 triệu`, `3.000 chu kỳ`) for subtitle keyword highlighting.
3. **Mandatory `[VIDEO] (.mp4)` Allocation, Topic-Matched Outro (`29`, `30`) & Animated Lemon Mascot**:
   - To prevent static `.jpg` slideshows in Shorts, allocate **7–8 `[VIDEO]` prompts** directly to **Scene 01 (Short 1 Opener)**, **Cluster 2, 3, and 4 Starter Scenes (Shorts 2, 3, 4 Openers)**, **1–2 Climax/Scene 02 clips**, PLUS **the last 2 Outro Scenes (`N-1` Survey & `N` Sign-off, e.g. Scenes `29` and `30`)**.
   - **NEVER reuse off-topic Outro clips (`29_mascot_survey.mp4`, `30_mascot_outro.mp4`) from unrelated niches** (e.g., never copy electric motorbike outro clips into a water purifier, smartphone, or Wi-Fi video). Always write dedicated topic-specific `[VIDEO]` prompts for Scenes `N-1` (`29`) and `N` (`30`) featuring the main device/subject of the current project alongside the animated lemon mascot. Only Scene `03` (`03_mascot_intro.mp4` - neutral lemon battery beaker) may be reused as `[REUSE]`.
   - Every Short episode (`1/4` to `4/4`) must start with an animated `.mp4` clip in its first scene.
   - **Mandatory Moving Lemon Mascot in ALL `[VIDEO]` Prompts**: Every single `[VIDEO]` prompt in `prompts_{vi,en}_video.txt` MUST include the animated lemon mascot (`a cute animated nerdy lemon mascot wearing round glasses`) actively moving, reacting, pointing, or interacting with the objects in the scene (never static).
4. **Channel Visual Isolation & Mandatory Negative Suffix**:
   - **VI (`Vắt Chanh Công Nghệ`)**: Warm cream `#FAF7F2`, charcoal outlines `#1C1917`, accents `#F4C430`, `#D35400`, `#7CB342`, lemon mascot in intro/outro. See `references/channel-vi.md`.
   - **EN (`Squeezing Tech`)**: Dark navy `#0B132B`, glowing vector lines, accents `#76FF03`, `#00E5FF`, `#FFB300`. See `references/channel-en.md`.
   - Append the verbatim `Negative:` block from `references/channel-vi.md` to EVERY `[VIDEO]` and `[IMG]` prompt.

---

## Project Directory Structure

```text
projects/<project>/
├── script_vi.txt         # VI script (28-32 lines, 01. -> NN.)
├── script_en.txt         # EN script (28-32 lines, 01. -> NN.)
├── prompts_vi_video.txt  # 5-6 [VIDEO] prompts (Scene 01 + Cluster 2/3/4 Openers + Climax)
├── prompts_vi_img.txt    # 20-23 [IMG] prompts (Cutaways, Bento Cards)
├── prompts_en_video.txt  # 5-6 [VIDEO] prompts (EN)
├── prompts_en_img.txt    # 20-23 [IMG] prompts (EN)
├── video_vi/             # Combined .mp4 + .jpg/.png matched 1:1 with script_vi.txt
├── video_en/             # Combined .mp4 + .jpg/.png matched 1:1 with script_en.txt
├── audio_vi/             # Generated VI TTS audio (01_voice.mp3 .. NN_voice.mp3)
├── audio_en/             # Generated EN TTS audio
├── youtube_vi.md         # VI YouTube SEO package (Titles, Timestamps, Tags, 16:9 Thumb)
└── youtube_en.md         # EN YouTube SEO package
```

---

## 3-Stage Execution Workflow

### Stage 1: Draft High-Retention Script (Stop Gate)
1. Read `references/script-writing-guide.md`.
2. Draft `28–32 lines` (10–18 words/line):
   - **Lines 01–03 (Intro)**: Paradox/Shocking Number -> Core Cause -> Open Loop.
   - **Lines 04 to N-3 (4 Standalone Clusters)**: 6–7 lines per cluster. Line 1 of each cluster MUST combine **Shocking Number/Pain + Main Topic + Angle**.
   - **Last 3 Lines (Outro)**: Pocket Rule Payoff -> Numeric Audience Question -> Brand Sign-off.
3. Display script with the 4 Shorts cluster boundaries and highlight which scenes will be `[VIDEO]` openers.
4. **STOP GATE**: Ask user to approve before saving files or generating prompts.

### Stage 2: Save Script & Generate Hybrid Prompts (`[VIDEO]` + `[IMG]` + `[REUSE]`)
1. Initialize folder if needed: `python make_video.py --new <project>`
2. Save `script_vi.txt` (skip `script_en.txt` unless `--en` is requested).
3. Read `references/channel-vi.md`.
4. Split 1:1 prompts into 3 groups for VI:
   - `[REUSE]` (**1 Neutral Mascot Intro scene**): Only Scene `03` (`03_mascot_intro.mp4` — neutral lemon beaker graphic) is copied from existing projects. NEVER copy `29_mascot_survey.mp4` or `30_mascot_outro.mp4` from another niche.
   - `[VIDEO]` (**7–8 animated `.mp4` scenes**): **MUST include Scene `01` (Short 1 hook) + the 3 starter scenes of Clusters 2, 3, 4 (Shorts 2, 3, 4 hooks)** + 1–2 key climax scenes + **Scenes `N-1` (`29`) and `N` (`30`) custom-tailored to the project's main device/topic with the animated lemon mascot**. Save to `prompts_vi_video.txt`.
   - `[IMG]` (**Remaining 21–22 scenes**): Cutaways, metaphors, and Bento cards. Save to `prompts_vi_img.txt`.

### Stage 3: Render Full HD Video & YouTube Package
1. Run `auto_flow.py` for `prompts_vi_video.txt` (Video Mode) and `prompts_vi_img.txt` (Image Mode).
2. Assemble all media into `video_vi/` numbered `01_..NN_` matching script lines.
3. Render 16:9 video: `python make_video.py <project> --lang vi`.
4. Generate `youtube_vi.md`.

## References
- Script & 4-Cluster Shorts Hook Formula: `references/script-writing-guide.md`
- VI Channel Style & Prompts: `references/channel-vi.md`
- EN Channel Style & Prompts: `references/channel-en.md`
