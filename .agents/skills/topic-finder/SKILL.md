---
name: topic-finder
description: This skill should be used when finding new tech video topics for Vắt Chanh Công Nghệ & Squeezing Tech with deduped ideas, hooks, 4 Shorts clusters, and pocket rules.
version: 1.0.0
---

# Topic Finder — Vắt Chanh Công Nghệ & Squeezing Tech

Fast ideation workflow for proposing 5 high-retention tech video topics aligned with `video-maker` and `shorts-maker`.

## Input Pattern

Accept a short seed domain or subject after the skill command:
- `/topic-finder pin xe máy điện`
- `/topic-finder sạc nhanh điện thoại`
- `/topic-finder điều hòa inverter`

If no seed topic is provided, ask for the target domain in one short line.

## Workflow

### 1. Deduplicate Against Existing Projects
List `projects/` in workspace root:
```powershell
Get-ChildItem -Name projects
```
Ignore utility folders (`demo_test`, `sample_template`). Record all existing project slugs and briefly state them in the opening line so proposed ideas never repeat or overlap covered angles.

### 2. Ground Facts & Numbers
Run 1–2 targeted `search_web` queries when the seed topic involves evolving specs, 2025–2026 tech releases, safety thresholds, or pricing. Use verified numbers and real physical mechanisms; never invent specs.

### 3. Propose 5 Distinct Topics
Load `references/topic-formula.md` and generate exactly **5 topics** (unless user specifies another count) covering different angles:
1. Myth-busting / costly mistakes
2. Internal anatomy / hidden mechanism (cutaway-friendly)
3. Head-to-head comparison or spec-vs-reality gap
4. Extreme condition / safety / failure mode
5. Emerging tech / buying decision

Each topic must fit both **Vắt Chanh Công Nghệ (VI)** and **Squeezing Tech (EN)** and include:
- Title + snake_case project slug (`project_slug`)
- **Hook**: Shocking number or direct paradox (no cliché openings)
- **4 cụm Shorts**: 4 standalone sub-points that slice cleanly into 9:16 Shorts
- **Quy tắc bỏ túi**: 1-sentence actionable rule/formula (Open Loop payoff)

### 4. Selection Gate & Handoff
End with a brief prompt asking user to pick `1–5` (or combine/adjust).
- **Do NOT** generate full 30-line scripts or visual prompts during topic finding.
- Once user selects a topic, activate `video-maker` and proceed directly to Stage 1 (drafting `script_vi.txt` & `script_en.txt`).

## References
- Angle diversity, quality checks & output template: `references/topic-formula.md`
- Downstream script rules: `../video-maker/references/script-writing-guide.md`
