# Quy Chuẩn Prompt Kênh Tiếng Anh: Squeezing Tech

## 1. Nhận Diện Thương Hiệu (Brand DNA)
- **Tên kênh**: Squeezing Tech
- **Slogan**: *Extracting Value from Everyday Tech*
- **Phong cách chủ đạo**: Minimalist 2D Flat Vector Motion Infographic, sắc nét, hiện đại, tương phản cao chuẩn công nghệ quốc tế.

## 2. Bảng Màu Bắt Buộc (Color Palette)
- **Màu nền (Background)**: Xanh đen thẫm (`dark navy blue background (#0B132B)`).
- **Màu chủ đạo (Primary)**: Xanh chanh neon (`glowing neon lime green #76FF03`).
- **Màu phụ trợ (Secondary)**: Xanh điện tử (`electric cyan #00E5FF`).
- **Màu điểm nhấn (Accent)**: Vàng hổ phách phát sáng (`glowing amber #FFB300`).
- **Đường nét (Outlines)**: Nét vector hình học sắc gọn, phát sáng nhẹ (`sharp glowing geometric vector line art`).

## 3. Liên Kết Phong Cách Logo & Banner Kênh
Khi viết prompt cho các cảnh giải thích hoặc so sánh, lồng ghép tinh tế các yếu tố nhận diện từ Logo & Banner kênh:
- **Biểu tượng lõi năng lượng**: `minimalist circular battery emblem` hoặc `clean circular wave icon`.
- **Đường dẫn mạch & Tín hiệu**: `glowing cyan circuit traces` và `neon lime energy indicator dots`.
- **Từ khóa bắt buộc cho Xe Máy Điện (Tránh vẽ nhầm xe trượt Kick Scooter)**: Luôn dùng `sit-down Vespa-style electric moped motorbike with padded saddle seat and front leg shield` (hoặc `electric motorbike`), kèm hậu tố cấm `no kick scooter, no stand-up scooter` và `--no kick scooter, stand-up scooter, push scooter`. **TUYỆT ĐỐI KHÔNG** viết trống không là `electric scooter`.
- **Bố cục**: Mặt cắt kỹ thuật tối giản (`cutaway 2D vector schematic`, `top-down technical blueprint`), không rườm rà.

## 4. Cấu Trúc Prompt Chuẩn Kênh Anh

### Hậu tố Negative bắt buộc (Gắn cuối MỌI câu prompt `[VIDEO]` và `[IMG]`):
```text
Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo.
```

### Công thức ghép Prompt:
```text
[Mô tả hành động/sơ đồ kỹ thuật 2D trực quan] + on a dark navy blue background (#0B132B), [Chi tiết màu sắc: glowing neon lime green / electric cyan / amber accents] + minimalist 2D flat vector infographic, flat motion design style, modern tech explainer graphic, clean vector aesthetic, no text, no google logo, no gemini logo, no star icon, no sparkles. Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo. --no 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 16:9
```

### Boilerplate Video Ngang (16:9 - YouTube):
```text
on a dark navy blue background (#0B132B), glowing neon lime green and electric cyan accents, minimalist 2D flat vector infographic, flat motion design style, modern tech explainer graphic, clean vector aesthetic, no text, no google logo, no gemini logo, no star icon, no sparkles. Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo. --no 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 16:9
```

### Boilerplate Video Dọc (9:16 - Shorts/TikTok):
```text
on a dark navy blue background (#0B132B), glowing neon lime green and electric cyan accents, minimalist 2D flat vector infographic, flat motion design style, modern tech explainer graphic, clean vector aesthetic, no text, no google logo, no gemini logo, no star icon, no sparkles. Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo. --no 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 9:16
```

## 5. Ví Dụ Định Dạng Trong `prompts_en_video.txt` / `prompts_en_img.txt`
```text
# Scene 01 [VIDEO]: [Short summary of script line 01]
Top-down 2D flat vector comparison of two electric motorbike battery packs side by side on a dark navy blue background (#0B132B), left LFP pack framed in sturdy neon lime green outline, right NCM pack framed in sleek electric cyan outline, glowing amber versus badge between them, minimalist 2D flat vector infographic, flat motion design style, modern tech explainer graphic, no text, no google logo, no gemini logo, no star icon, no sparkles. Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo. --no 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 16:9
```
