---
name: topic-finder
description: This skill should be used when finding new tech video topics for Vắt Chanh Công Nghệ & Squeezing Tech using the V3 Shorts-First Probe strategy, locked to the Power/Mobile/EV hardware audience.
version: 3.0.0
---

# Topic Finder V3 — Shorts-First Probe (Trục Điện • Di Động • Xe Điện)

Propose **5 high-retention Shorts-First Probe topics (`24–34s`)** with Curiosity-Gap titles (`<55 chars`), 6-beat vertical blueprints, and Winner Long-Form expansion angles.

## Core Positioning Lock (30-Day Authority Sprint)

- **Locked Audience Pillar**: **Điện – Di động – Xe điện** (*Male/Tech-Utility Seed Audience*).
- **5 Allowed Sub-Pillars (Rotate across proposals)**:
  1. **Charging & Power**: Củ sạc GaN, chuẩn PD/PPS, cáp E-Marker, sạc dự phòng dung lượng ảo, MagSafe/Qi2 nóng máy.
  2. **Smartphone & Display**: Pin Silicon-Carbon vs Li-ion, màn OLED PWM nháy mắt, tản nhiệt buồng hơi, bẫy sạc 80% vs 100%.
  3. **EV & 2-Wheeler Mobility**: Pin LFP vs NCM, sụt áp leo dốc, phanh tái sinh, động cơ Hub vs CVT, áp suất lốp ngốn pin.
  4. **Wi-Fi & Home Networking**: Wi-Fi 6/7 băng tần 5GHz vs 2.4GHz xuyên tường, đặt sai Router, Mesh backhaul vs Repeater.
  5. **Storage, Audio & Computing**: SSD đầy 85% tụt tốc độ SLC Cache, chống ồn ANC ngược pha, ổ cắm chống sét MOV.
- **STRICT BAN**: Do NOT jump to kitchen/plumbing appliances (water purifiers, stoves) unless user passes `--allow-appliance`. Never propose 2 consecutive projects on the exact same device.

## Workflow

1. **Audit Recent Projects**: Run `Get-ChildItem -Path projects -Directory | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime` (ignore `demo_test`, `sample_template`). Flag collision if the 2 latest projects share the exact same device.
2. **Ground Specs**: Run 1–2 `search_web` queries if 2025–2026 specs/wattage/prices need verification.
3. **Propose 5 Standalone Shorts-First Topics**: Load `references/topic-formula.md`. Each topic MUST include:
   - **Curiosity-Gap Title (`<55 chars`, NEVER spoil verdict upfront)** + `project_slug`
   - **Hook Cảnh 01 (`0–3s`, cận cảnh vật thật + số liệu đối lập)**
   - **Khung Short 6 Nhịp (`24–34s`, Seamless Loop + gài Sub `1.5s`)**
   - **Hướng mở rộng Video dài 16:9 (chỉ dựng khi Short >2.000 views & APV >75%)**
4. **Handoff**: Ask user to pick `1–5`, then activate `shorts-maker` (Standalone `9:16` mode).
