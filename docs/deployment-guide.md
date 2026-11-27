# Hướng dẫn cài đặt & thiết lập môi trường

Công cụ chạy cục bộ trên máy cá nhân, không có bước deploy lên server.

## 1. Yêu cầu hệ thống

| Thành phần | Yêu cầu |
|---|---|
| Hệ điều hành | **Windows 10/11** (Studio dùng `winsound`, font Segoe UI, file `.bat`) |
| Python | 3.12 (đang dùng 3.12.5), có kèm `tkinter` |
| Trình duyệt | Google Chrome (bắt buộc cho bot Google Flow) |
| CPU / RAM | Render dùng tối đa 4 luồng FFmpeg; bật 2.5D cần thêm RAM cho model ONNX |
| Ổ đĩa | Mỗi dự án vài trăm MB (media + audio + video xuất) |
| Tài khoản | Gemini API key (cho giọng `gemini:`), tài khoản Google truy cập Flow |

FFmpeg **không cần cài riêng** — dùng binary đi kèm gói `imageio-ffmpeg`.

## 2. Cài đặt

```powershell
cd C:\Workspace2\Video

# (Khuyến nghị) môi trường ảo
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install numpy scipy        # dùng trực tiếp trong core/tts.py và core/motion_25d.py

# Trình duyệt cho Playwright (bot dùng channel="chrome" nên cần Chrome đã cài sẵn)
python -m playwright install chrome
```

> `requirements.txt` hiện chưa khai báo `numpy` và `scipy`; chúng thường được kéo theo qua `rembg`, nhưng nên cài tường minh như trên.

## 3. Cấu hình API key

```powershell
# Phiên hiện tại
$env:GEMINI_API_KEY = "<khóa của bạn>"

# Lưu vĩnh viễn cho user (mở terminal mới để có hiệu lực)
setx GEMINI_API_KEY "<khóa của bạn>"
```

> ⚠️ Không commit API key. `.gitignore` đã chặn `.env`, nhưng code không tự đọc `.env` — hãy dùng biến môi trường.

Không có key vẫn chạy được nếu chọn giọng Edge TTS (`vi-VN-NamMinhNeural`, `vi-VN-HoaiMyNeural`).

## 4. Lần chạy đầu tiên

1. **Kiểm tra test**:
   ```powershell
   python -m unittest discover -s tests
   python -m unittest discover -s .agents/skills/shorts-maker/scripts -p "test_*.py"
   ```
2. **Mở Studio**: nhấp đúp `run_studio.bat` (đặt code page 65001 + `PYTHONIOENCODING=utf-8`).
3. **Bot Google Flow lần đầu**: Chrome mở với hồ sơ riêng `user_data/` → đăng nhập Google thủ công 1 lần; các lần sau giữ phiên đăng nhập.
4. **Tách nền 2.5D lần đầu** (`--25d`): `rembg` tải model ONNX về thư mục người dùng — cần mạng, mất vài phút.

## 5. Tài nguyên cần có trong `resources/`

| File | Bắt buộc | Khi thiếu |
|---|---|---|
| `bgm_vi.mp3` hoặc `bgm.mp3` | Không | Video dài không có nhạc nền |
| `bgm_shorts.mp3` | Không | Short dùng BGM video dài (vol 0.08) |
| `sfx_whoosh.wav`, `sfx_pop.wav` | Không | Short không có SFX chuyển cảnh |
| `intro_vi.mp4` | Không | Bỏ qua `--with-intro` |
| `pronunciation_vi.json`, `vi_compound_words.txt` | Nên có | Không chuẩn hóa phát âm / có thể cắt sai từ ghép |

Khi thêm hoặc đổi file nhạc/âm thanh, cập nhật `resources/CREDITS.md`.

## 6. Dữ liệu không nằm trong git

`.gitignore` loại trừ: `projects/`, `user_data/`, `app_settings.json`, `archive/`, `temp_render/`, `*.log`, `.env`, `__pycache__/`.

→ **Tự sao lưu** `projects/` (kịch bản, media, video) và `resources/` ra ổ khác hoặc cloud.

## 7. Cập nhật

```powershell
git pull
pip install -r requirements.txt --upgrade
python -m unittest discover -s tests
```

Danh sách model trong `GEMINI_TTS_FALLBACK_MODELS` (`core/config.py`) nên được rà định kỳ, bỏ model đã ngừng hoạt động.
