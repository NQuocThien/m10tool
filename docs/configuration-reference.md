# Tham chiếu cấu hình, định dạng file & CLI

## 1. `core/config.py`

| Hằng số | Giá trị mặc định | Ý nghĩa |
|---|---|---|
| `PROJECTS_DIR` / `RESOURCES_DIR` | `<repo>/projects`, `<repo>/resources` | Thư mục dữ liệu |
| `FFMPEG_PATH` | `imageio_ffmpeg.get_ffmpeg_exe()` | Binary FFmpeg dùng cho mọi lệnh |
| `DEFAULT_FPS` | `25` | FPS xuất |
| `DEFAULT_RESOLUTION` | `(1920, 1080)` | Độ phân giải video dài khi không đọc được media |
| `DEFAULT_MAX_ZOOM` | `1.10` | Biên độ Ken Burns (thực tế tối thiểu 1.08) |
| `DEFAULT_BGM_VOLUME` | `0.08` | Âm lượng BGM video dài |
| `SCENE_TAIL_PAD_SEC` | `0.18` | Đệm cuối cảnh |
| `SHORT_MAX_DURATION_SEC` | `38.0` | Trần thời lượng Short dùng trong audit |
| `SHORT_IDEAL_MAX_SCENES` | `7` | Số cảnh tối đa khuyến nghị |
| `SHORT_HOOK_BANNER_SEC` | `3.2` | Thời gian hiện Hook banner |
| `SHORT_WORDS_PER_CAPTION` | `4` | Số từ mục tiêu mỗi caption động |
| `HIGHLIGHT_UNITS`, `HIGHLIGHT_KEYWORDS` | tập từ | Từ được tô màu nhấn trong caption Short |
| `GEMINI_TTS_MODEL` | `gemini-3.8-flash-tts` | Model TTS chính |
| `GEMINI_TTS_FALLBACK_MODELS` | 5 model | Thứ tự thử khi lỗi/hết quota |
| `GEMINI_STYLE_VI` | mô tả giọng | Style dẫn chuyện (chỉ model 3.8 hỗ trợ) |
| `DEFAULT_VOICE` | `gemini:voice_5mxlq1k9luls` | Giọng mặc định của kênh |
| `VOICES_VI` | 8 giọng | Danh sách hiển thị trong Studio |
| `DEFAULT_SUB_STYLE` | Segoe UI 16, viền đen | Style ASS khi burn phụ đề video dài |
| `OUTRO_SCRIPT_VI` | slogan + CTA | Câu outro |

### Định dạng voice ID

| Dạng | Engine | Ví dụ |
|---|---|---|
| `gemini:<VoiceName>` | Gemini TTS | `gemini:Charon`, `gemini:vi-vn-advisor-2` |
| `<locale>-<Name>Neural` | Edge TTS | `vi-VN-NamMinhNeural` |

## 2. Biến môi trường

| Biến | Bắt buộc | Mô tả |
|---|---|---|
| `GEMINI_API_KEY` (hoặc `GOOGLE_API_KEY`) | Có, nếu dùng giọng `gemini:` | SDK `google-genai` tự đọc khi tạo `genai.Client()` |
| `PYTHONIOENCODING=utf-8` | Khuyến nghị | `run_studio.bat` đã đặt sẵn |

> Repo **không** tự nạp file `.env`. Đặt biến ở môi trường Windows (System Properties → Environment Variables) hoặc trong phiên PowerShell trước khi chạy.

## 3. Cấu trúc thư mục dự án `projects/<slug>/`

| File / thư mục | Giai đoạn | Tạo bởi | Nội dung |
|---|---|---|---|
| `script_short_vi.txt` | 1 | Agent / người dùng | 6–7 câu, mỗi dòng 1 cảnh, dạng `01. Nội dung câu` |
| `prompts_short_vi_video.txt` | 1 | Agent | Prompt `[VIDEO]` dọc `--ar 9:16` |
| `prompts_short_vi_img.txt` | 1 | Agent | Prompt `[IMG]` dọc `--ar 9:16` |
| `video_short_vi/` | 1 | Người dùng | Media 9:16 đánh số `01_..06_` |
| `audio_short_vi/` | 1 | `build_shorts.py` | `NN_voice.mp3`, `full_voiceover.mp3`, `tts_manifest.json` |
| `shorts_config_vi.json` | 1 | Agent | Cấu hình Short (xem §4) |
| `shorts_vi/` | 1 | `build_shorts.py` | `<id>.mp4`, `<id>_thumb.jpg`, `<id>_script.txt`, `<id>_dang_bai.txt`, `TONG_HOP_DANG_SHORTS.md` |
| `script_vi.txt` | 2 | Agent | 24–28 câu |
| `prompts_vi_video.txt`, `prompts_vi_img.txt` | 2 | Agent | Prompt `--ar 16:9` |
| `video_vi/` (hoặc `imgs_vi/`, `imgs/`) | 2 | Người dùng | Media 16:9 đánh số |
| `audio_vi/` | 2 | `make_video.py` | Audio video dài |
| `subtitles_vi.srt` | 2 | `make_video.py` | Phụ đề |
| `<slug>_vi.mp4` | 2 | `make_video.py` | Video dài |
| `thumbnail_vi.jpg` | 2 | `make_video.py` | Thumbnail 16:9 |
| `youtube_vi.md` | 2 | Agent | Tiêu đề, mô tả, tags, gợi ý thumbnail |

**Quy tắc vàng:** số dòng kịch bản phải **bằng** số file media; file media thứ N khớp câu thứ N.

### Định dạng file prompt

```text
# Cảnh 01 [VIDEO]: mô tả ngắn (comment, bot bỏ qua)
<prompt tiếng Anh một dòng> --ar 9:16
# Cảnh 03 [VIDEO]: ...
<prompt>
```

Comment `# Cảnh XX` / `# Scene XX` ngay trước dòng prompt là căn cứ để **Sort Resource** đổi tên file tải về thành `XX_<tên gốc>`.

## 4. `shorts_config_vi.json`

Mảng JSON gồm 1 Short (chế độ Shorts-first) hoặc 1–2 Short (chế độ cắt từ video dài).

| Trường | Bắt buộc | Ràng buộc |
|---|---|---|
| `id` | ✔ | Slug tên file, vd. `short_01_gan_charger_trap` |
| `main_topic` | | 14–28 ký tự, không chứa `TẬP x/y` |
| `badge` | ✔ | 12–24 ký tự, vd. `BÓC MẼ PHẦN CỨNG` |
| `title_line1` | ✔ | Hook dòng 1, 16–26 ký tự |
| `title_line2` | ✔ | Hook dòng 2, 20–38 ký tự |
| `accent_color` | ✔ | `#D35400`, `#F4C430` hoặc `#7CB342` |
| `scenes` | ✔ | 5–7 số nguyên (đánh số từ 1); `scenes[0]` nên là `.mp4` |
| `thumb_scene` | ✔ | Cảnh dùng làm thumbnail |
| `thumb_big_text` | ✔ | 2 dòng ngăn bởi `\n`, viết hoa, 2–4 từ/dòng |
| `thumb_sub_badge` | ✔ | Thường là `VẮT CHANH CÔNG NGHỆ` |
| `skip_outro` | | `true` (mặc định — Seamless Loop) |
| `has_related_video` | | `true` khi đã có video dài để trỏ tới |
| `yt_titles` | ✔ | 3 tiêu đề < 65 ký tự + `#shorts` |
| `yt_description` | ✔ | Mô tả + hashtag |
| `yt_pinned_comment` | ✔ | Bình luận ghim kích thích tương tác |
| `thumb_desc` | ✔ | Mô tả bố cục thumbnail |
| `thumb_prompt` | ✔ | Prompt ảnh AI `--ar 9:16` |

Ví dụ rút gọn:

```json
[
  {
    "id": "short_01_gan_charger_trap",
    "main_topic": "SẠC NHANH GIÁ RẺ",
    "badge": "BÓC MẼ PHẦN CỨNG",
    "title_line1": "BẪY SẠC NHANH GIÁ RẺ!",
    "title_line2": "Kiểm Tra Ngay Trước Khi Phồng Pin",
    "accent_color": "#D35400",
    "scenes": [1, 2, 3, 4, 5, 6],
    "thumb_scene": 1,
    "thumb_big_text": "BÁO SẠC SIÊU NHANH\nNHƯNG NƯỚNG PHỒNG PIN?!",
    "thumb_sub_badge": "VẮT CHANH CÔNG NGHỆ",
    "skip_outro": true,
    "has_related_video": false,
    "yt_titles": ["...", "...", "..."],
    "yt_description": "...",
    "yt_pinned_comment": "...",
    "thumb_desc": "...",
    "thumb_prompt": "... --ar 9:16"
  }
]
```

## 5. File dữ liệu chỉnh được không cần sửa code

### `resources/pronunciation_vi.json`

```json
{
  "terms": { "OLED": "ô lét", "TDS": "T D S" },
  "units": { "W": "oát", "mAh": "mi li am pe giờ", "%": "phần trăm" }
}
```

`terms` thay thuật ngữ, `units` thay đơn vị đứng sau số. Chỉ ảnh hưởng **giọng đọc**; phụ đề giữ nguyên chữ gốc. Sửa xong, các câu bị ảnh hưởng sẽ tự tạo lại audio (hash thay đổi).

### `resources/vi_compound_words.txt`

Mỗi dòng 1 cụm từ không được cắt đôi khi chia caption; dòng bắt đầu bằng `#` là ghi chú.

### `app_settings.json`

Trạng thái Studio: `last_project`, `last_voice_idx`, `last_prompt_file`, `bot_wait_min`, `bot_wait_max`… Tự sinh, có thể xóa an toàn.

## 6. CLI

### `make_video.py`

```bash
python make_video.py --list                         # Liệt kê dự án
python make_video.py --new-short <slug>             # Tạo dự án Short-first 9:16
python make_video.py --new <slug> [--short-first]   # Tạo dự án video dài
python make_video.py <slug> [tùy chọn]              # Render video dài 16:9
```

| Tùy chọn | Mô tả |
|---|---|
| `--voice ID` | Giọng TTS (mặc định: giọng đã cache của dự án, rồi tới `DEFAULT_VOICE`) |
| `--media-dir PATH` | Thư mục media tùy chọn |
| `--force` | Tạo lại toàn bộ audio và thumbnail |
| `--with-intro` | Ghép intro vào đầu (mặc định tắt) |
| `--25d` / `--no-25d` | Bật/tắt parallax 2.5D cho ảnh tĩnh (mặc định tắt) |
| `--thumb-top TEXT`, `--thumb-bottom TEXT` | 2 dòng chữ thumbnail |
| `--lang vi` | Giữ để tương thích, chỉ nhận `vi` |

### `build_shorts.py`

```bash
python .agents/skills/shorts-maker/scripts/build_shorts.py <slug> [tùy chọn]
```

| Tùy chọn | Mô tả |
|---|---|
| `--dry-run` | Chỉ validate + audit, không render |
| `--meta-only` | Chỉ tạo thumbnail và file đăng bài |
| `--with-outro` | Thêm thẻ CTA ~1.8s (tắt Seamless Loop) |
| `--voice ID` | Giọng TTS |
| `--force-tts` | Tạo lại toàn bộ audio |
| `--media-dir`, `--audio-dir` | Ghi đè thư mục (tương đối theo dự án hoặc tuyệt đối) |
| `--lang vi` | Giữ để tương thích |

### `auto_flow.py`

```bash
python auto_flow.py <file_prompt> [wait_min] [wait_max]
# Video: 45 65 giây; ảnh: 15 25 giây (gợi ý trong WORKFLOW.md)
```
