# Automated AI Video Generator Pipeline

Hệ thống sản xuất video thuyết minh công nghệ (Tech Explainer) tự động từ ảnh tĩnh và kịch bản.

## 🚀 Quick Start (Chạy nhanh trong 3 bước)

1. **Tạo folder video mới**:
   ```bash
   python make_video.py --new ten_video_cua_ban
   ```

2. **Thêm tài nguyên**:
   - Thả ảnh vào `projects/ten_video_cua_ban/imgs/`
   - Soạn các câu thoại vào `projects/ten_video_cua_ban/script.txt` (1 dòng/ảnh)

3. **Render video**:
   ```bash
   python make_video.py ten_video_cua_ban
   ```

Video MP4 thành phẩm Full HD sẽ nằm ngay tại `projects/ten_video_cua_ban/ten_video_cua_ban.mp4`.

---

## 📖 Hướng Dẫn Chi Tiết
Đọc tài liệu đầy đủ tại: **[HUONG_DAN_SU_DUNG.md](HUONG_DAN_SU_DUNG.md)**
- Cách viết prompt đồng nhất phong cách.
- Danh sách giọng đọc AI tiếng Anh & tiếng Việt.
- Tự động nhận diện video ngang 16:9 (YouTube) & video dọc 9:16 (TikTok/Shorts).
- Tùy chỉnh hiệu ứng Ken Burns & cỡ chữ phụ đề.
