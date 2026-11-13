# Squeezing Tech (Vắt Chanh Công Nghệ) - Video Automation Engine

> **Slogan EN**: *Extracting Value from Everyday Tech*  
> **Slogan VI**: *Vắt sạch thông số, giữ lại cách dùng.*

---

## 🍋 Tôn Chỉ Kênh
Không đọc thông số nhà sản xuất suông. Mổ xẻ bản chất kỹ thuật bên trong để trả lời câu hỏi duy nhất của người dùng: **"Cái này đem lại giá trị gì trong thực tế?"**

---

## 🚀 Cách Sản Xuất Video Nhanh

### 1. Tạo thư mục video mới:
```bash
python make_video.py --new ten_video
```

### 2. Thêm nguyên liệu:
- Đặt ảnh tải về vào: `projects/ten_video/imgs/`
- Viết kịch bản vào: `projects/ten_video/script.txt` (1 dòng/ảnh)

### 3. Render video 1-click:
- **Tiếng Việt** (Giọng Nam Minh trầm ấm, chuẩn tin tức):
  ```bash
  python make_video.py ten_video --voice vi-VN-NamMinhNeural
  ```
- **Tiếng Anh** (Giọng Christopher chuẩn tài liệu công nghệ):
  ```bash
  python make_video.py ten_video --voice en-US-ChristopherNeural
  ```

File video MP4 Full HD xuất thẳng ra `projects/ten_video/ten_video.mp4`.

---

## 🎨 Nhận Diện Hình Ảnh Kênh (Visual Branding)
- **Tông màu chủ đạo**: Vàng Chanh / Xanh Chanh Neon (Lime Green `#39FF14`) + Xanh Điện Tử (Electric Cyan `#00F0FF`) trên nền Tối (Dark Navy `#0A0F1D`).
- **Phong cách ảnh**: 3D Isometric, X-ray cutaway, Exploded view mô phỏng cơ chế bóc tách từng lớp linh kiện.
- **Intro (2.5s)**: Hình ảnh quả chanh cơ khí 3D vắt ra các giọt vi mạch năng lượng phát sáng.
- **Outro (4s)**: *"Vắt sạch thông số, giữ lại cách dùng. Đăng ký kênh để đón xem video mổ xẻ tiếp theo!"*
