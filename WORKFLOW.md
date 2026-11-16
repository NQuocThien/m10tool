# QUY TRÌNH CHUẨN SẢN XUẤT VIDEO DÀI & SHORTS (2 KÊNH VI / EN)

Hệ sinh thái 2 kênh:
- **Tiếng Việt (`Vắt Chanh Công Nghệ`)**: *“Vắt sạch thông số, giữ lại cách dùng”* — Nền vàng kem ấm `#FAF7F2`, vàng chanh `#F4C430`, cam đất `#D35400`, xanh lá mầm `#7CB342`, nét nâu than `#1C1917`.
- **Tiếng Anh (`Squeezing Tech`)**: *“Extracting Value from Everyday Tech”* — Nền xanh đen `#0B132B`, xanh neon `#76FF03`, xanh cyan `#00E5FF`, vàng hổ phách `#FFB300`.

---

## Cấu Trúc Thư Mục 1 Dự Án (`projects/<ten_project>/`)

```text
projects/<ten_project>/
├── script_vi.txt           # Kịch bản dài kênh Việt (28-32 câu, đánh số 01. -> N.)
├── script_en.txt           # Kịch bản dài kênh Anh (28-32 câu, đánh số 01. -> N.)
├── prompts_vi.txt          # Tập prompt khớp 1:1 câu thoại kênh Việt (#FAF7F2)
├── prompts_en.txt          # Tập prompt khớp 1:1 câu thoại kênh Anh (#0B132B)
├── video_vi/ (hoặc imgs_vi/) # Media tải từ Google Flow (đánh số 01_..N_)
├── video_en/ (hoặc imgs_en/) # Media tải từ Google Flow (đánh số 01_..N_)
├── audio_vi/ & audio_en/   # Giọng đọc TTS tự sinh (01_voice.mp3 .. N_voice.mp3)
├── subtitles_vi.srt / _en.srt # Phụ đề tự sinh đồng bộ mili-giây
├── youtube_vi.md / _en.md  # Gói đăng YouTube video dài (Tiêu đề, Mô tả + Timestamps, Tags, Thumbnail)
├── shorts_config_vi.json   # Cấu hình tách 3-4 tập Shorts kênh Việt (có main_topic)
├── shorts_config_en.json   # Cấu hình tách 3-4 tập Shorts kênh Anh (có main_topic)
├── shorts_vi/ & shorts_en/ # Chứa các tập Short .mp4, *_thumb.jpg, *_dang_bai.txt, TONG_HOP_DANG_SHORTS*.md
└── <ten_project>_vi.mp4 / _en.mp4 # Video dài Full HD 16:9 hoàn chỉnh
```

---

## 5 Bước Thực Hiện Một Dự Án Mới

### Bước 1: Khởi Tạo Thư Mục Dự Án
```bash
python make_video.py --new <ten_project>
```

### Bước 2: Viết & Chốt Kịch Bản Dài (`28–32 câu`, 10–18 từ/câu)
> **Nguyên tắc**: Chốt kịch bản trước, tuyệt đối chưa tạo prompt khi chưa duyệt kịch bản.

1. **Mở đầu tự nhiên — 3 nhịp (Câu 01–03)**:
   - `01`: Chạm tình huống thực tế đời thường người dùng hay gặp.
   - `02`: Phá vỡ lầm tưởng & đồng cảm.
   - `03`: Lời chào dẫn nhập tự nhiên của kênh (*"Chào mừng bạn đến với Vắt Chanh Công Nghệ..."* / *"Welcome back to Squeezing Tech..."*).
2. **Thân bài chia 3–4 Cụm Độc Lập (Câu 04 đến N-3)** để dễ tách Shorts:
   - Mỗi cụm 6–7 câu giải quyết trọn vẹn 1 khía cạnh.
   - **Bắt buộc câu đầu mỗi cụm là Câu Neo Chủ Đề Tự Thân** (nêu rõ *Chủ đề chính* + *Góc nhìn của cụm*).
   - **Cấm** mở đầu cụm bằng từ phụ thuộc (*"Nhưng..."*, *"Thủ phạm thứ hai là..."*, *"Thứ ba là..."*).
3. **Lời kết tự nhiên — 3 nhịp (3 câu cuối)**:
   - `N-2`: Đúc kết 1 quy tắc thực dụng dễ nhớ.
   - `N-1`: Câu hỏi trò chuyện gần gũi về trải nghiệm thực tế của người xem.
   - `N`: Lời chào thương hiệu + nhắc đăng ký kênh kèm slogan.
4. Lưu kịch bản đã duyệt vào `projects/<ten_project>/script_vi.txt` và `script_en.txt`.

### Bước 3: Sinh Tập Prompt & Chạy Google Flow
1. Tạo `prompts_vi.txt` (`#FAF7F2`) và `prompts_en.txt` (`#0B132B`) khớp `1:1` với số câu kịch bản:
   - Mỗi prompt có dòng ghi chú `# Cảnh XX: ...` phía trên.
   - Xen kẽ 3 dạng cảnh: *Tình huống đời thường* $\rightarrow$ *Mặt cắt/Ẩn dụ trực quan* $\rightarrow$ *Bảng tổng kết 3–4 thẻ Bento Card*.
   - Giữ đồng bộ hình dáng xe/pin ở các cảnh liền kề; gắn hậu tố chặn logo/watermark AI.
2. Chạy bot đẩy prompt lên Google Flow (hoặc mở `run_studio.bat`):
   ```bash
   python auto_flow.py projects/<ten_project>/prompts_vi.txt
   ```
3. Tải media về `video_vi/` (hoặc `imgs_vi/`) và `video_en/` (hoặc `imgs_en/`).
4. **Đánh số đầu file (`01_` $\rightarrow$ `NN_`)** khớp đúng thứ tự `prompts_{vi,en}.txt` trước khi dựng.

### Bước 4: Render Video Dài 16:9 & Xuất Gói YouTube SEO
```bash
# Render bản Tiếng Việt (Giọng Nam Minh + Intro VI)
python make_video.py <ten_project> --lang vi

# Render bản Tiếng Anh (Giọng Christopher + Intro EN)
python make_video.py <ten_project> --lang en
```
- Xuất file `youtube_vi.md` và `youtube_en.md` (gồm 4 tiêu đề CTR cao, mô tả + Timestamps đã cộng bù ~3s Intro, Tags, Pinned Comment, và Text + Prompt Thumbnail 16:9).

### Bước 5: Tách 3–4 Tập YouTube Shorts 9:16 Có Neo Chủ Đề Chính
1. Tạo `shorts_config_vi.json` và `shorts_config_en.json` (mỗi tập 6–8 cảnh, thời lượng `35s–58s`):
   - **Bắt buộc khai báo `"main_topic"`** (VD: `"QUÃNG ĐƯỜNG XE ĐIỆN"`, `"SO GĂNG PIN LFP vs NCM"`) để pano trên đầu video luôn hiển thị `CHỦ ĐỀ CHÍNH • TẬP X/4`.
   - **Cảnh đầu tiên (`scenes[0]`) của mọi tập** phải nêu rõ chủ đề chính (nếu cụm thân bài thiếu ngữ cảnh, ghép thêm Cảnh `1` lên đầu tập).
2. Kiểm tra và render toàn bộ Shorts + Thumbnail 9:16 + bài đăng:
   ```bash
   # Kiểm tra cấu hình trước khi render
   python .agents/skills/shorts-maker/scripts/build_shorts.py <ten_project> --lang vi --dry-run

   # Render Shorts + Thumbnail + Metadata đăng bài
   python .agents/skills/shorts-maker/scripts/build_shorts.py <ten_project> --lang vi
   python .agents/skills/shorts-maker/scripts/build_shorts.py <ten_project> --lang en
   ```
   *(Thêm `--meta-only` nếu chỉ muốn xuất lại ảnh `*_thumb.jpg` và file đăng bài mà không cần render lại `.mp4`).*

---

## Bảng Lệnh Nhanh (Quick Commands)

| Tác vụ | Lệnh CLI |
|---|---|
| Liệt kê các dự án | `python make_video.py --list` |
| Tạo dự án mới | `python make_video.py --new <ten_project>` |
| Render video dài VI / EN | `python make_video.py <ten_project> --lang vi` (hoặc `--lang en`) |
| Ép tạo lại toàn bộ TTS | `python make_video.py <ten_project> --lang vi --force` |
| Kiểm tra cấu hình Shorts | `python .agents/skills/shorts-maker/scripts/build_shorts.py <ten_project> --lang vi --dry-run` |
| Render toàn bộ Shorts VI / EN | `python .agents/skills/shorts-maker/scripts/build_shorts.py <ten_project> --lang vi` (hoặc `--lang en`) |
| Chỉ tạo lại Thumbnail & bài đăng Shorts | `python .agents/skills/shorts-maker/scripts/build_shorts.py <ten_project> --lang vi --meta-only` |
