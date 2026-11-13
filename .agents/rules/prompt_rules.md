# Rule: Quy Chuẩn Kịch Bản & Sinh Prompt Ảnh/Video Cho 2 Kênh

Mọi tác vụ tạo kịch bản và prompt hình ảnh/video trong dự án BẮT BUỘC tuân thủ:

1. **Chốt kịch bản trước khi tạo Prompt (Script Gate)**:
   - Phải viết kịch bản và chờ người dùng chốt duyệt xong mới được tạo tập prompt.
   - Lưu kịch bản tại `projects/<ten_project>/script_vi.txt` (VI) hoặc `script_en.txt` (EN).

2. **Đúng bảng màu & phong cách từng kênh**:
   - **Kênh Tiếng Việt (Vắt Chanh Công Nghệ)**:
     - Màu nền bắt buộc: `on a warm cream background (#FAF7F2)` (cấm nền tối `--no dark background`).
     - Bảng màu & style: Vàng chanh `#F4C430`, Cam đất `#D35400`, Xanh lá mầm `#7CB342`, nét viền bo tròn Nâu than `#1C1917`, phong cách `2D flat vector modern editorial tech infographic`, lồng ghép tinh tế biểu tượng nút nguồn quả chanh / lá mầm / mascot quả chanh đeo kính.
     - Lưu tại: `projects/<ten_project>/prompts_vi.txt`.
   - **Kênh Tiếng Anh (Squeezing Tech)**:
     - Màu nền bắt buộc: `on a dark navy blue background (#0B132B)`.
     - Bảng màu & style: Neon Lime Green `#76FF03`, Electric Cyan `#00E5FF`, Amber `#FFB300`, phong cách `minimalist 2D flat vector infographic, flat motion design style`.
     - Lưu tại: `projects/<ten_project>/prompts_en.txt`.

3. **Chặn sạch Logo AI / Watermark**:
   - Mọi prompt BẮT BUỘC gắn hậu tố:
     `no text, no watermark, no google logo, no gemini logo, no star icon, no sparkles --no 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text`
