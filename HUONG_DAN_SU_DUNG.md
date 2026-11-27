# HƯỚNG DẪN VẬN HÀNH NHANH — VẮT CHANH CÔNG NGHỆ (FLOW V3)

Tài liệu quy trình đầy đủ xem tại **[WORKFLOW.md](WORKFLOW.md)**.

## 1. Quy Tắc Vàng Khi Vận Hành Kênh (30 Ngày Tới)
- **Khóa 1 tệp khán giả**: Chỉ xoay vòng trong trục **Điện – Di động – Sạc nhanh GaN – Xe điện – Wi-Fi** (không nhảy sang lọc nước/bếp núc; không đăng 2 bài liên tiếp trùng 1 món đồ).
- **Nhịp đăng chuẩn**: **1 Short `9:16` độc lập (`24–34s`)/ngày** vào khung `11h30` hoặc `19h30`. Chủ đề nào đạt **`>2.000 views` & `APV > 75%`** sau 48h mới dựng thêm **1 Video dài `16:9`** (1–2 bài dài/tuần) và gắn nút *Video liên quan* từ Short trỏ sang.
- **Không lộ đáp án trên Tiêu đề**: Giữ tiêu đề `<55–65 ký tự`, khơi gợi tò mò (Curiosity Gap), tuyệt đối không gắn nhãn `Tập 1/4..4/4` trên Shorts.

## 2. Thao Tác Trên Giao Diện Studio (`run_studio.bat`)
1. Bấm **`+ Tạo Dự Án Mới`** -> Giữ tích chọn **`Chuẩn Shorts-First 9:16 dò đường`** -> Nhập tên dự án.
2. Duyệt kịch bản 6–7 câu với AI (`/topic-finder` -> `/shorts-maker`), đẩy prompt `--ar 9:16` qua tab **Bot Google Flow**, tải file về `video_short_vi/` (xóa sao AI ở tab **Xóa Star/Logo Gemini** nếu cần) rồi bấm **`🔀 Sort Resource`**.
3. Bấm **`📱 DỰNG SHORTS 9:16`** -> Tool tự tạo giọng đọc AI (`gemini:voice_5mxlq1k9luls`), dựng video `9:16` tràn viền + phụ đề động `3–5 từ/nhịp` + ảnh bìa + file chữ đăng bài trong `shorts_vi/`.
4. Khi Short nổ view -> Dùng `/video-maker` tạo bộ `16:9` trong `video_vi/` -> Bấm **`🎬 VIDEO DÀI 16:9`** để xuất video không vướng Intro 3s kèm `thumbnail_vi.jpg` tương phản cao.
