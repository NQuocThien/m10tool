# HƯỚNG DẪN SẢN XUẤT VIDEO DÀI & SHORTS (VẮT CHANH CÔNG NGHỆ & SQUEEZING TECH)

Xem quy trình chuẩn từng bước ngắn gọn tại [WORKFLOW.md](WORKFLOW.md).

## 1. Nhận Diện 2 Kênh
- **Kênh Tiếng Việt (`Vắt Chanh Công Nghệ`)**:
  - Slogan: *“Vắt sạch thông số, giữ lại cách dùng”*
  - Bảng màu: Nền vàng kem ấm `#FAF7F2`, vàng chanh `#F4C430`, cam đất `#D35400`, xanh lá mầm `#7CB342`, nét nâu than `#1C1917`.
  - Giọng đọc mặc định: `vi-VN-NamMinhNeural`
- **Kênh Tiếng Anh (`Squeezing Tech`)**:
  - Slogan: *“Extracting Value from Everyday Tech”*
  - Bảng màu: Nền xanh đen `#0B132B`, xanh chanh neon `#76FF03`, xanh điện tử `#00E5FF`, vàng hổ phách `#FFB300`.
  - Giọng đọc mặc định: `en-US-ChristopherNeural`

## 2. Tóm Tắt 5 Bước Chuẩn
1. **Khởi tạo**: `python make_video.py --new <ten_project>`
2. **Kịch bản dài (`script_vi.txt` / `script_en.txt`, 28–32 câu)**:
   - **Mở đầu (01–03)**: Chạm tình huống thực tế $\rightarrow$ Phá lầm tưởng $\rightarrow$ Lời chào dẫn nhập tự nhiên.
   - **Thân bài (3–4 cụm độc lập)**: Câu đầu mỗi cụm phải nêu rõ *Chủ đề chính + Khía cạnh cụm* (không dùng *"Nhưng..."*, *"Thủ phạm thứ hai..."*) để tách Shorts không bị cụt ngữ cảnh.
   - **Lời kết (3 câu cuối)**: Đúc kết thực dụng $\rightarrow$ Hỏi thăm trải nghiệm $\rightarrow$ Lời chào thương hiệu kèm slogan.
3. **Tạo Prompt & Media (`prompts_vi.txt` / `prompts_en.txt`)**:
   - Khớp `1:1` với câu thoại, xen kẽ 3 dạng cảnh (*Đời thường / Mặt cắt ẩn dụ / Thẻ Bento Card*).
   - Tải ảnh/video từ Google Flow vào `video_vi/`, `video_en/` và đánh số `01_` $\rightarrow$ `NN_`.
4. **Dựng Video Dài 16:9 & Gói YouTube (`youtube_vi.md` / `youtube_en.md`)**:
   - `python make_video.py <ten_project> --lang vi`
   - `python make_video.py <ten_project> --lang en`
5. **Tách 3–4 Tập Shorts 9:16 (`shorts_config_vi.json` / `shorts_config_en.json`)**:
   - Khai báo `"main_topic"` để hiển thị cố định Chủ đề chính trên pano đầu video (`MAIN_TOPIC • TẬP X/4`).
   - Đảm bảo `scenes[0]` của mọi tập Short nêu rõ chủ đề chính.
   - Chạy: `python .agents/skills/shorts-maker/scripts/build_shorts.py <ten_project> --lang vi` (và `--lang en`).
