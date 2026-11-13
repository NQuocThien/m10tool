---
name: video-maker
description: This skill should be used when writing scripts, generating 2-channel visual prompts (VI/EN), and producing tech videos for Vắt Chanh Công Nghệ & Squeezing Tech.
version: 2.0.0
---

# Video Maker - Hệ Sinh Thái Kênh Vắt Chanh Công Nghệ (VI) & Squeezing Tech (EN)

Quy trình chuẩn sản xuất kịch bản, sinh tập prompt ảnh/video đồng bộ nhận diện 2 kênh và dựng video tự động.

## Quy Tắc Cốt Lõi (BẮT BUỘC TUÂN THỦ)

1. **CHỐT KỊCH BẢN TRƯỚC - TẠO PROMPT SAU (Script Approval Gate)**:
   - **TUYỆT ĐỐI KHÔNG** sinh danh sách prompt ảnh/video khi người dùng chưa duyệt và chốt kịch bản.
   - Luôn hoàn thành Giai đoạn 1 (viết kịch bản, trình bày cho người dùng và dừng lại chờ xác nhận) trước khi bước sang Giai đoạn 2.
2. **PHÂN TÁCH ĐÚNG PHONG CÁCH & MÀU NỀN 2 KÊNH**:
   - **Kênh Tiếng Việt (`Vắt Chanh Công Nghệ`)**: Nền vàng kem ấm `#FAF7F2` (`warm cream background (#FAF7F2)`), nét nâu than bo tròn, màu vàng chanh `#F4C430` + cam đất `#D35400` + xanh lá mầm `#7CB342`, điểm xuyết biểu tượng quả chanh nút nguồn / lá mầm / mascot đeo kính. Đọc chi tiết tại `references/channel-vi.md`.
   - **Kênh Tiếng Anh (`Squeezing Tech`)**: Nền xanh đen thẫm `#0B132B` (`dark navy blue background (#0B132B)`), nét vector phát sáng sắc gọn, màu xanh chanh neon `#76FF03` + xanh điện tử `#00E5FF` + vàng hổ phách `#FFB300`. Đọc chi tiết tại `references/channel-en.md`.
3. **LUÔN CHẶN SẠCH LOGO AI & WATERMARK**:
   - Mọi prompt bắt buộc gắn hậu tố cấm chữ, watermark, logo Google/Gemini và ngôi sao AI.
4. **LƯU ĐÚNG VỊ TRÍ TRONG PROJECT**:
   - Mọi file kịch bản và tập prompt phải lưu trực tiếp vào `projects/<ten_project>/` theo đúng bảng cấu trúc chuẩn bên dưới.

---

## Cấu Trúc Thư Mục Chuẩn Của Một Project

```text
projects/<ten_project>/
├── script_vi.txt      # Kịch bản kênh Tiếng Việt (đánh số 01. -> N.)
├── script_en.txt      # Kịch bản kênh Tiếng Anh (đánh số 01. -> N.)
├── prompts_vi.txt     # Tập prompt chuẩn màu & style kênh Tiếng Việt (#FAF7F2)
├── prompts_en.txt     # Tập prompt chuẩn màu & style kênh Tiếng Anh (#0B132B)
├── imgs_vi/           # (Hoặc video_vi/) Chứa ảnh/clip 8s của kênh Tiếng Việt
├── imgs_en/           # (Hoặc video_en/, imgs/) Chứa ảnh/clip của kênh Tiếng Anh
├── audio_vi/          # Giọng đọc TTS Tiếng Việt tự sinh
├── audio_en/          # Giọng đọc TTS Tiếng Anh tự sinh
├── subtitles_vi.srt   # Phụ đề Tiếng Việt tự sinh
├── subtitles_en.srt   # Phụ đề Tiếng Anh tự sinh
├── youtube_vi.md      # Bộ thông tin Upload YouTube kênh Việt (Tiêu đề, Mô tả + Timestamps, Tags, Thumbnail Prompt)
├── youtube_en.md      # Bộ thông tin Upload YouTube kênh Anh (Titles, Description + Timestamps, Tags, Thumbnail Prompt)
├── <ten_project>_vi.mp4
└── <ten_project>_en.mp4
```

---

## Quy Trình Thực Thi 3 Giai Đoạn

### GIAI ĐOẠN 1: Thiết Kế & Chốt Kịch Bản (Dừng Chờ Duyệt)
1. Phân tích chủ đề theo tiêu chí *"Vắt sạch thông số, giữ lại cách dùng"*: biến lý thuyết phức tạp thành ví dụ thực tế gần gũi.
2. Cấu trúc kịch bản (25–30 câu, mỗi câu 10–18 từ, ~4–6 giây/cảnh):
   - **Câu 01–03 (Hook)**: Đánh thẳng vào nỗi đau/sự phân vân thực tế của người dùng.
   - **Câu 04–27 (Thân bài)**: Giải thích nguyên lý bằng hình ảnh ẩn dụ trực quan, so sánh đối lập rõ ràng.
   - **Câu cuối (CTA)**: Câu hỏi mở kích thích bình luận tương tác.
3. Hiển thị bản thảo kịch bản (`01..N`) cho người dùng xem.
4. **DỪNG LẠI (STOP GATE)**: Hỏi người dùng *"Bạn chốt kịch bản này chưa để tôi lưu file và tạo tập prompt?"*. Chỉ đi tiếp khi người dùng đồng ý.

### GIAI ĐOẠN 2: Lưu Kịch Bản & Tạo Tập Prompt Chuẩn Vị Trí
Ngay sau khi người dùng chốt kịch bản:
1. Kiểm tra thư mục `projects/<ten_project>/`. Nếu chưa có, chạy:
   ```bash
   python make_video.py --new <ten_project>
   ```
2. Lưu kịch bản đã chốt vào đúng file:
   - Kênh Việt: `projects/<ten_project>/script_vi.txt`
   - Kênh Anh: `projects/<ten_project>/script_en.txt`
3. Đọc `references/channel-vi.md` (cho kênh Việt) hoặc `references/channel-en.md` (cho kênh Anh).
4. Tạo tập prompt khớp 1:1 với từng câu thoại (số lượng prompt = số câu trong script), mỗi prompt có dòng ghi chú `# Cảnh XX: ...` phía trên để tương thích với Bot Google Flow (`auto_flow.py`).
5. Ghi tập prompt vào đúng vị trí:
   - Kênh Việt: `projects/<ten_project>/prompts_vi.txt`
   - Kênh Anh: `projects/<ten_project>/prompts_en.txt`

### GIAI ĐOẠN 3: Thu Thập Media, Render Video & Tạo Bộ Upload YouTube (Bắt Buộc)
1. Chạy Bot Google Flow từ Studio UI (`run_studio.bat`) hoặc nạp file `prompts_vi.txt` / `prompts_en.txt` để tải ảnh hoặc video 8s vào `imgs_vi/`, `video_vi/`, `imgs_en/`, hoặc `video_en/`.
2. **Kiểm tra & Chuẩn hóa thứ tự file (`01_` -> `30_`)**:
   - Nếu file tải về từ Google Flow có tên theo mô tả tiếng Anh (chưa đánh số đầu file), **BẮT BUỘC** đối chiếu tên/khung hình với `prompts_vi.txt` / `prompts_en.txt` để đổi tên thành `01_<name>.mp4` .. `30_<name>.mp4` trước khi chạy `make_video.py` (tránh bị sắp xếp theo bảng chữ cái làm lệch cảnh).
3. Chạy lệnh dựng video Full HD (tự ghép Intro kênh + TTS + Subtitles):
   - Tiếng Việt: `python make_video.py <ten_project> --lang vi`
   - Tiếng Anh: `python make_video.py <ten_project> --lang en`
4. **TỰ ĐỘNG XUẤT BỘ THÔNG TIN UPLOAD YOUTUBE (`youtube_vi.md` & `youtube_en.md`)**:
   Ngay khi hoàn thành dựng video (hoặc theo yêu cầu đóng gói dự án), **BẮT BUỘC** tự động tạo và lưu file `projects/<ten_project>/youtube_vi.md` và `projects/<ten_project>/youtube_en.md`, đồng thời hiển thị tóm tắt cho người dùng gồm đủ 5 mục:
   - **Gợi ý Tiêu đề (3–4 lựa chọn)**: Giật tít kích thích tò mò (CTR cao), đánh trúng nỗi đau thực tế và chứa từ khóa SEO.
   - **Mô tả Video (Description)**: Tóm tắt súc tích theo tôn chỉ *"Vắt sạch thông số, giữ lại cách dùng"*, kèm **Mốc thời gian (Timestamps `00:00`)** đã cộng bù chính xác thời lượng Intro (`intro_vi.mp4` / `intro_en.mp4` ~3 giây) với `subtitles_vi.srt` / `subtitles_en.srt`, bài học rút ra và Hashtags.
   - **Thẻ từ khóa (Tags)**: Chuỗi từ khóa cách nhau bằng dấu phẩy để copy-paste thẳng vào YouTube Studio.
   - **Bình luận ghim (Pinned Comment)**: Câu hỏi khảo sát nhanh kích thích người xem bình luận.
   - **Thiết kế Ảnh bìa (Thumbnail 16:9)**:
     - Gợi ý chữ đè lên Thumbnail (Text Overlay 3–5 từ ngắn gọn, tương phản mạnh).
     - Prompt tạo ảnh nền Thumbnail (`--ar 16:9`, chừa khoảng trống hợp lý cho chữ, đúng bảng màu `#FAF7F2` cho kênh Việt và `#0B132B` cho kênh Anh, chặn sạch chữ/watermark AI).

---

## Tài Liệu Tham Chiếu (References)
- Quy chuẩn màu sắc, style Logo/Banner & Boilerplate Kênh Tiếng Việt: `references/channel-vi.md`
- Quy chuẩn màu sắc, style Logo/Banner & Boilerplate Kênh Tiếng Anh: `references/channel-en.md`
