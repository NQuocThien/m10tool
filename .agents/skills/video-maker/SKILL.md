---
name: video-maker
description: This skill should be used when writing natural scripts, generating 2-channel visual prompts (VI/EN), and producing tech videos for Vắt Chanh Công Nghệ & Squeezing Tech.
version: 2.1.0
---

# Video Maker - Vắt Chanh Công Nghệ (VI) & Squeezing Tech (EN)

Quy trình chuẩn sản xuất kịch bản tự nhiên (dễ tách Shorts), sinh tập prompt ảnh/video đồng bộ nhận diện 2 kênh và dựng video tự động.

## Quy Tắc Cốt Lõi (BẮT BUỘC TUÂN THỦ)

1. **CHỐT KỊCH BẢN TRƯỚC - TẠO PROMPT SAU (Script Approval Gate)**:
   - **TUYỆT ĐỐI KHÔNG** sinh danh sách prompt ảnh/video khi người dùng chưa duyệt và chốt kịch bản.
   - Hoàn thành Giai đoạn 1 (viết kịch bản, trình bày và dừng lại chờ xác nhận) trước khi sang Giai đoạn 2.
2. **MỞ ĐẦU & LỜI KẾT TỰ NHIÊN + THÂN BÀI CHIA CỤM ĐỘC LẬP**:
   - Bắt buộc đọc `references/script-writing-guide.md` trước khi viết kịch bản.
   - **Mở đầu (Câu 01–03)**: 3 nhịp *Chạm tình huống đời thường -> Phá vỡ lầm tưởng -> Lời chào dẫn nhập tự nhiên của kênh*.
   - **Thân bài chia 3–4 cụm độc lập**: Đầu mỗi cụm phải là **Câu Neo Chủ Đề Tự Thân** (nêu rõ chủ đề chính + khía cạnh đang bàn, cấm mở đầu cụm bằng *"Nhưng..."*, *"Thủ phạm thứ hai là..."*) để khi cắt ra làm Shorts người xem hiểu ngay chủ đề chính.
   - **Lời kết (3 câu cuối)**: 3 nhịp *Đúc kết triết lý thực dụng -> Câu hỏi trò chuyện gần gũi -> Lời chào thương hiệu kèm slogan kênh*.
3. **PHÂN TÁCH ĐÚNG PHONG CÁCH & MÀU NỀN 2 KÊNH**:
   - **Kênh Tiếng Việt (`Vắt Chanh Công Nghệ`)**: Nền vàng kem ấm `#FAF7F2`, nét nâu than bo tròn, vàng chanh `#F4C430` + cam đất `#D35400` + xanh lá mầm `#7CB342`, mascot quả chanh đeo kính ở cảnh mở đầu & kết. Đọc `references/channel-vi.md`.
   - **Kênh Tiếng Anh (`Squeezing Tech`)**: Nền xanh đen thẫm `#0B132B`, nét vector phát sáng sắc gọn, xanh chanh neon `#76FF03` + xanh điện tử `#00E5FF` + vàng hổ phách `#FFB300`. Đọc `references/channel-en.md`.
4. **CHẶN SẠCH LOGO AI & LƯU ĐÚNG VỊ TRÍ**:
   - Mọi prompt gắn hậu tố cấm chữ, watermark, logo Google/Gemini, ngôi sao AI và lưu trực tiếp vào `projects/<ten_project>/`.

---

## Cấu Trúc Thư Mục Chuẩn Của Một Project

```text
projects/<ten_project>/
├── script_vi.txt      # Kịch bản kênh Tiếng Việt (28-32 câu, đánh số 01. -> N.)
├── script_en.txt      # Kịch bản kênh Tiếng Anh (28-32 câu, đánh số 01. -> N.)
├── prompts_vi.txt     # Tập prompt chuẩn màu & style kênh Tiếng Việt (#FAF7F2)
├── prompts_en.txt     # Tập prompt chuẩn màu & style kênh Tiếng Anh (#0B132B)
├── imgs_vi/           # (Hoặc video_vi/) Chứa ảnh/clip 8s của kênh Tiếng Việt
├── imgs_en/           # (Hoặc video_en/) Chứa ảnh/clip của kênh Tiếng Anh
├── audio_vi/          # Giọng đọc TTS Tiếng Việt tự sinh
├── audio_en/          # Giọng đọc TTS Tiếng Anh tự sinh
├── subtitles_vi.srt   # Phụ đề Tiếng Việt tự sinh
├── subtitles_en.srt   # Phụ đề Tiếng Anh tự sinh
├── youtube_vi.md      # Bộ thông tin Upload YouTube kênh Việt (SEO, Timestamps, Thumbnail)
├── youtube_en.md      # Bộ thông tin Upload YouTube kênh Anh
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

### GIAI ĐOẠN 2: Lưu Kịch Bản & Tạo Tập Prompt Đồng Bộ
1. Nếu chưa có thư mục `projects/<ten_project>/`, chạy: `python make_video.py --new <ten_project>`
2. Lưu kịch bản vào `projects/<ten_project>/script_vi.txt` và `script_en.txt`.
3. Đọc `references/channel-vi.md` và `references/channel-en.md`.
4. Tạo tập prompt khớp 1:1 với từng câu thoại, xen kẽ 3 dạng cảnh (*Tình huống đời thường / Mặt cắt ẩn dụ / Thẻ tổng kết Bento Card*), khóa đồng bộ hình dáng vật thể giữa các cảnh liền kề, có dòng `# Cảnh XX: ...` phía trên.
5. Ghi vào `projects/<ten_project>/prompts_vi.txt` và `prompts_en.txt`.

### GIAI ĐOẠN 3: Render Video & Xuất Bộ Upload YouTube
1. Đổi tên media tải từ Google Flow theo đúng thứ tự `01_<name>.mp4` .. `NN_<name>.mp4` khớp với `prompts_{vi,en}.txt`.
2. Chạy lệnh dựng video Full HD:
   - Tiếng Việt: `python make_video.py <ten_project> --lang vi`
   - Tiếng Anh: `python make_video.py <ten_project> --lang en`
3. Tự động tạo `projects/<ten_project>/youtube_vi.md` và `youtube_en.md` gồm 5 mục: Tiêu đề (3–4 lựa chọn), Mô tả + Timestamps (đã cộng bù ~3s Intro), Tags, Bình luận ghim, và Thiết kế Thumbnail 16:9 (Text Overlay + Prompt AI).

## Tài Liệu Tham Chiếu (References)
- Công thức Mở đầu/Kết tự nhiên & Cụm kịch bản tách Shorts: `references/script-writing-guide.md`
- Quy chuẩn màu sắc & Boilerplate Kênh Tiếng Việt: `references/channel-vi.md`
- Quy chuẩn màu sắc & Boilerplate Kênh Tiếng Anh: `references/channel-en.md`
