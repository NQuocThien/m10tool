# Rule: Quy Chuẩn Kịch Bản & Sinh Prompt Ảnh/Video Kênh Vắt Chanh Công Nghệ

Mọi tác vụ tạo kịch bản và prompt hình ảnh/video trong dự án BẮT BUỘC tuân thủ:

1. **Chốt kịch bản trước khi tạo Prompt (Script Gate)**:
   - Phải viết kịch bản và chờ người dùng chốt duyệt xong mới được tạo tập prompt.
   - Lưu kịch bản tại `projects/<ten_project>/script_vi.txt` (kênh chỉ làm tiếng Việt).

2. **Đúng bảng màu & phong cách kênh**:
   - **Vắt Chanh Công Nghệ** (prompt ảnh/video vẫn viết bằng tiếng Anh vì công cụ AI hiểu tốt hơn):
     - Màu nền bắt buộc: `on a warm cream background (#FAF7F2)` (cấm nền tối `--no dark background`).
     - Bảng màu & style: Vàng chanh `#F4C430`, Cam đất `#D35400`, Xanh lá mầm `#7CB342`, nét viền bo tròn Nâu than `#1C1917`, phong cách `2D flat vector modern editorial tech infographic`, lồng ghép tinh tế biểu tượng nút nguồn quả chanh / lá mầm / mascot quả chanh đeo kính.
     - Lưu tại: `projects/<ten_project>/prompts_vi.txt`.

3. **Chặn sạch Logo AI / Watermark**:
   - Mọi prompt BẮT BUỘC gắn hậu tố:
     `no text, no watermark, no google logo, no gemini logo, no star icon, no sparkles --no 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text`
