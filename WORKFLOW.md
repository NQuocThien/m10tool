# QUY TRÌNH CHUẨN V3: SHORTS-FIRST DÒ ĐƯỜNG & BUNG VIDEO DÀI THẮNG CUỘC

Hệ sinh thái **Vắt Chanh Công Nghệ (`#FAF7F2`)**: *“Vắt sạch thông số, giữ lại cách dùng”*  
**Trục khán giả khóa cứng 30 ngày**: **Điện – Di động – Sạc nhanh – Xe điện – Wi-Fi** *(Không trộn đồ bếp/lọc nước làm loạn tệp đề xuất; không đăng >2 bài liên tiếp trùng 1 thiết bị).*

---

## Tư Duy Cốt Lõi V3 (Chống Nghẹt View & Tối Đa Hóa Đăng Ký)

1. **Ngừng xả 4 Shorts dài >60s + 1 Video dài mỗi ngày**: Làm loãng kênh và rớt `APV` xuống `<40%`.
2. **Phễu 2 Giai Đoạn "Dò Đường -> Ăn Chắc"**:
   - **Giai đoạn 1 (Mỗi ngày 1 Short `9:16` độc lập, `24–34 giây`)**: Dùng `/topic-finder` -> `/shorts-maker` ra 1 Short tràn viền `9:16`, Hook chỉ hiện `3.2s` đầu, phụ đề động `3–5 từ/nhịp`, tự lặp Seamless Loop, có câu gài Subscribe `1.5s` cuối bài.
   - **Giai đoạn 2 (1–2 Video dài `16:9`/tuần cho Chủ đề Thắng)**: Short nào sau 48h vượt **`2.000 views` & `APV > 75%`** mới dùng `/video-maker` dựng bản giải phẫu sâu `24–28 câu` (`3.5–4.2 phút`, **vào thẳng Hook ở `00:00` không Intro**, có Thumbnail tương phản cao), rồi gắn nút **Video liên quan (`▶`)** từ Short thắng trỏ về!

---

## Cấu Trúc Thư Mục Dự Án Chuẩn V3 (`projects/<slug>/`)

```text
projects/<slug>/
├── script_short_vi.txt         # [GĐ 1] Kịch bản Short độc lập (6-7 câu, 24-34s)
├── prompts_short_vi_video.txt  # [GĐ 1] 2-3 prompt [VIDEO] dọc (--ar 9:16)
├── prompts_short_vi_img.txt    # [GĐ 1] 3-4 prompt [IMG] dọc (--ar 9:16)
├── video_short_vi/             # [GĐ 1] Media 9:16 đánh số 01_..06_
├── audio_short_vi/             # [GĐ 1] Giọng TTS tự sinh khi chạy build_shorts.py
├── shorts_config_vi.json       # [GĐ 1] Cấu hình Short V3 (Không nhãn Tập 1/4, skip_outro=true)
├── shorts_vi/                  # [GĐ 1] Xuất ra *.mp4 (9:16), *_thumb.jpg, *_dang_bai.txt
│
├── script_vi.txt               # [GĐ 2 - Khi Short thắng] Kịch bản dài 24-28 câu (<7s/cảnh)
├── prompts_vi_video.txt        # [GĐ 2] 6-8 prompt [VIDEO] ngang (--ar 16:9)
├── prompts_vi_img.txt          # [GĐ 2] 16-20 prompt [IMG] ngang (--ar 16:9)
├── video_vi/                   # [GĐ 2] Media 16:9 đánh số 01_..NN_
├── thumbnail_vi.jpg            # [GĐ 2] Thumbnail 16:9 tương phản cao tự xuất
├── youtube_vi.md               # [GĐ 2] Tiêu đề Curiosity Gap (<55 ký tự), Mô tả, Tags
└── <slug>_vi.mp4               # [GĐ 2] Video dài 16:9 (0s Intro, vào thẳng Hook 00:00)
```

---

## Quy Trình Thực Hiện Từng Bước

### Giai Đoạn 1: Tạo & Xuất Bản Short 9:16 Dò Đường (`24–34s`)

1. **Tìm chủ đề chuẩn trục Điện – Di động – Xe điện**:
   Gõ `/topic-finder` (hoặc `/topic-finder sạc nhanh GaN`) -> Chọn 1 trong 5 ý tưởng có Tiêu đề Curiosity Gap `<55 ký tự`.
2. **Khởi tạo dự án Shorts-First & Chốt kịch bản 6–7 câu (`/shorts-maker`)**:
   ```bash
   python make_video.py --new-short <slug>
   ```
   - Chốt `script_short_vi.txt` (6–7 câu x 10–15 từ, câu 6 gài Sub 1.5s + cầu nối Loop về câu 1).
3. **Chạy Google Flow (`--ar 9:16`) & Tải Media vào `video_short_vi/`**:
   ```bash
   python auto_flow.py projects/<slug>/prompts_short_vi_video.txt 45 65
   python auto_flow.py projects/<slug>/prompts_short_vi_img.txt 15 25
   ```
   - Giữ nguyên dấu nhận diện AI trên ảnh/video; đánh số `01_..06_` trong `video_short_vi/`.
   - Khi đăng, bật nhãn **nội dung bị thay đổi hoặc tổng hợp** (altered or synthetic content) trong YouTube Studio *(đối chiếu chính sách hiện hành của YouTube)*.
4. **Kiểm duyệt Retention & Render Short 9:16 chỉ với 1 lệnh**:
   ```bash
   python .agents/skills/shorts-maker/scripts/build_shorts.py <slug> --lang vi --dry-run
   python .agents/skills/shorts-maker/scripts/build_shorts.py <slug> --lang vi
   ```
   *(Hoặc mở `run_studio.bat` -> Chọn dự án -> Bấm **📱 DỰNG SHORTS 9:16**).*

---

### Giai Đoạn 2: Bung Video Dài 16:9 Khi Short Nổ View (`>2.000 views`, `APV > 75%`)

1. **Lên kịch bản mở rộng 24–28 câu (`/video-maker`)**:
   - Đào sâu thêm thực nghiệm/bảng so sánh chưa có trong Short; chèn câu gài Sub ở giữa bài (câu 13–15).
2. **Tạo Media `16:9` vào `video_vi/` & Render Video Dài (Không Intro 3s + Tự xuất Thumbnail 16:9)**:
   ```bash
   python make_video.py <slug> --lang vi --thumb-top "BÁO SẠC SIÊU NHANH" --thumb-bottom "NHƯNG NƯỚNG PHỒNG PIN?!"
   ```
3. **Khép kín phễu chuyển đổi**:
   - Đăng `<slug>_vi.mp4` kèm `thumbnail_vi.jpg` và tiêu đề Curiosity Gap `<55 ký tự`.
   - Vào YouTube Studio của video Short thắng cuộc -> Gắn mục **Video liên quan (Related Video)** trỏ thẳng vào video dài vừa đăng!

---

## Bảng Lệnh Nhanh (Quick CLI)

- Khởi tạo dự án Short 9:16 mới: `python make_video.py --new-short <slug>`
- Kiểm tra rủi ro rớt view Short: `python .agents/skills/shorts-maker/scripts/build_shorts.py <slug> --lang vi --dry-run`
- Render Short 9:16 (tự tạo TTS + Phụ đề động + Loop): `python .agents/skills/shorts-maker/scripts/build_shorts.py <slug> --lang vi`
- Render Video dài 16:9 + Thumbnail tương phản cao: `python make_video.py <slug> --lang vi --thumb-top "..." --thumb-bottom "..."`
- Mở giao diện đồ họa Studio: `run_studio.bat` (hoặc `python app.py`)
