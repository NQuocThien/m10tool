---
name: video-maker
description: This skill should be used when writing natural scripts, generating 2-channel visual prompts (VI/EN), and producing tech videos for Vắt Chanh Công Nghệ & Squeezing Tech.
version: 2.2.0
---

# Video Maker - Vắt Chanh Công Nghệ (VI) & Squeezing Tech (EN)

Quy trình chuẩn sản xuất kịch bản tự nhiên (dễ tách Shorts), sinh tập prompt ảnh/video đồng bộ nhận diện 2 kênh và dựng video tự động.

## Quy Tắc Cốt Lõi (BẮT BUỘC TUÂN THỦ)

1. **CHỐT KỊCH BẢN TRƯỚC - TẠO PROMPT SAU (Script Approval Gate)**:
   - **TUYỆT ĐỐI KHÔNG** sinh danh sách prompt ảnh/video khi người dùng chưa duyệt và chốt kịch bản.
   - Hoàn thành Giai đoạn 1 (viết kịch bản, trình bày và dừng lại chờ xác nhận) trước khi sang Giai đoạn 2.
2. **MỞ ĐẦU HOOK SỐC & OPEN LOOP + THÂN BÀI CHIA CỤM ĐỘC LẬP**:
   - Bắt buộc đọc `references/script-writing-guide.md` trước khi viết kịch bản.
   - **Mở đầu (Câu 01–03)**: 3 nhịp *Con số sốc / Nghịch lý trực diện -> Bóc mẽ nguyên nhân cốt lõi -> Cài Open Loop giữ chân đến cuối video* (cấm mở đầu bằng *"Chắc hẳn bạn từng..."*).
   - **Nhịp câu & Con số**: Xen kẽ nhịp ngắt ngắn (`.`, ` — `) trong câu để giọng Gemini TTS (`voice_5mxlq1k9luls` / `Charon`) nhấn nhá có trọng lượng; viết số bằng chữ số + đơn vị chuẩn (`200 km`, `65%`, `3.000 chu kỳ`) để nổi bật trên phụ đề SRT.
   - **Thân bài chia 3–4 cụm độc lập**: Đầu mỗi cụm phải là **Câu Neo Chủ Đề Tự Thân** (nêu rõ chủ đề chính + khía cạnh đang bàn, cấm mở đầu cụm bằng *"Nhưng..."*, *"Thủ phạm thứ hai là..."*) để khi cắt ra làm Shorts người xem hiểu ngay chủ đề chính.
   - **Lời kết (3 câu cuối)**: 3 nhịp *Trả Open Loop / Quy tắc bỏ túi -> Câu hỏi khảo sát con số thực tế -> Lời chào thương hiệu kèm slogan kênh*.
3. **PHÂN TÁCH ĐÚNG PHONG CÁCH & MÀU NỀN 2 KÊNH**:
   - **Kênh Tiếng Việt (`Vắt Chanh Công Nghệ`)**: Nền vàng kem ấm `#FAF7F2`, nét nâu than bo tròn, vàng chanh `#F4C430` + cam đất `#D35400` + xanh lá mầm `#7CB342`, mascot quả chanh đeo kính ở cảnh mở đầu & kết. Đọc `references/channel-vi.md`.
   - **Kênh Tiếng Anh (`Squeezing Tech`)**: Nền xanh đen thẫm `#0B132B`, nét vector phát sáng sắc gọn, xanh chanh neon `#76FF03` + xanh điện tử `#00E5FF` + vàng hổ phách `#FFB300`. Đọc `references/channel-en.md`.
4. **CHẶN SẠCH LOGO AI & HẬU TỐ NEGATIVE BẮT BUỘC**:
   - Mọi câu prompt (`[VIDEO]` và `[IMG]`) **BẮT BUỘC** gắn nguyên văn khối Negative chuẩn sau ở cuối câu và lưu trực tiếp vào `projects/<ten_project>/`:
     `Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo.`

---

## Cấu Trúc Thư Mục Chuẩn Của Một Project

```text
projects/<ten_project>/
├── script_vi.txt         # Kịch bản kênh Tiếng Việt (28-32 câu, đánh số 01. -> N.)
├── script_en.txt         # Kịch bản kênh Tiếng Anh (28-32 câu, đánh số 01. -> N.)
├── prompts_vi_video.txt  # 4-6 prompt [VIDEO] (Hook & Climax) chạy Flow Video Mode
├── prompts_vi_img.txt    # 20-24 prompt [IMG] (Mặt cắt, Bento Card...) chạy Flow/AI Image Mode
├── prompts_en_video.txt  # 4-6 prompt [VIDEO] kênh Tiếng Anh
├── prompts_en_img.txt    # 20-24 prompt [IMG] kênh Tiếng Anh
├── imgs_vi/              # (Hoặc video_vi/) Chứa ảnh (.png/.jpg) + clip (.mp4) trộn chung theo số thứ tự 01_..NN_
├── imgs_en/              # (Hoặc video_en/) Chứa ảnh + clip kênh Tiếng Anh
├── audio_vi/             # Giọng đọc TTS Tiếng Việt tự sinh
├── audio_en/             # Giọng đọc TTS Tiếng Anh tự sinh
├── subtitles_vi.srt      # Phụ đề Tiếng Việt tự sinh
├── subtitles_en.srt      # Phụ đề Tiếng Anh tự sinh
├── youtube_vi.md         # Bộ thông tin Upload YouTube kênh Việt (SEO, Timestamps, Thumbnail)
├── youtube_en.md         # Bộ thông tin Upload YouTube kênh Anh
├── <ten_project>_vi.mp4
└── <ten_project>_en.mp4
```

---

## Quy Trình Thực Thi 3 Giai Đoạn

### GIAI ĐOẠN 1: Thiết Kế & Chốt Kịch Bản Tự Nhiên (Dừng Chờ Duyệt)
1. Đọc `references/script-writing-guide.md`. Phân tích chủ đề theo tiêu chí *"Vắt sạch thông số, giữ lại cách dùng"*.
2. Soạn kịch bản `28–32 câu` (10–18 từ/câu) gồm:
   - **Câu 01–03 (Mở đầu tự nhiên)**: Gợi chuyện đời thường -> Đồng cảm phá lầm tưởng -> Chào mừng đến với kênh & dẫn nhập.
   - **Câu 04 đến N-3 (Thân bài chia 3–4 cụm độc lập)**: Mỗi cụm 6–7 câu, câu đầu cụm nêu rõ chủ đề chính để sẵn sàng cắt sang Shorts.
   - **3 câu cuối (Lời kết tự nhiên)**: Đúc kết bỏ túi -> Hỏi thăm gần gũi -> Lời chào tạm biệt gắn slogan kênh.
3. Hiển thị bản thảo kịch bản (`01..N`) kèm phân đoạn các cụm cho người dùng xem.
4. **DỪNG LẠI (STOP GATE)**: Hỏi người dùng *"Bạn chốt kịch bản này chưa để tôi lưu file và tạo tập prompt?"*. Chỉ đi tiếp khi người dùng đồng ý.

### GIAI ĐOẠN 2: Lưu Kịch Bản & Tạo Tập Prompt Tiết Kiệm (Hybrid Video + Image + Reuse)
1. Nếu chưa có thư mục `projects/<ten_project>/`, chạy: `python make_video.py --new <ten_project>`
2. Lưu kịch bản vào `projects/<ten_project>/script_vi.txt` và `script_en.txt`.
3. Đọc `references/channel-vi.md` và `references/channel-en.md`.
4. Tạo tập prompt khớp 1:1 với từng câu thoại, xen kẽ 3 dạng cảnh (*Tình huống đời thường / Mặt cắt ẩn dụ / Thẻ tổng kết Bento Card*), khóa đồng bộ hình dáng vật thể giữa các cảnh liền kề, và **phân loại rõ từng cảnh thành 3 nhóm** để tiết kiệm credit:
   - `[REUSE]` (**~3–4 cảnh Mascot Intro/Outro**): Cảnh mở đầu/kết dùng lại bộ clip mascot cố định trong `resources/` (không render mới; ghi chú rõ `# Cảnh XX [REUSE]: Copy <ten_file_mascot>.mp4 -> XX_mascot.mp4`).
   - `[VIDEO]` (**4–6 cảnh Hook & Climax**): Cảnh đầu video (`01–02`) hoặc cảnh chuyển động vật lý phức tạp cần chuyển động thật. Ghi chú `# Cảnh XX [VIDEO]: ...` và lưu vào `prompts_vi_video.txt` / `prompts_en_video.txt`.
   - `[IMG]` (**20–24 cảnh còn lại**): Toàn bộ *Mặt cắt ẩn dụ*, *Thẻ tổng kết Bento Card*, cảnh giải thích tĩnh (`renderer.py` tự thêm hiệu ứng Ken Burns `zoompan`). Ghi chú `# Cảnh XX [IMG]: ...` và lưu vào `prompts_vi_img.txt` / `prompts_en_img.txt`.

### GIAI ĐOẠN 3: Render Video & Xuất Bộ Upload YouTube
1. Chạy `auto_flow.py` tách 2 lượt:
   - Lượt Video Mode: `python auto_flow.py projects/<ten_project>/prompts_vi_video.txt`
   - Lượt Image Mode: `python auto_flow.py projects/<ten_project>/prompts_vi_img.txt`
   (Tương tự với `prompts_en_video.txt` / `prompts_en_img.txt`).
2. Gom toàn bộ media (clip `[VIDEO]`, ảnh `[IMG]`, và clip `[REUSE]` copy từ `resources/`) vào chung 1 thư mục `imgs_vi/` (hoặc `video_vi/`), đặt tên đúng thứ tự `01_<name>.mp4` / `03_<name>.png` .. `NN_<name>.mp4` khớp 1:1 với `script_vi.txt`.
3. Chạy lệnh dựng video Full HD:
   - Tiếng Việt: `python make_video.py <ten_project> --lang vi`
   - Tiếng Anh: `python make_video.py <ten_project> --lang en`
4. Tự động tạo `projects/<ten_project>/youtube_vi.md` và `youtube_en.md` gồm 5 mục: Tiêu đề (3–4 lựa chọn), Mô tả + Timestamps (đã cộng bù ~3s Intro), Tags, Bình luận ghim, và Thiết kế Thumbnail 16:9 (Text Overlay + Prompt AI).

## Tài Liệu Tham Chiếu (References)
- Công thức Mở đầu/Kết tự nhiên & Cụm kịch bản tách Shorts: `references/script-writing-guide.md`
- Quy chuẩn màu sắc & Boilerplate Kênh Tiếng Việt: `references/channel-vi.md`
- Quy chuẩn màu sắc & Boilerplate Kênh Tiếng Anh: `references/channel-en.md`
