# Quy chuẩn mã nguồn

Ghi lại quy ước **đang áp dụng** trong repo và quy ước **nên theo** khi thêm code mới.

## 1. Tổ chức code

| Quy tắc | Giải thích |
|---|---|
| Logic dùng chung đặt trong `core/` | Entry point (`make_video.py`, `build_shorts.py`, `app.py`) chỉ điều phối, không chứa thuật toán xử lý |
| Dữ liệu tách khỏi code | Cấu hình Short → `shorts_config_vi.json`; phát âm → `resources/pronunciation_vi.json`; từ ghép → `resources/vi_compound_words.txt` |
| Hằng số tập trung ở `core/config.py` | Không hardcode đường dẫn, FPS, voice, model ở nơi khác |
| Module mới nhỏ, một trách nhiệm | Mẫu tham khảo: `tts_cache.py` (90 dòng), `vi_text.py` (125 dòng) |
| Hàm < 100 dòng, file < 400 dòng | Mục tiêu cho code mới; `app.py`, `make_shorts.py` hiện vượt — không làm chúng phình thêm |
| Chỉ hỗ trợ tiếng Việt | Không thêm cặp hàm `_vi/_en`; nếu cần đa ngôn ngữ, dùng tham số `lang` |

## 2. Đặt tên

| Đối tượng | Quy ước | Ví dụ |
|---|---|---|
| Module, hàm, biến | `snake_case` | `generate_audio`, `audio_dir` |
| Hằng số | `UPPER_SNAKE_CASE` | `SHORT_HOOK_BANNER_SEC` |
| Class | `PascalCase` | `VatChanhStudioApp` |
| Hàm nội bộ | Tiền tố `_` | `_render_single_scene` |
| Slug dự án | `snake_case` tiếng Anh không dấu | `waterproof_ip67_truth` |
| File theo ngôn ngữ | Hậu tố `_vi` | `script_vi.txt`, `shorts_vi/` |
| Media | Tiền tố số 2 chữ số | `01_hook.mp4`, `02_cutaway.png` |
| Audio | `NN_voice.mp3` | `03_voice.mp3` |

## 3. Encoding & Windows

- Luôn mở file văn bản với `encoding="utf-8"`.
- Gọi `subprocess.run(..., text=True, encoding="utf-8", errors="ignore")` để log FFmpeg không làm crash.
- Đường dẫn trong file concat của FFmpeg: đổi `\` thành `/`.
- Đường dẫn SRT trong filter `subtitles=`: thoát dấu `:` (`replace(":", "\\:")`).
- `import core` đã tự ép console sang UTF-8 (`core/__init__.py`).

## 4. FFmpeg

- Luôn dùng `FFMPEG_PATH` từ `core.config`, không gọi `ffmpeg` hệ thống.
- Audio đầu ra thống nhất: `aac 192k, 48000 Hz, stereo` (video) hoặc `libmp3lame 192k` (mp3) — để concat `-c copy` không lỗi.
- Video trung gian: `libx264 -preset ultrafast -crf 19`; bước cuối: `veryfast`, CRF 20–21; `format=yuv420p`.
- Kiểm tra `returncode`, ném `RuntimeError` kèm ~300 ký tự cuối của `stderr`.
- File tạm đặt trong `temp_render/` hoặc `_temp_<id>/` và xóa trong khối `finally`.

## 5. Xử lý lỗi & log

**Đang dùng:** `print(..., flush=True)` với tiền tố `[OK]`, `[WARN]`, `[ERROR]`, `[DONE]`. Studio parse các dòng log này để cập nhật tiến độ, nên **giữ định dạng** khi sửa.

Quy tắc cho code mới:

- Không viết `except Exception: pass` cho việc đọc config/settings — tối thiểu in `[WARN]` kèm tên file.
- Dọn file tạm: bắt `OSError` cụ thể.
- Lỗi đầu vào của người dùng (thiếu file, sai số cảnh) → thông báo rõ cách sửa rồi `sys.exit(1)` hoặc `raise ValueError`.
- Giao thức stdout với Studio: `STATE:<TÊN>` và `PROGRESS:<i>/<total>` — không đổi nếu không sửa cả `app.py`.

## 6. Cache & tính tái lập

- Mọi thao tác tốn API phải có cache theo **nội dung**, không theo số thứ tự (xem `tts_cache.py`).
- Ghi file trạng thái theo kiểu atomic: ghi `.tmp` rồi `os.replace`.
- Không xóa output người dùng khi chưa tạo xong output mới.

## 7. Test

- Framework: `unittest` (chưa dùng `pytest`).
- Test đặt trong `tests/`, tên `test_<module>.py`; test không được gọi API thật — mock lớp gọi TTS.
- Ưu tiên test hàm thuần: chia caption, cache, sorter, định dạng thời gian SRT.
- Sửa bug → thêm test hồi quy tái hiện bug đó.

```bash
python -m unittest discover -s tests
```

## 8. Quy chuẩn nội dung cho agent

Bắt buộc với mọi agent sinh kịch bản/prompt — chi tiết ở `.agents/rules/prompt_rules.md` và `resources/brand_identity_vi.md`:

1. Chốt kịch bản với người dùng **trước** khi sinh prompt.
2. Prompt hình ảnh viết tiếng Anh; nền `on a warm cream background (#FAF7F2)`; style `2D flat vector modern editorial tech infographic`; bảng màu `#F4C430`, `#D35400`, `#7CB342`, viền `#1C1917`.
3. Prompt luôn kèm hậu tố chặn chữ/logo/watermark.
4. Không gắn nhãn `Tập x/y` cho Short; tiêu đề không lộ đáp án.

## 9. Commit

Dùng Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`. Không commit `projects/`, `user_data/`, API key hoặc file nhạc chưa rõ license.
