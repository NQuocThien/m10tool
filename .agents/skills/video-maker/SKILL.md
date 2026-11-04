---
name: video-maker
description: Quy trình sản xuất video Tech Explainer chuẩn hóa. Hỗ trợ thảo luận kịch bản trước, chốt prompt tạo ảnh, quản lý thư mục dự án và tự động render video bằng Azure Neural TTS + FFmpeg.
---

# Video Maker Skill

Quy trình sản xuất video kỹ thuật/công nghệ từ ý tưởng đến file MP4 hoàn chỉnh qua 3 giai đoạn rõ ràng.

## Nguyên tắc cốt lõi
1. **Không vội sinh prompt ảnh**: Phải thảo luận, góp ý và chốt kịch bản câu thoại với người dùng trước.
2. **Khớp 1-1**: Số lượng ảnh luôn phải bằng đúng số lượng câu thoại trong `script.txt`.
3. **Quản lý theo thư mục**: Mọi tài nguyên thuộc về 1 video nằm trong `projects/<tên_dự_án>/`.

---

## Quy trình làm việc 3 giai đoạn

### GIAI ĐOẠN 1: Thảo luận & Lên kịch bản (Chat-first)
Khi người dùng đưa ra chủ đề hoặc yêu cầu làm video:
1. Đặt câu hỏi hoặc đề xuất mạch nội dung (Storyline):
   - Đối tượng mục tiêu là ai?
   - Cần bao nhiêu cảnh? (Thường 15-30 cảnh, mỗi cảnh ~4-6 giây).
   - Mạch so sánh / giải thích gồm những phần nào (Tổng quan -> Cấu tạo vi mô -> Thử nghiệm -> Ứng dụng thực tế).
2. Viết bản thảo kịch bản lời bình (Voiceover Script):
   - Đánh số `01`, `02`, ...
   - Câu thoại ngắn gọn, súc tích (10-18 từ/câu).
3. **Chờ phản hồi của người dùng**: Chỉnh sửa câu chữ, bổ sung luận điểm cho đến khi người dùng nói "chốt" / "ok" / "đồng ý".

---

### GIAI ĐOẠN 2: Sinh Prompt & Khởi tạo dự án
Sau khi người dùng chốt kịch bản:
1. **Khởi tạo thư mục dự án**:
   Chạy lệnh:
   ```bash
   python make_video.py --new <ten_du_an>
   ```
2. **Lưu file kịch bản**:
   Ghi toàn bộ câu thoại đã chốt vào `projects/<ten_du_an>/script.txt`.
3. **Sinh danh sách Prompt ảnh (1-1 với kịch bản)**:
   Mỗi prompt ảnh phải mô tả trực quan chính xác ý của câu thoại tương ứng, gắn kèm phong cách chuẩn:
   ```text
   3D technical render, clean engineering aesthetic, octane render, photorealistic lighting, highly detailed, 8k resolution, cinematic atmosphere --ar 16:9
   ```
   (Nếu làm Shorts/TikTok thì đổi đuôi `--ar 9:16`).
   Ghi danh sách prompt ra file để người dùng copy hoặc nạp vào bot `auto_flow.py`.

---

### GIAI ĐOẠN 3: Thu thập ảnh & Render tự động
1. Người dùng tải ảnh từ Google Flow / Midjourney về thư mục `projects/<ten_du_an>/imgs/`.
2. Kiểm tra khớp số lượng:
   - Đảm bảo số file trong `imgs/` bằng số dòng trong `script.txt`.
3. Chạy lệnh dựng video tự động 1-click:
   ```bash
   python make_video.py <ten_du_an>
   ```
   *(Nếu là video tiếng Việt, thêm cờ `--voice vi-VN-NamMinhNeural` hoặc `vi-VN-HoaiMyNeural`)*.
4. Kiểm tra video thành phẩm tại: `projects/<ten_du_an>/<ten_du_an>.mp4`.
