# Quy Chuẩn Prompt Kênh Tiếng Việt: Vắt Chanh Công Nghệ

## 1. Nhận Diện Thương Hiệu (Brand DNA)
- **Tên kênh**: Vắt Chanh Công Nghệ
- **Slogan**: *Vắt sạch thông số, giữ lại cách dùng*
- **Phong cách chủ đạo**: 2D Flat Vector Editorial Tech, nét vẽ bo tròn thân thiện, ấm áp, trực quan dễ hiểu cho người xem Việt Nam.

## 2. Bảng Màu Bắt Buộc (Color Palette)
- **Màu nền (Background)**: Vàng kem ấm (`warm cream background (#FAF7F2)`). **TUYỆT ĐỐI KHÔNG** dùng nền xanh đen hay nền tối.
- **Màu chủ đạo (Primary)**: Vàng chanh ấm (`golden lemon yellow #F4C430`) kết hợp Cam đất (`terracotta orange #D35400`).
- **Màu điểm nhấn (Accent)**: Xanh lá mầm (`fresh lime green #7CB342`) đại diện cho sự bền bỉ, an toàn, sinh thái và sóng công nghệ.
- **Đường nét (Outlines)**: Nâu than đậm (`clean rounded deep charcoal line art #1C1917`), nét dày dặn, bo góc mềm mại.

## 3. Liên Kết Phong Cách Logo & Banner Kênh
Khi viết prompt cho các cảnh giải thích hoặc so sánh, lồng ghép tinh tế các yếu tố nhận diện từ Logo & Banner kênh:
- **Biểu tượng nút nguồn quả chanh**: `stylized lemon power emblem` hoặc `subtle lemon tech badge detail`.
- **Lá mầm / Sóng công nghệ**: `sprout leaf accent` hoặc `lime green Wi-Fi wave motif`.
- **Mascot (BẮT BUỘC có chuyển động trong MỌI cảnh `[VIDEO]` + Mở đầu / CTA cuối video)**: `a cute animated nerdy lemon mascot wearing round glasses` đang cử động sinh động (chỉ tay, bật công tắc, quạt khói, ôm heo đất, giơ ngón cái...). Mọi câu prompt trong `prompts_vi_video.txt` bắt buộc phải có linh vật chanh chuyển động tương tác với bối cảnh.
- **Từ khóa bắt buộc cho Xe Máy Điện (Tránh vẽ nhầm xe trượt Kick Scooter)**: Luôn dùng `sit-down Vespa-style electric moped motorbike with padded saddle seat and front leg shield` (hoặc `electric motorbike`), kèm hậu tố cấm `no kick scooter, no stand-up scooter` và `--no kick scooter, stand-up scooter, push scooter`. **TUYỆT ĐỐI KHÔNG** viết trống không là `electric scooter` (AI phương Tây mặc định hiểu là xe trượt đứng Xiaomi).
- **Bố cục**: Bento card bo góc nhẹ nhàng hoặc mặt cắt 2D trực quan (`modern editorial tech infographic`).

## 4. Cấu Trúc Prompt Chuẩn Kênh Việt

### Hậu tố Negative bắt buộc (Gắn cuối MỌI câu prompt `[VIDEO]` và `[IMG]`):
```text
Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo.
```

### Công thức ghép Prompt:
```text
[Mô tả hành động/vật thể chính trực quan] + on a warm cream background (#FAF7F2), [Chi tiết màu sắc: lime green / golden lemon / terracotta orange] + [Chi tiết liên kết thương hiệu nhẹ nếu phù hợp] + clean rounded charcoal line art, modern editorial tech infographic, clean vector aesthetic, no text, no google logo, no gemini logo, no star icon, no sparkles. Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo. --no dark background, 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 16:9
```

### Boilerplate Video Ngang (16:9 - YouTube):
```text
on a warm cream background (#FAF7F2), warm golden lemon and terracotta palette with lime green accents, clean rounded charcoal line art, modern editorial tech infographic, clean vector aesthetic, no text, no google logo, no gemini logo, no star icon, no sparkles. Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo. --no dark background, 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 16:9
```

### Boilerplate Video Dọc (9:16 - Shorts/TikTok/Reels):
```text
on a warm cream background (#FAF7F2), warm golden lemon and terracotta palette with lime green accents, clean rounded charcoal line art, modern editorial tech infographic, clean vector aesthetic, no text, no google logo, no gemini logo, no star icon, no sparkles. Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo. --no dark background, 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 9:16
```

## 5. Ví Dụ Định Dạng Trong `prompts_vi_video.txt` / `prompts_vi_img.txt`
```text
# Cảnh 01 [VIDEO]: [Tóm tắt ngắn gọn nội dung câu thoại số 01]
Top-down 2D flat vector comparison of two electric motorbike battery packs side by side on a warm cream background (#FAF7F2), left LFP pack framed in sturdy lime green and charcoal outline, right NCM pack framed in energetic golden lemon and terracotta orange outline, stylized lemon power emblem in center as comparison divider, clean rounded line art, modern editorial tech infographic, no text, no google logo, no gemini logo, no star icon, no sparkles. Negative: no 3D render, no photorealistic, no anime cel-shaded action style, no complex shading, no realistic proportions, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo. --no dark background, 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 16:9
```
