---
name: topic-finder
description: This skill should be used when finding new tech video topics for Vắt Chanh Công Nghệ (Vietnamese-only channel) using the V3 Shorts-First Probe strategy, locked to the Power/Mobile/EV hardware audience.
version: 3.1.0
---

# Topic Finder V3.1 — Mass-Appeal Shorts-First Probe (Điện • Di Động • Xe Điện)

Generate **5 high-demand Shorts-First Probe topics (`24–34s`)** engineered for mass Vietnamese stop-scroll (`Viewed > 75%`, `APV > 85%`), Curiosity-Gap CTR (`<55 chars`), and comment-section debate.

## Input Pattern

Accept an optional seed keyword after `/topic-finder`:
- `/topic-finder` *(auto-audits `projects/` and proposes 5 diverse high-TAM topics across sub-pillars)*
- `/topic-finder củ sạc nhanh`
- `/topic-finder pin điện thoại`
- `/topic-finder wifi phòng ngủ`

## 1. Core Positioning & Mass-Appeal Filter (Mandatory)

- **30-Day Audience Lock**: **Điện – Di động – Xe điện** (*Male/Tech-Utility Seed Audience*). Do NOT jump to kitchen/plumbing appliances (`lọc nước`, `bếp từ`, `máy giặt`) unless user passes `--allow-appliance`.
- **80% Mass-Market TAM Filter (Cấm Đề Tài "Nerd Hẹp")**:
  - Every proposed topic MUST involve an everyday object owned by **>=80% of Vietnamese viewers**: *Củ sạc nhanh (GaN/PD/PPS), Cáp sạc Type-C/Lightning, Pin dự phòng, Pin/Màn hình Smartphone (iPhone/Samsung/Xiaomi), Xe máy điện & Ắc quy/Pin, hoặc Modem/Router Wi-Fi gia đình*.
  - **AVOID obscure niche hardware** (e.g., *SSD SLC Cache cliff, PSU MOV varistors, acoustic phase-cancellation math*) unless the user explicitly asks for them — narrow TAM caps Shorts views under 1,000.
- **Vietnamese Real-World Context**: Anchor hooks in familiar local price points and habits (*củ sạc 99K–150K sàn TMĐT, vừa sạc vừa ốp lưng dày, cắm sạc qua đêm, tường gạch 20cm nhà ống VN, cốp xe điện mùa nắng 40°C*).

## 2. Workflow

### Step 1: Full-Archive Deduplication & Sub-Niche Rotation
Run:
```powershell
Get-ChildItem -Path projects -Directory | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime
```
- Ignore `demo_test` and `sample_template`.
- **Full-Archive Dedup**: Read ALL existing folder slugs in `projects/` so you NEVER re-pitch an angle already covered (e.g., `lfp_vs_ncm`, `graphene_vs_lithium_cost`, `waterproof_ip67_truth`, `claimed_vs_real_range`, `hub_motor_vs_cvt_loss`, `scooter_battery_lifespan_myth`, `solid_state_waiting_trap`).
- **Anti-Collision Rule**: Never propose the exact same device as the most recent project; spread the 5 proposals across at least **3–4 distinct sub-pillars** (*Sạc & Cáp*, *Pin & Nhiệt Smartphone*, *Wi-Fi Nhà Ống*, *Xe Điện Thực Chiến*).

### Step 2: Ground Facts & Specs
Run 1–2 targeted `search_web` queries when verifying charging wattages, thermal limits (`45°C`), battery chemistries, or 2025–2026 Vietnamese market prices. Never invent numbers.

### Step 3: Generate 5 Distinct Mass-Appeal Topics (`references/topic-formula.md`)
Read `references/topic-formula.md` and map the 5 proposals across **5 distinct psychological triggers**:
1. **Bẫy đồ giá rẻ bán chạy** (Cheap bestseller hardware cutting hidden safety/thermal chips)
2. **Thói quen hàng ngày tưởng tốt hóa hại** (Counter-intuitive daily habit silently killing hardware)
3. **Thông số hãng vs Thực tế vật lý** (Why advertised numbers drop 30–50% in real Vietnamese homes)
4. **Dấu hiệu cảnh báo nguy hiểm / Cứu nguy 3 giây** (Heat, swelling, signal drop, voltage sag)
5. **Đọ trực diện 2 lựa chọn sát sườn túi tiền** (Clear buyer rule without spoiling the twist in the title)

Every topic MUST include:
- **Curiosity-Gap Title (`<55 chars`, zero verdict spoilers!)** + `project_slug`
- **Hook Cảnh 01 (`0–3s`, cận cảnh vật thật + con số đối lập)**
- **Khung Short 6 Nhịp (`24–34s`, Seamless Loop + gài Sub `1.5s`)**
- **Mồi Tranh Luận Bình Luận (2-sided viewer question to boost comment velocity)**
- **Hướng bung Video dài `16:9` (chỉ sản xuất khi Short đạt `>2.000 views` & `APV > 75%`)**

### Step 4: Selection Gate & Handoff
Ask user to choose `1–5` (or tweak an angle). Once selected, hand off directly to **`shorts-maker` (Mode 1: Standalone 9:16 Probe Short)** — do NOT generate a 28-line Long-form script upfront.

## References
- Title formulas, 5 psychological angles, TAM checklist & output template: `references/topic-formula.md`
