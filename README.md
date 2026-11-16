# Vắt Chanh Công Nghệ (VI) & Squeezing Tech (EN) — Video & Shorts Pipeline

> **Kênh Tiếng Việt (`Vắt Chanh Công Nghệ`)**: *“Vắt sạch thông số, giữ lại cách dùng”* — Nền vàng kem ấm `#FAF7F2`  
> **Kênh Tiếng Anh (`Squeezing Tech`)**: *“Extracting Value from Everyday Tech”* — Nền xanh đen `#0B132B`

Tài liệu quy trình chuẩn từng bước: Xem chi tiết tại **[WORKFLOW.md](WORKFLOW.md)**.

---

## Quy Trình Nhanh 5 Bước

1. **Khởi tạo dự án**:
   ```bash
   python make_video.py --new <ten_project>
   ```
2. **Soạn kịch bản (`script_vi.txt` & `script_en.txt`, 28–32 câu)**:
   - **Mở đầu (01–03)**: Gợi chuyện đời thường $\rightarrow$ Phá lầm tưởng $\rightarrow$ Lời chào dẫn nhập tự nhiên.
   - **Thân bài (3–4 cụm độc lập)**: Đầu mỗi cụm có câu neo chủ đề chính (không mở đầu cụm bằng *"Nhưng..."*, *"Thứ hai là..."*) để sẵn sàng cắt sang Shorts.
   - **Lời kết (3 câu cuối)**: Đúc kết thực dụng $\rightarrow$ Câu hỏi trò chuyện $\rightarrow$ Lời chào thương hiệu kèm slogan.
3. **Sinh Prompt & Tải Media (`prompts_vi.txt` & `prompts_en.txt`)**:
   - Đẩy prompt lên Google Flow: `python auto_flow.py projects/<ten_project>/prompts_vi.txt`
   - Lưu media vào `video_vi/` (hoặc `imgs_vi/`) và `video_en/` (hoặc `imgs_en/`), đánh số thứ tự `01_` $\rightarrow$ `NN_`.
4. **Render Video Dài 16:9 & Xuất Gói YouTube (`youtube_vi.md` & `youtube_en.md`)**:
   ```bash
   python make_video.py <ten_project> --lang vi
   python make_video.py <ten_project> --lang en
   ```
5. **Tách 3–4 Tập YouTube Shorts 9:16 (`shorts_config_vi.json` & `shorts_config_en.json`)**:
   - Khai báo `"main_topic"` để gắn nhãn Chủ đề chính cố định trên đầu mọi tập Short.
   ```bash
   python .agents/skills/shorts-maker/scripts/build_shorts.py <ten_project> --lang vi --dry-run
   python .agents/skills/shorts-maker/scripts/build_shorts.py <ten_project> --lang vi
   python .agents/skills/shorts-maker/scripts/build_shorts.py <ten_project> --lang en
   ```
