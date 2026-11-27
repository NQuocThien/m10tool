# Tổng quan dự án & PDR (Product Development Requirements)

> Dự án: **Vắt Chanh Công Nghệ — Video Pipeline (Flow V3)**
> Cập nhật: 2026-11-27

## 1. Bối cảnh

"Vắt Chanh Công Nghệ" là kênh YouTube tiếng Việt chuyên giải thích phần cứng công nghệ với slogan *"Vắt sạch thông số, giữ lại cách dùng"*. Trục nội dung bị khóa vào 5 nhóm: **Điện – Di động – Sạc nhanh – Xe điện – Wi-Fi**.

Repo này là công cụ cá nhân (chạy trên Windows) giúp một người làm kênh đi từ **kịch bản → giọng đọc AI → phụ đề → video hoàn chỉnh → thumbnail → nội dung đăng bài** mà không cần phần mềm dựng phim.

## 2. Mục tiêu sản phẩm

| # | Mục tiêu | Đo bằng |
|---|---|---|
| G1 | Ra **1 Short 9:16 / ngày** để dò chủ đề | Thời gian dựng 1 Short < 15 phút sau khi có media |
| G2 | Chỉ làm video dài cho chủ đề đã thắng | Short đạt `> 2.000 views` và `APV > 75%` sau 48h |
| G3 | Giữ nhận diện thương hiệu nhất quán | Nền `#FAF7F2`, bảng màu chanh/cam đất/xanh mầm, mascot chanh |
| G4 | Tối thiểu chi phí API | TTS gộp 5 câu/request, cache theo nội dung câu |
| G5 | Tuân thủ chính sách nền tảng | Khai báo nội dung AI khi đăng; ghi nguồn tài nguyên trong `resources/CREDITS.md` |

## 3. Người dùng

- **Chủ kênh / người vận hành** (1 người): viết hoặc duyệt kịch bản, tạo media qua Google Flow, bấm dựng, đăng bài.
- **AI agent** (Antigravity / Claude…): dùng các skill trong `.agents/skills/` để đề xuất chủ đề, viết kịch bản, sinh prompt, cấu hình Short.

## 4. Phạm vi chức năng

### 4.1 Trong phạm vi

| Mã | Chức năng | Thành phần |
|---|---|---|
| F1 | Khởi tạo dự án (Short-first hoặc video dài) | `make_video.py --new-short / --new` |
| F2 | Tìm chủ đề, viết kịch bản, sinh prompt theo giọng kênh | Skill `topic-finder`, `shorts-maker`, `video-maker` |
| F3 | Đẩy danh sách prompt lên Google Flow tự động | `auto_flow.py` (Playwright) |
| F4 | Sắp xếp/đổi tên media theo số cảnh trong file prompt | `core/sorter.py` |
| F5 | Sinh giọng đọc tiếng Việt (Gemini TTS, dự phòng Edge TTS) có cache | `core/tts.py`, `core/tts_cache.py`, `core/vi_text.py` |
| F6 | Sinh phụ đề SRT (video dài) và caption động 3–5 từ (Short) | `core/subtitles.py` |
| F7 | Render video dài 16:9 (Ken Burns / 2.5D, phụ đề, BGM, intro tùy chọn) | `core/renderer.py` |
| F8 | Render Short 9:16 (Hook 3.2s, caption động, Seamless Loop) + audit retention | `build_shorts.py`, `make_shorts.py` |
| F9 | Xuất thumbnail và file nội dung đăng bài | `render_long_thumbnail`, `render_short_thumbnail`, `*_dang_bai.txt` |
| F10 | Giao diện Studio Tkinter gom mọi thao tác | `app.py` |

### 4.2 Ngoài phạm vi (hiện tại)

- Upload tự động lên YouTube, lấy số liệu Analytics.
- Kênh tiếng Anh (đã gỡ; tham số `--lang` chỉ còn `vi` để tương thích lệnh cũ).
- Chạy trên macOS/Linux (Studio dùng `winsound`, file `.bat`).

## 5. Yêu cầu phi chức năng

| Mã | Yêu cầu |
|---|---|
| NF1 | **Tái lập**: sửa 1 câu kịch bản chỉ tạo lại audio câu đó (cache theo hash `voice + style + text`). |
| NF2 | **Chịu lỗi API**: hết quota (HTTP 429) ở model TTS nào thì chuyển ngay sang model dự phòng kế tiếp. |
| NF3 | **Hiệu năng**: render cảnh song song (tối đa 4 luồng FFmpeg); tách lớp 2.5D chạy tuần tự trước để tránh tranh CPU. |
| NF4 | **An toàn dữ liệu**: manifest TTS ghi atomic; thư mục tạm luôn bị dọn kể cả khi lỗi. |
| NF5 | **Unicode**: console ép UTF-8 để log tiếng Việt không làm crash render trên Windows. |
| NF6 | **Không phụ thuộc FFmpeg hệ thống**: dùng binary đi kèm `imageio-ffmpeg`. |

## 6. Quy tắc nội dung bắt buộc (Business rules)

| Quy tắc | Giá trị | Nơi kiểm tra |
|---|---|---|
| Độ dài Short | 24–34s, 6–7 câu, 10–15 từ/câu, trần cứng < 38s | `audit_shorts_retention_risks` |
| Cảnh mở đầu Short | Phải là video `.mp4`, có con số cụ thể | Audit (`[RETENTION RISK]`, `[RETENTION TIP]`) |
| Nhãn tập | Cấm `Tập 1/4`, `Part 1`, `Episode 1` | Audit + `format_overlay_badge` tự gỡ |
| Tiêu đề YouTube | Curiosity Gap, < 55–65 ký tự, không lộ đáp án | Audit (`[CTR TIP]`, `[CURIOSITY RISK]`) |
| Video dài | 24–28 câu, 3.5–4.2 phút, < 7s/cảnh, **không intro** ở 00:00 | Mặc định `use_intro=False` |
| Prompt hình ảnh | Viết tiếng Anh, nền `#FAF7F2`, style 2D flat vector, hậu tố chặn logo/watermark | `.agents/rules/prompt_rules.md` |
| Kịch bản trước prompt | Phải chốt kịch bản với người dùng rồi mới sinh prompt | `.agents/rules/prompt_rules.md` |
| Khai báo AI | Bật nhãn "altered or synthetic content" trên YouTube Studio | Checklist trong `*_dang_bai.txt` |

## 7. Tiêu chí chấp nhận

- `python make_video.py --new-short <slug>` tạo đủ khung thư mục + file mẫu.
- `build_shorts.py <slug> --dry-run` báo lỗi rõ ràng khi số câu ≠ số media hoặc config thiếu trường.
- `build_shorts.py <slug>` xuất `shorts_vi/<id>.mp4` 1080x1920, có giọng, caption, BGM, thumbnail và file đăng bài.
- `make_video.py <slug>` xuất `<slug>_vi.mp4` (độ phân giải theo media đầu tiên) và `thumbnail_vi.jpg`.
- Bộ test (`tests/` + `test_build_shorts.py`) pass: hiện **25/25**.

## 8. Rủi ro đã biết

Xem chi tiết tại [project-roadmap.md](project-roadmap.md) và báo cáo review `plans/visuals/review-du-an-vat-chanh-cong-nghe-video-pipeline.md`.

- Thời gian phụ đề đang **ước lượng theo số ký tự**, chưa khớp từng từ thật.
- `full_voiceover.mp3` được nối byte MP3 thô.
- Bot Google Flow phụ thuộc giao diện web, dễ gãy khi Flow đổi DOM; cần đối chiếu điều khoản dịch vụ hiện hành của Google.
- Nguồn/license nhạc nền trong `resources/CREDITS.md` còn ô "Cần điền".
