# Quy Chuẩn Prompt Kênh Tiếng Việt: Vắt Chanh Công Nghệ (V3)

## 1. Nhận Diện Thương Hiệu (Brand DNA)
- **Tên kênh**: Vắt Chanh Công Nghệ
- **Slogan**: *Vắt sạch thông số, giữ lại cách dùng*
- **Trục nội dung trọng tâm**: Phần cứng Điện – Di động – Sạc nhanh – Xe điện – Mạng Wi-Fi.
- **Phong cách kết hợp V3 (Tăng Độ Tin Cậy & Xóa Cảm Giác "Rác AI")**:
  - **Cảnh Hook Mở Màn (`Cảnh 01`)**: Ưu tiên mô tả cận cảnh vật thể/tình huống đời thực có độ tương phản mạnh (ổ cắm tia lửa, củ sạc nóng đỏ, màn hình báo sóng yếu, lõi pin phồng) kết hợp đường cắt X-ray editorial sắc nét và **Mascot Chanh đeo kính chuyển động**.
  - **Các cảnh Giải Phẫu (`Cảnh 02..N`)**: 2D Flat Vector Editorial Tech Cutaway trên nền vàng kem ấm `#FAF7F2`, đường viền nâu than `#1C1917` dày dặn, điểm nhấn vàng chanh `#F4C430`, cam đất `#D35400`, xanh lá mầm `#7CB342`.

## 2. Quy Tắc Chống Lỗi Hình AI (Mandatory)
1. **CẤM chữ rởm / tiếng Anh sai ngữ cảnh trong hình**: Luôn gắn `no text, no words, no letters, no labels, no numbers` (mọi chữ và số liệu sẽ do `make_shorts.py` / `renderer.py` vẽ sắc nét bằng tiếng Việt!).
2. **BẮT BUỘC có Mascot Chanh chuyển động trong MỌI cảnh `[VIDEO]`**: `a cute animated nerdy lemon mascot wearing round glasses actively pointing / testing / shielding / reacting`.
3. **Từ khóa chuẩn cho Xe Máy Điện Việt Nam**: Luôn viết `sit-down Vespa-style electric moped motorbike with padded saddle seat and front leg shield`, cấm `kick scooter, stand-up scooter`.
4. **Bố cục an toàn cho Shorts dọc (`--ar 9:16`)**: Đặt vật thể chính và Mascot Chanh tập trung ở **vùng giữa khung hình (`y = 22% .. 65%`)**, chừa khoảng thoáng nhẹ ở đỉnh (cho Hook 3s đầu) và 1/3 dưới (cho Phụ đề động 3–5 từ).

## 3. Hậu Tố Negative Bắt Buộc (Gắn Cuối Mọi Prompt `[VIDEO]` & `[IMG]`)
```text
Negative: no text, no words, no letters, no English labels, no 3D render, no anime cel-shaded action style, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo, no google logo, no gemini star.
```

## 4. Boilerplate Chuẩn Dọc `9:16` (Shorts-First Probe — Mặc Định)
```text
[Mô tả cận cảnh hành động / mặt cắt linh kiện đặt ở trung tâm khung dọc] + featuring a cute animated nerdy lemon mascot wearing round glasses actively reacting, centered vertical composition with clean breathing room at top and bottom third, on a warm cream background (#FAF7F2), golden lemon (#F4C430), terracotta orange (#D35400) and fresh lime green (#7CB342) accents, clean rounded deep charcoal line art (#1C1917), modern editorial tech cutaway infographic, no text, no words, no letters, no google logo, no gemini logo, no star icon, no sparkles. Negative: no text, no words, no letters, no English labels, no 3D render, no anime cel-shaded action style, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo, no google logo, no gemini star. --no dark background, 3d, logo, watermark, gemini, google, star, sparkle, text, words, letters --ar 9:16
```

## 5. Boilerplate Chuẩn Ngang `16:9` (Video Dài Mở Rộng)
```text
[Mô tả mặt cắt giải phẫu / so sánh trực diện 2 bên] + on a warm cream background (#FAF7F2), warm golden lemon (#F4C430) and terracotta (#D35400) palette with fresh lime green (#7CB342) accents, clean rounded deep charcoal line art (#1C1917), modern editorial tech infographic, clean vector aesthetic, no text, no words, no letters, no google logo, no gemini logo, no star icon, no sparkles. Negative: no text, no words, no letters, no English labels, no 3D render, no anime cel-shaded action style, no bright neon cyberpunk colors, no talking mouth movement, no female voice, no Southern accent, no upbeat music, no blurry, no watermark, no logo, no google logo, no gemini star. --no dark background, 3d, logo, watermark, gemini, google, star, sparkle, text, words, letters --ar 16:9
```
