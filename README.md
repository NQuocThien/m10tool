# Vắt Chanh Công Nghệ (VI) — V3 Shorts-First & Dual-Aspect Video Pipeline

> **Định vị kênh**: *"Vắt sạch thông số, giữ lại cách dùng"* — Trục nội dung: **Điện • Di động • Sạc nhanh • Xe điện • Wi-Fi**.

Công cụ Python chạy trên Windows biến **kịch bản tiếng Việt + ảnh/video AI** thành **YouTube Short 9:16** và **video dài 16:9** hoàn chỉnh: giọng đọc AI, phụ đề, nhạc nền, thumbnail và nội dung đăng bài.

---

## Điểm cốt lõi của Flow V3

1. **Shorts-First dò đường**: mỗi ngày 1 Short `9:16` độc lập (`24–34s`, 6–7 câu). Chủ đề nào vượt `2.000 views` và `APV > 75%` sau 48h mới mở rộng thành video dài `16:9` (`3.5–4.2 phút`).
2. **Engine render Short (`build_shorts.py` + `make_shorts.py`)**:
   - Nguồn dọc `9:16`: full-bleed `1080x1920`.
   - Nguồn ngang `16:9`: nền mờ chuyển động + khung hero `1048x740`.
   - Banner Hook 3.2s đầu + caption động `3–5 từ/nhịp` tô màu số liệu + Seamless Loop mặc định.
   - Audit rủi ro tụt view trước khi render (`--dry-run`).
3. **Video dài (`make_video.py` + `core/renderer.py`)**: vào thẳng Hook ở `00:00` (tắt intro mặc định), Ken Burns hoặc parallax 2.5D, tự xuất thumbnail 16:9 tương phản cao.
4. **TTS thông minh**: Gemini TTS gộp 5 câu/request, tự chuyển model khi hết quota, dự phòng Edge TTS; cache theo nội dung câu — sửa câu nào chỉ tạo lại câu đó.

---

## Cài đặt nhanh

Yêu cầu: Windows 10/11, Python 3.12, Google Chrome, Gemini API key.

```powershell
pip install -r requirements.txt
pip install numpy scipy
python -m playwright install chrome
setx GEMINI_API_KEY "<khóa của bạn>"
```

Chi tiết: [docs/deployment-guide.md](docs/deployment-guide.md).

---

## Lệnh khởi chạy nhanh

```bash
# 1. Tạo dự án Short 9:16 dò đường (6-7 câu, 24-34s)
python make_video.py --new-short <project_slug>

# 2. Đẩy prompt lên Google Flow (tùy chọn), tải media vào video_short_vi/
python auto_flow.py projects/<project_slug>/prompts_short_vi_video.txt 45 65

# 3. Kiểm duyệt retention & render Short 9:16 (tự tạo TTS nếu chưa có)
python .agents/skills/shorts-maker/scripts/build_shorts.py <project_slug> --lang vi --dry-run
python .agents/skills/shorts-maker/scripts/build_shorts.py <project_slug> --lang vi

# 4. Render video dài 16:9 + thumbnail (khi chủ đề thắng view)
python make_video.py <project_slug> --lang vi --thumb-top "BẪY SẠC 65W 150K" --thumb-bottom "NƯỚNG PHỒNG PIN?!"

# Hoặc mở giao diện Studio tất-cả-trong-một
run_studio.bat
```

---

## Tài liệu

| Tài liệu | Nội dung |
|---|---|
| [WORKFLOW.md](WORKFLOW.md) | Quy trình vận hành kênh từng bước (2 giai đoạn) |
| [HUONG_DAN_SU_DUNG.md](HUONG_DAN_SU_DUNG.md) | Hướng dẫn nhanh trên giao diện Studio |
| [docs/project-overview-pdr.md](docs/project-overview-pdr.md) | Mục tiêu, phạm vi, yêu cầu, quy tắc nội dung |
| [docs/system-architecture.md](docs/system-architecture.md) | Kiến trúc, sơ đồ luồng TTS / render / bot |
| [docs/codebase-summary.md](docs/codebase-summary.md) | Mô tả từng module và hàm chính |
| [docs/configuration-reference.md](docs/configuration-reference.md) | `config.py`, cấu trúc dự án, `shorts_config_vi.json`, CLI |
| [docs/deployment-guide.md](docs/deployment-guide.md) | Cài đặt, API key, lần chạy đầu |
| [docs/code-standards.md](docs/code-standards.md) | Quy chuẩn code, FFmpeg, test, nội dung agent |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Xử lý sự cố thường gặp |
| [docs/project-roadmap.md](docs/project-roadmap.md) | Việc đã xong và lộ trình tiếp theo |

---

## Cấu trúc repo

```text
app.py              Studio Tkinter (render + bot Flow)
make_video.py       Tạo dự án, render video dài 16:9
make_shorts.py      Đồ họa & render cảnh Short 9:16
auto_flow.py        Bot Playwright đẩy prompt lên Google Flow
core/               TTS, cache, phụ đề, renderer, sorter, 2.5D, cấu hình
.agents/            Skill AI (topic-finder, shorts-maker, video-maker) + rules
resources/          BGM, SFX, brand, từ điển phát âm, từ ghép
tests/              Unit test
projects/<slug>/    Dữ liệu từng video (không commit)
docs/               Tài liệu
```

## Test

```bash
python -m unittest discover -s tests
python -m unittest discover -s .agents/skills/shorts-maker/scripts -p "test_*.py"
```

> Khi đăng video: bật nhãn **nội dung bị thay đổi hoặc tổng hợp** (altered or synthetic content) trong YouTube Studio vì hình ảnh/giọng đọc do AI tạo *(đối chiếu chính sách hiện hành của YouTube)*.
