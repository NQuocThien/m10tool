# Tóm tắt mã nguồn (Codebase Summary)

> Python 3.12 · ~4.300 dòng code sản phẩm (không tính `archive/`) · 25 unit test

## 1. Cây thư mục

```text
Video/
├── app.py                  # Studio Tkinter (1150 dòng) — GUI gom mọi thao tác
├── make_video.py           # CLI: tạo dự án, liệt kê, render video dài 16:9 (360 dòng)
├── make_shorts.py          # Thư viện đồ họa + render cảnh Short 9:16 (692 dòng)
├── auto_flow.py            # Bot Playwright đẩy prompt lên Google Flow (341 dòng)
├── run_studio.bat          # Mở Studio với console UTF-8
├── requirements.txt
├── core/                   # Thư viện lõi dùng chung
│   ├── config.py           # Hằng số: đường dẫn, FPS, voice, model TTS, style phụ đề
│   ├── tts.py              # Gemini TTS (batch + fallback) / Edge TTS
│   ├── tts_cache.py        # Cache audio theo hash nội dung câu
│   ├── vi_text.py          # Gom từ ghép cho phụ đề, chuẩn hóa phát âm cho TTS
│   ├── subtitles.py        # SRT video dài, chia caption động Short
│   ├── renderer.py         # Render video dài + thumbnail 16:9
│   ├── sorter.py           # Sắp xếp/đổi tên media theo số cảnh
│   └── motion_25d.py       # Tách lớp parallax 2.5D bằng rembg
├── .agents/
│   ├── rules/prompt_rules.md
│   └── skills/
│       ├── topic-finder/   # Đề xuất chủ đề
│       ├── shorts-maker/   # Skill Short + scripts/build_shorts.py (pipeline V3) + test
│       └── video-maker/    # Skill video dài
├── resources/              # BGM, SFX, intro, logo, brand, từ điển phát âm/từ ghép
├── tests/                  # test_tts_cache.py, test_vi_text.py
├── projects/<slug>/        # Dữ liệu từng video (bị .gitignore)
├── plans/                  # Báo cáo review, kế hoạch
├── docs/                   # Tài liệu (thư mục này)
├── archive/                # Script cũ, không còn dùng (bị .gitignore)
└── user_data/              # Hồ sơ Chrome của bot + cache preview (bị .gitignore)
```

## 2. Entry points

### `make_video.py`

| Hàm | Mô tả |
|---|---|
| `cmd_new_project(name, short_first)` | Tạo khung dự án. Short-first: `video_short_vi/`, `video_vi/`, `script_short_vi.txt`, 2 file prompt 9:16, `shorts_config_vi.json` mẫu. Thường: `imgs/`, `imgs_vi/`, `video_vi/`, `script_vi.txt`, 2 file prompt 16:9 |
| `cmd_list_projects()` | Bảng liệt kê dự án: số media, loại kịch bản, số Short/video dài đã render |
| `get_media_dir(proj_dir)` | Ưu tiên `video_vi` → `imgs_vi-clean` → `imgs_vi` → `video` → `videos` → `imgs-clean` → `imgs` |
| `get_script_path(proj_dir)` | `script_vi.txt`, dự phòng `script.txt` |
| `_extract_thumb_lines_from_youtube_md` | Lấy 2 dòng chữ thumbnail từ mục thumbnail trong `youtube_vi.md` khi không truyền `--thumb-top/--thumb-bottom` |
| `build_video_for_project(...)` | 4 bước: sort media → TTS → SRT → render; sau đó tạo `thumbnail_vi.jpg` |

### `.agents/skills/shorts-maker/scripts/build_shorts.py`

| Hàm | Mô tả |
|---|---|
| `resolve_project_paths` | Xác định chế độ Shorts-first hay Repurpose, trả về dict đường dẫn |
| `load_and_validate_configs` | Kiểm tra `REQUIRED_FIELDS`, số cảnh nằm trong `1..total_scenes` |
| `audit_shorts_retention_risks` | 7 kiểm tra: trùng cảnh mở đầu, mở bằng ảnh tĩnh, 100% ảnh tĩnh, câu mở yếu/không có số, quá dài, nhãn tập, tiêu đề dài/lộ đáp án |
| `format_overlay_badge` | Ghép `main_topic • badge`, tự gỡ `TẬP X/N` |
| `_prepare_punchy_short_audio` | FFmpeg: cắt lặng 2 đầu (-42dB), `atempo=1.18`, EQ +2.5dB @3kHz, pad 0.06s, trộn SFX (whoosh cảnh 1, pop cảnh sau) |
| `render_short_outro_cta_clip` | Thẻ CTA ~1.8s (chỉ khi `--with-outro`) |
| `build_shorts` | Pipeline render cho từng Short trong config |
| `generate_metadata_and_thumbnails` | `<id>_thumb.jpg`, `<id>_dang_bai.txt`, `TONG_HOP_DANG_SHORTS.md` |

### `make_shorts.py` (thư viện được `build_shorts.py` import với tên `ms`)

| Hàm | Mô tả |
|---|---|
| `probe_media_dimensions` | Đọc kích thước media qua FFmpeg |
| `render_hook_banner_png` | Banner Hook 2 dòng + badge |
| `render_caption_strip_png` | Dải caption 3–5 từ, tô màu số liệu/đơn vị/từ khóa (`HIGHLIGHT_UNITS`, `HIGHLIGHT_KEYWORDS`) |
| `create_short_overlay` | Lớp "chrome" khung Short; trả về `box_rect` (full-bleed hoặc hero 1048x740) |
| `_render_short_scene` | Ghép nền + overlay + hook + caption thành 1 clip |
| `render_short_thumbnail` | Thumbnail 9:16 từ cảnh `thumb_scene` |

### `auto_flow.py`

Script chạy cấp module (chưa có `main()`). Tham số vị trí: `prompt_file [wait_min] [wait_max]` (mặc định 25–40s). Bỏ qua dòng rỗng và dòng bắt đầu bằng `#`. Hàm phụ: `find_flow_input`, `click_send_button`, `inject_ready_button`.

### `app.py`

Class `VatChanhStudioApp`; xem [system-architecture.md §7](system-architecture.md#7-studio-apppy). Các nhóm phương thức:

- Dự án: `refresh_projects`, `on_project_selected`, `prompt_new_project`, `sort_project_resources`.
- Âm thanh: `preview_voice_thread`, `preview_bgm_thread`, `preview_mix_thread`, `change_bgm_file`.
- Render: `start_render_thread`, `start_render_shorts_thread`, `stop_render_process`, `update_render_progress_from_line` (parse log để cập nhật % tiến độ).
- Bot: `run_bot_thread`, `on_bot_ready`, `stop_bot`, `append_bot_log`.

## 3. Thư viện lõi `core/`

### `config.py`
Hằng số toàn cục — xem [configuration-reference.md](configuration-reference.md#1-coreconfigpy).

### `tts.py`

| Hàm | Mô tả |
|---|---|
| `load_script(path)` | Đọc kịch bản thành danh sách câu (1 dòng không rỗng = 1 cảnh), tự bỏ tiền tố số `01.`, `1 -`, `01:` |
| `generate_audio(script, audio_dir, voice, force, style)` | API chính. Trả về `[{index, text, audio_path}]`, ghi `NN_voice.mp3`, `full_voiceover.mp3`, `tts_manifest.json` |
| `synthesize_preview(text, out_mp3, voice)` | Tạo 1 câu nghe thử cho Studio |
| `_synthesize_batch_gemini` | Gộp tối đa 5 câu/request, nối bằng `\n\n...\n\n` |
| `_split_wav_by_lines` | Tách WAV gộp thành từng câu tại "thung lũng im lặng" gần ranh giới ước lượng theo độ dài chữ |
| `_call_gemini_tts_with_fallback` | Duyệt `GEMINI_TTS_FALLBACK_MODELS`; 429 → đánh dấu model cạn, chuyển ngay |
| `_synthesize_line_edge` | Edge TTS, retry 8 lần, backoff tuyến tính |

### `tts_cache.py`

| Hàm | Mô tả |
|---|---|
| `line_cache_key(text, voice, style)` | `sha1` 16 ký tự |
| `plan_line(...)` | Trả về `(cần_tạo, lý_do)`: `force` / `missing` / `legacy` / `untracked` / `changed` / `cached` |
| `load_manifest` / `save_manifest` | Đọc/ghi `tts_manifest.json` (ghi qua file `.tmp` rồi `os.replace`) |
| `read_cached_voice(audio_dir)` | Voice đã dùng — để lần render sau giữ nguyên giọng khi không truyền `--voice` |

### `vi_text.py`

| Hàm | Mô tả |
|---|---|
| `group_caption_atoms(words)` | Dính "số + đơn vị" và từ ghép (đọc từ `resources/vi_compound_words.txt`) để không cắt "nhu / cầu" |
| `is_phrase_start(atom)` | Gợi ý điểm ngắt caption tự nhiên |
| `normalize_for_tts(text)` | Thay thuật ngữ/đơn vị theo `resources/pronunciation_vi.json` (vd. `65W` → "65 oát", `OLED` → "ô lét") |

### `subtitles.py`

| Hàm | Mô tả |
|---|---|
| `get_audio_duration` | Đọc thời lượng qua FFmpeg |
| `split_subtitle_chunks(text, max_words=9)` | Chia câu cho SRT video dài |
| `split_short_caption_chunks(text, max_words=4)` | Chia caption Short 3–5 từ |
| `compute_caption_cue_timings(text, duration)` | Phân bổ thời gian theo số ký tự + thưởng 3.5 cho dấu câu |
| `generate_subtitles(audio_items, srt_path)` | Ghi SRT, trả về item kèm `start`, `end`, `duration` |

### `renderer.py`

| Hàm | Mô tả |
|---|---|
| `get_bgm_path` / `get_intro_path` | `resources/bgm_vi.mp3` → `resources/bgm.mp3`; `resources/intro_vi.mp4` → `intro.mp4` |
| `detect_target_resolution` | Theo media đầu tiên: dọc 1080x1920, ngang 1920x1080 (+ style phụ đề tương ứng) |
| `prepare_intro_clip` | Chuẩn hóa intro về cùng độ phân giải/FPS/audio để concat |
| `_render_single_scene` | Render 1 cảnh (video / Ken Burns / 2.5D) |
| `render_project` | Pipeline render đầy đủ, dọn `temp_render/` trong `finally` |
| `render_long_thumbnail` | Thumbnail 16:9 tương phản cao, 2 dòng chữ lớn |

### `sorter.py`

| Hàm | Mô tả |
|---|---|
| `get_sorted_images(dir, auto_prefix=True)` | Sắp xếp tự nhiên; nếu file chưa có tiền tố số thì **đổi tên** thành `01_..`, `02_..` |
| `parse_prompt_scene_numbers(prompt_file)` | Đọc số cảnh từ comment `# Cảnh XX` / `# Scene XX` đứng trước mỗi dòng prompt |
| `sort_media_by_prompts(media_dir, video_prompt, img_prompt, sort_by="mtime")` | Ghép file tải về với số cảnh theo thứ tự thời gian tải; file có tiền tố số không thuộc danh sách (vd. mascot tái sử dụng) được giữ nguyên |

### `motion_25d.py`

`prepare_25d_layers(image, w, h, cache_dir)` → `(fg_png, bg_png)`. Session `rembg` dùng chung (khóa thread), lấp lỗ nền bằng màu pixel gần nhất, kết quả cache trong `cache_25d/`.

## 4. Tài nguyên `resources/`

| File | Dùng ở |
|---|---|
| `bgm_vi.mp3`, `bgm.mp3` | BGM video dài (vol 0.08, fade-out 1.5s) |
| `bgm_shorts.mp3` | BGM Short (vol 0.13, fade-out 1s) |
| `sfx_whoosh.wav`, `sfx_pop.wav` | SFX chuyển cảnh Short |
| `shorts_cta_vi.mp3` | Giọng CTA khi bật outro |
| `intro_vi.mp4` | Intro (mặc định tắt) |
| `pronunciation_vi.json` | Từ điển phát âm cho TTS |
| `vi_compound_words.txt` | Danh sách từ ghép không được cắt |
| `brand_identity_vi.md`, `prompts_brand_vi.txt`, `logo_vi.jpg`, `banner_vi.jpg` | Nhận diện thương hiệu |
| `CREDITS.md` | Nguồn & license từng file |

## 5. Test

| File | Phạm vi |
|---|---|
| `tests/test_tts_cache.py` | Cache theo hash: sửa/chèn câu, đổi voice, manifest hỏng, legacy |
| `tests/test_vi_text.py` | Gom từ ghép, chuẩn hóa phát âm, chia caption |
| `.agents/skills/shorts-maker/scripts/test_build_shorts.py` | Resolve đường dẫn, validate config, audit |

Chạy:

```bash
python -m unittest discover -s tests
python -m unittest discover -s .agents/skills/shorts-maker/scripts -p "test_*.py"
```
