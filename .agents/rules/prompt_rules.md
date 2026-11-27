# Rule: Quy Chuẩn Kịch Bản & Sinh Prompt Ảnh/Video Kênh Vắt Chanh Công Nghệ (Flow V3)

Mọi tác vụ tạo kịch bản và prompt hình ảnh/video trong dự án BẮT BUỘC tuân thủ:

1. **Chốt kịch bản trước khi tạo Prompt (Script Gate)**:
   - Phải trình bày kịch bản (kèm Tiêu đề Curiosity Gap `<55–65 ký tự`, không lộ đáp án) và **chờ người dùng chốt duyệt xong** mới được sinh file prompt.
   - Kênh chỉ sản xuất **Tiếng Việt (`Vắt Chanh Công Nghệ`)**:
     - **Giai đoạn 1 (Short 9:16 dò đường, 6–7 câu, `24–34s`)**: Lưu tại `projects/<slug>/script_short_vi.txt`.
     - **Giai đoạn 2 (Video dài 16:9 mở rộng khi Short thắng view, 24–28 câu)**: Lưu tại `projects/<slug>/script_vi.txt`.

2. **Tách riêng File Prompt `[VIDEO]` và `[IMG]` có gắn nhãn `# Cảnh XX` (để chạy `Sort Resource`)**:
   - Dòng ngay trên mỗi prompt BẮT BUỘC có comment `# Cảnh XX [VIDEO]: ...` hoặc `# Cảnh XX [IMG]: ...` khớp đúng số câu thoại `XX` để nút `🔀 Sort Resource` tự động đánh số file tải về.
   - **Giai đoạn 1 (`--ar 9:16`)**: Lưu tại `prompts_short_vi_video.txt` (2–3 cảnh `.mp4`, bắt buộc có Cảnh `01` và Cảnh cuối) và `prompts_short_vi_img.txt` (3–4 cảnh `.png`/`.jpg`).
   - **Giai đoạn 2 (`--ar 16:9`)**: Lưu tại `prompts_vi_video.txt` (6–8 cảnh `.mp4`, bắt buộc có Cảnh `01` và 2 cảnh kết) và `prompts_vi_img.txt` (16–20 cảnh tĩnh).

3. **Đúng bảng màu, Mascot chuyển động & Chống chữ rác AI**:
   - Prompt viết bằng tiếng Anh: nền bắt buộc `on a warm cream background (#FAF7F2)`, bảng màu Vàng chanh `#F4C430`, Cam đất `#D35400`, Xanh lá mầm `#7CB342`, nét viền bo tròn Nâu than `#1C1917`, phong cách `2D flat vector modern editorial tech cutaway infographic`.
   - Mọi prompt `[VIDEO]` bắt buộc có `a cute animated nerdy lemon mascot wearing round glasses` đang tương tác/chuyển động thực tế.
   - Mọi prompt BẮT BUỘC gắn hậu tố cấm chữ sai & watermark:
     `no text, no words, no letters, no English labels, no watermark, no google logo, no gemini logo, no star icon, no sparkles. Negative: no text, no words, no letters, no English labels, no 3D render, no anime cel-shaded action style, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo, no google logo, no gemini star. --no dark background, 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text, words, letters` (kèm `--ar 9:16` cho Short hoặc `--ar 16:9` cho Video dài).
