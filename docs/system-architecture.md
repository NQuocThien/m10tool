# Kiến trúc hệ thống

## 1. Bức tranh tổng thể

Hệ thống là một pipeline **file-based**: mọi bước đọc/ghi file trong `projects/<slug>/`. Không có database, không có server. Mỗi entry point là một script Python độc lập; Studio (`app.py`) chỉ gọi lại các script đó bằng `subprocess`.

```mermaid
flowchart LR
    subgraph Agent["AI agent (.agents/)"]
        TF["topic-finder"]
        SM["shorts-maker"]
        VM["video-maker"]
        RULE["rules/prompt_rules.md"]
    end

    subgraph Entry["Entry points"]
        APP["app.py (Studio Tkinter)"]
        MV["make_video.py (video dài 16:9)"]
        BS["build_shorts.py (Short 9:16)"]
        AF["auto_flow.py (bot Google Flow)"]
    end

    subgraph Core["core/"]
        CFG["config.py"]
        TTS["tts.py"]
        CACHE["tts_cache.py"]
        VI["vi_text.py"]
        SUB["subtitles.py"]
        REN["renderer.py"]
        SORT["sorter.py"]
        M25["motion_25d.py"]
    end

    MS["make_shorts.py (đồ họa Short)"]
    EXT1[("Gemini TTS API")]
    EXT2[("Edge TTS")]
    EXT3[("Google Flow web")]
    FF[["FFmpeg (imageio-ffmpeg)"]]

    Agent -->|"script, prompts, shorts_config"| Entry
    APP -->|subprocess| MV
    APP -->|subprocess| BS
    APP -->|subprocess| AF
    APP --> SORT
    MV --> TTS
    MV --> SUB
    MV --> REN
    BS --> TTS
    BS --> SUB
    BS --> MS
    MS --> SUB
    TTS --> CACHE
    TTS --> VI
    SUB --> VI
    REN --> M25
    TTS --> EXT1
    TTS --> EXT2
    AF --> EXT3
    REN --> FF
    MS --> FF
    BS --> FF
```

## 2. Luồng nghiệp vụ 2 giai đoạn

```mermaid
flowchart TD
    A["/topic-finder: chọn 1 trong 5 chủ đề"] --> B["make_video.py --new-short slug"]
    B --> C["Agent viết script_short_vi.txt (6-7 câu) - người dùng duyệt"]
    C --> D["Agent sinh prompts_short_vi_*.txt + shorts_config_vi.json"]
    D --> E["auto_flow.py đẩy prompt lên Google Flow"]
    E --> F["Tải media về video_short_vi/, Sort Resource"]
    F --> G["build_shorts.py --dry-run (audit)"]
    G --> H["build_shorts.py (render Short + thumbnail + dang_bai)"]
    H --> I{"Sau 48h: > 2.000 views và APV > 75%?"}
    I -- Không --> A
    I -- Có --> J["/video-maker: script_vi.txt 24-28 câu + prompts 16:9"]
    J --> K["Media vào video_vi/"]
    K --> L["make_video.py slug (video dài + thumbnail_vi.jpg)"]
    L --> M["Đăng video dài, gắn Related Video từ Short"]
```

## 3. Pipeline video dài (`make_video.py`)

```mermaid
sequenceDiagram
    participant U as Người dùng / Studio
    participant MV as make_video.py
    participant SO as core.sorter
    participant T as core.tts
    participant S as core.subtitles
    participant R as core.renderer
    participant F as FFmpeg

    U->>MV: make_video.py slug [--voice --force --25d --with-intro]
    MV->>SO: get_sorted_images(media_dir)
    SO-->>MV: danh sách media (tự thêm tiền tố 01_ nếu thiếu)
    MV->>T: generate_audio(script_vi.txt, audio_vi/)
    T-->>MV: [{index, text, audio_path}]
    MV->>MV: kiểm tra số media == số câu
    MV->>S: generate_subtitles(audio_items, subtitles_vi.srt)
    S-->>MV: items + start/end/duration
    MV->>R: render_project(media, items, srt, out.mp4)
    R->>F: render từng cảnh song song (<=4 luồng)
    R->>F: concat, burn phụ đề, mix BGM, (ghép intro)
    R-->>MV: slug_vi.mp4
    MV->>R: render_long_thumbnail(media[0]) -> thumbnail_vi.jpg
```

Chi tiết render từng cảnh (`_render_single_scene`):

| Loại media | Xử lý |
|---|---|
| Video (`.mp4/.mov/.webm/...`) | Scale + crop về khung đích, lặp (`-stream_loop -1`) và cắt đúng thời lượng câu thoại |
| Ảnh, tắt 2.5D (mặc định) | Ken Burns: zoom vào/ra xen kẽ tối thiểu 8%, kèm trôi ngang nhẹ |
| Ảnh, bật `--25d` | `rembg` tách tiền cảnh, lấp lỗ nền (`distance_transform_edt`), 2 lớp zoompan lệch nhau tạo parallax |

Độ phân giải đích lấy từ **media đầu tiên**: ảnh dọc → 1080x1920, còn lại → 1920x1080. FPS 25.

## 4. Pipeline Short 9:16 (`build_shorts.py`)

```mermaid
flowchart TD
    P["resolve_project_paths: chọn script/media/audio theo chế độ"] --> V["load_and_validate_configs + kiểm tra số câu == số media"]
    V --> AU["audit_shorts_retention_risks: in cảnh báo"]
    AU --> DR{"--dry-run?"}
    DR -- Có --> END1["In tóm tắt cảnh mở đầu, dừng"]
    DR -- Không --> TTS["generate_audio (đồng bộ cache)"]
    TTS --> LOOP["Với mỗi Short trong config"]
    LOOP --> PA["_prepare_punchy_short_audio: cắt lặng, x1.18, EQ 3kHz, SFX"]
    PA --> SR["generate_subtitles (tính thời lượng)"]
    SR --> HB["render_hook_banner_png (3.2s đầu)"]
    HB --> SC["_render_short_scene song song: nền + overlay + hook + caption động"]
    SC --> CC["concat + (outro CTA nếu --with-outro)"]
    CC --> BG["mix bgm_shorts.mp3 (vol 0.13)"]
    BG --> META["generate_metadata_and_thumbnails"]
```

Bố cục khung 1080x1920:

| Nguồn media | Bố cục |
|---|---|
| Dọc (cao > rộng) | **Full-bleed** 1080x1920 |
| Ngang | Nền mờ (`boxblur`) phủ lớp kem `#FAF7F2` 76% + khung hero `1048x740` |
| Hook banner | Overlay tại `y=152`, chỉ hiện `0..3.2s` cảnh 1 |
| Caption động | PNG 3–5 từ, overlay tại `y=1205`, thời điểm theo `compute_caption_cue_timings` |

Chọn chế độ trong `resolve_project_paths`:

- Có `script_short_vi.txt` và config không tham chiếu cảnh vượt số câu → **Shorts-first**: media `video_short_vi/`, audio `audio_short_vi/`.
- Ngược lại → **Repurpose 16:9 → 9:16**: dùng `script_vi.txt`, `video_vi/`, `audio_vi/`.

## 5. Hệ thống TTS

```mermaid
flowchart TD
    L["load_script: danh sách câu"] --> N["normalize_for_tts: 65W -> sáu lăm oát, LFP -> ..."]
    N --> K["line_cache_key = sha1(voice | style | text)"]
    K --> PL{"plan_line"}
    PL -- "cached / legacy" --> USE["Dùng lại NN_voice.mp3"]
    PL -- "missing / changed / force" --> PEND["Danh sách cần tạo"]
    PEND --> G{"voice bắt đầu bằng gemini:?"}
    G -- Có --> B["Gộp 5 câu/request"]
    B --> FB["_call_gemini_tts_with_fallback: thử lần lượt GEMINI_TTS_FALLBACK_MODELS"]
    FB --> SPL["_split_wav_by_lines: cắt WAV tại khoảng lặng gần ranh giới dự kiến"]
    SPL -- lỗi --> ONE["Tạo từng câu"]
    G -- Không --> EDGE["Edge TTS từng câu, retry 8 lần"]
    SPL --> MP3["WAV -> MP3"]
    ONE --> MP3
    EDGE --> MAN
    MP3 --> MAN["save_manifest (atomic) tts_manifest.json"]
    USE --> MAN
    MAN --> FULL["full_voiceover.mp3"]
```

Điểm chính:

- Phụ đề giữ **nguyên văn kịch bản**; chỉ phần đọc được chuẩn hóa phát âm.
- Model không thuộc dòng 3.8 không hỗ trợ voice tùy biến và `speech_metadata` → tự đổi sang voice `Charon`.
- Client Gemini đặt `retry attempts=1` để không bị treo nhiều giờ theo header `Retry-After` khi gặp 429.

## 6. Bot Google Flow (`auto_flow.py`)

```mermaid
sequenceDiagram
    participant S as Studio
    participant B as auto_flow.py
    participant C as Chrome (user_data/)
    S->>B: python auto_flow.py prompts.txt min max
    B->>C: launch_persistent_context(channel=chrome, headless=False)
    B->>C: mở flow.google, chờ ô nhập prompt (tối đa 300s)
    B-->>S: STATE:WAITING_READY
    S->>B: tạo file cờ .bot_ready (hoặc bấm nút xanh trong Chrome)
    loop từng prompt
        B->>C: điền prompt + Send
        B-->>S: PROGRESS:i/total
        B->>B: chờ ngẫu nhiên min..max giây
    end
    B->>C: giữ trình duyệt mở 60s để tải về
```

Giao tiếp Studio ↔ bot qua **stdout** (`STATE:`, `PROGRESS:`) và **file cờ** `.bot_ready` ở thư mục gốc.

## 7. Studio (`app.py`)

Class `VatChanhStudioApp` (Tkinter, theme tối) gồm 2 tab:

| Tab | Chức năng | Gọi tới |
|---|---|---|
| 🎬 Dựng Video | Chọn/tạo dự án, chọn giọng + nghe thử, nghe BGM/mix, đổi BGM, mở media/kịch bản, Sort Resource, dựng Short, dựng video dài, hủy render, thanh tiến độ | `build_shorts.py`, `make_video.py`, `core.sorter`, `core.tts.synthesize_preview` |
| 🌐 Bot Google Flow | Chọn file prompt, khoảng chờ, khởi động / sẵn sàng / dừng bot, log chi tiết | `auto_flow.py` |

Trạng thái giao diện (dự án cuối, giọng, khoảng chờ…) lưu tại `app_settings.json` (bị `.gitignore`). Cache nghe thử giọng nằm ở `user_data/preview_cache/`.

## 8. Phụ thuộc ngoài

| Phụ thuộc | Vai trò | Ghi chú |
|---|---|---|
| `google-genai` | Gemini TTS qua Interactions API | Cần biến môi trường API key |
| `edge-tts` | TTS dự phòng (voice `*-Neural`) | Không cần key |
| `imageio-ffmpeg` | Binary FFmpeg đi kèm | Không cần cài FFmpeg hệ thống |
| `Pillow` | Vẽ overlay, banner, caption, thumbnail | Font Segoe UI (Windows) |
| `rembg[cpu]` + `scipy` + `numpy` | Tách nền 2.5D | Tải model ONNX lần đầu |
| `playwright` | Điều khiển Chrome cho bot Flow | Cần Google Chrome đã cài |
| `tkinter`, `winsound` | Studio | Chỉ chạy trên Windows |
