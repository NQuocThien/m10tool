# Vắt Chanh Công Nghệ (VI) — V3 Shorts-First & Dual-Aspect Video Pipeline

> **Định vị kênh**: *“Vắt sạch thông số, giữ lại cách dùng”* — Trục nội dung trọng tâm: **Điện • Di động • Sạc nhanh • Xe điện • Wi-Fi**.  
> Xem hướng dẫn vận hành chi tiết từng bước tại **[WORKFLOW.md](WORKFLOW.md)**.

---

## Điểm Mới Cốt Lõi Của Flow V3

1. **Chiến lược Shorts-First Dò Đường**: Ra 1 Short `9:16` độc lập (`24–34s`, 6–7 câu) mỗi ngày để test chủ đề; bài nào vượt `2.000 views` & `APV > 75%` mới mở rộng thành Video dài `16:9` (`3.5–4.2 phút`).
2. **Engine Render Hỗ Trợ Kép Thông Minh (`make_shorts.py` + `build_shorts.py`)**:
   - Nguồn dọc `9:16`: Phóng **Full-Bleed 100% màn hình `1080x1920`**.
   - Nguồn ngang `16:9` (khi tách từ dự án có sẵn): Dựng **nền mờ chuyển động + khung hình lớn `1048x740`**, xóa bỏ hoàn toàn "3 hộp chữ PowerPoint".
   - **Banner Hook 3.2s đầu + Phụ đề động `3–5 từ/nhịp`** kèm highlight số liệu + **Seamless Loop** mặc định.
3. **Video Dài Tối Ưu CTR & Giữ Chân (`make_video.py` + `core/renderer.py`)**:
   - Tắt mặc định Intro 3s ở giây `00:00` để vào thẳng cảnh Hook.
   - Tự động xuất **Thumbnail 16:9 tương phản cao (`thumbnail_vi.jpg`)** chữ siêu lớn đọc rõ trên điện thoại.

---

## Lệnh Khởi Chạy Nhanh

```bash
# 1. Tạo dự án Short 9:16 dò đường (6-7 câu, 24-34s)
python make_video.py --new-short <project_slug>

# 2. Kiểm duyệt Retention & Render Short 9:16 (tự động tạo TTS nếu chưa có)
python .agents/skills/shorts-maker/scripts/build_shorts.py <project_slug> --lang vi --dry-run
python .agents/skills/shorts-maker/scripts/build_shorts.py <project_slug> --lang vi

# 3. Render Video dài 16:9 + Thumbnail tương phản cao (khi chủ đề thắng view)
python make_video.py <project_slug> --lang vi --thumb-top "BẪY SẠC 65W 150K" --thumb-bottom "NƯỚNG PHỒNG PIN?!"

# 4. Hoặc mở giao diện đồ họa Studio tất-cả-trong-một
python app.py
```
