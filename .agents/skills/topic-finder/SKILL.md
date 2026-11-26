---
name: topic-finder
description: This skill should be used when finding new tech video topics for Vắt Chanh Công Nghệ & Squeezing Tech with deduped ideas, hooks, 4 Shorts clusters, and pocket rules.
version: 1.1.0
---

# Topic Finder — Vắt Chanh Công Nghệ & Squeezing Tech

Fast ideation workflow for proposing 5 high-retention tech video topics aligned with `video-maker` (v2.3+) and `shorts-maker` (v1.5+).

## Input Pattern

Accept a short seed domain or subject after the skill command:
- `/topic-finder sạc nhanh điện thoại`
- `/topic-finder wifi xuyên tường`
- `/topic-finder điều hòa inverter`
- `/topic-finder pin xe máy điện`

If no seed topic is provided, inspect recent projects in `projects/` and immediately propose **4 diverse everyday-tech categories** (to prevent sub-niche fatigue) or ask for the target domain in one short line.

## Workflow

### 1. Deduplicate & Check Sub-Niche Saturation
List `projects/` sorted by modification time:
```powershell
Get-ChildItem -Path projects -Directory | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime
```
Ignore utility folders (`demo_test`, `sample_template`).
- **Anti-Saturation Rule**: If the 3 most recent projects belong to the exact same sub-niche (e.g., 3+ consecutive electric motorbike battery videos), explicitly flag **Sub-Niche Fatigue Warning** in 1 line and recommend rotating to an adjacent high-demand consumer tech domain (Smartphones/GaN Chargers, Wi-Fi/Networking, Smart Home/Inverter Appliances, Audio/ANC, PC/SSD Hardware) so the Shorts Feed audience doesn't suffer visual banner blindness.

### 2. Ground Facts & Numbers
Run 1–2 targeted `search_web` queries when the seed topic involves 2025–2026 specs, safety thresholds, or pricing. Use verified numbers and real physical mechanisms; never invent specs.

### 3. Propose 5 Distinct Topics with 4 Shorts Cluster Hooks
Load `references/topic-formula.md` and generate **5 topics** covering distinct angles:
1. Myth-busting / costly mistakes
2. Internal anatomy / hidden mechanism (cutaway-friendly)
3. Head-to-head comparison or spec-vs-reality gap
4. Extreme condition / safety / failure mode
5. Emerging tech / buying decision

Each topic must fit **Vắt Chanh Công Nghệ (VI)** (Vietnamese consumer tech pain points; EN channel `Squeezing Tech` is paused) and include:
- Title + snake_case project slug (`project_slug`)
- **Hook (Tập 1 Opener)**: Shocking number or direct paradox (no cliché openings)
- **4 cụm Shorts (Mỗi cụm kèm Con số sốc / Hook 3s riêng)**: 4 standalone sub-points where **every cluster has its own concrete numeric/pain hook** ready to become an animated `[VIDEO]` Short opener
- **Quy tắc bỏ túi**: 1-sentence actionable numeric rule/formula (Open Loop payoff)

### 4. Selection Gate & Handoff
End with a brief prompt asking user to pick `1–5` (or combine/adjust).
- **Do NOT** generate full 30-line scripts or visual prompts during topic finding.
- Once user selects a topic, activate `video-maker` Stage 1.

## References
- Angle diversity, anti-saturation rotation & output template: `references/topic-formula.md`
- Downstream script rules: `../video-maker/references/script-writing-guide.md`
