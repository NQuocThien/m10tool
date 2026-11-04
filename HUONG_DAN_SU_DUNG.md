# HƯỚNG DẪN SẢN XUẤT VIDEO TỰ ĐỘNG BẰNG AI PIPELINE

Tài liệu hướng dẫn chuẩn hóa quy trình tạo video công nghệ/giải thích (Tech Explainer) từ ảnh tĩnh và câu thoại, tự động hóa 100% bằng Python, Azure Neural TTS và FFmpeg.

---

## 1. CẤU TRÚC THƯ MỤC CHUẨN

Toàn bộ dự án nằm tại `C:\Workspace2\Video`. Không cần tạo project mới ở ngoài, mỗi video mới chỉ là **một thư mục con** nằm trong `projects/`:

```
C:\Workspace2\Video\
├── make_video.py                  # Công cụ dòng lệnh (CLI) chính để render mọi video
├── auto_flow.py                   # Script tự động đẩy prompt lên Google Flow
├── requirements.txt               # Thư viện phụ thuộc (edge-tts, imageio-ffmpeg)
├── core/                          # Bộ máy xử lý ngầm (TTS, Sort, Subtitle, Render)
│   ├── config.py                  # Cấu hình mặc định (fps, zoom, sub style)
│   ├── sorter.py                  # Tự động nhận diện và sắp xếp thứ tự ảnh
│   ├── tts.py                     # Sinh giọng đọc AI Studio tự nhiên
│   ├── subtitles.py               # Đo duration và tạo file SRT chuẩn mili-giây
│   └── renderer.py                # FFmpeg: lia zoom Ken Burns 3% + burn hardsub
└── projects/                      # Nơi lưu trữ tất cả các video
    ├── lfp_vs_ncm/                # Dự án mẫu: So sánh Pin LFP vs NCM (30 cảnh)
    ├── sample_template/           # Thư mục mẫu sẵn khung
    └── <ten_video_cua_ban>/       # Thư mục video mới do bạn tạo
        ├── imgs/                  # Thư mục chứa các file ảnh
        ├── script.txt             # File chứa các câu thoại (mỗi dòng 1 câu)
        ├── audio/                 # Tự động sinh ra: các file voice mp3
        ├── subtitles.srt          # Tự động sinh ra: file phụ đề đã sync time
        └── <ten_video>.mp4        # Video Full HD thành phẩm
```

---

## 2. QUY TRÌNH 3 BƯỚC TẠO VIDEO MỚI

### Bước 1: Soạn Prompt ảnh & Kịch bản thoại
Yêu cầu AI (hoặc tự viết) 2 nội dung:
1. **Danh sách Prompt ảnh**: Mạch logic từ 1 đến N cảnh. Để ảnh có phong cách 3D kỹ thuật đồng nhất, luôn gắn thêm đuôi:
   ```text
   3D technical render, clean engineering aesthetic, octane render, photorealistic lighting, highly detailed, 8k resolution, cinematic atmosphere --ar 16:9
   ```
2. **Kịch bản thoại (`script.txt`)**: Mỗi câu tương ứng 1 ảnh, thời lượng khoảng 3-5 giây (10-18 từ/câu).
   - Ví dụ format trong `script.txt`:
     ```text
     01. When choosing an electric two-wheeler, the biggest decision starts inside the battery pack.
     02. In this showdown, it comes down to a classic trade-off: rugged durability against energy density.
     03. Both chemistries power modern mobility, but create two entirely different riding experiences.
     ```

### Bước 2: Tạo ảnh & Tải về
- **Cách 1 (Tự động)**: Chạy bot nạp danh sách prompt lên Google Flow:
  ```bash
  python auto_flow.py <duong_dan_file_prompt>
  ```
- **Cách 2 (Thủ công)**: Dán prompt vào Google Flow / Midjourney / Flux.
- **Tải ảnh**: Trên Flow, bấm menu 3 chấm góc phải trên $\rightarrow$ chọn **Download project** $\rightarrow$ giải nén các file ảnh vào thư mục `projects/<ten_video>/imgs/`.

### Bước 3: Tạo thư mục & Render video 1-click
Mở terminal tại `C:\Workspace2\Video` và thực hiện:

1. **Khởi tạo thư mục dự án mới**:
   ```bash
   python make_video.py --new ten_video_moi
   ```
2. **Copy file**:
   - Thả toàn bộ ảnh tải về vào `projects/ten_video_moi/imgs/`.
   - Dán nội dung câu thoại vào `projects/ten_video_moi/script.txt`.
3. **Bấm render**:
   ```bash
   python make_video.py ten_video_moi
   ```

Hệ thống sẽ tự động thực hiện từ A đến Z:
- Tự chuẩn hóa thứ tự ảnh (`01_...` đến `N_...`).
- Tự gọi Azure Neural AI đọc từng câu và lưu thành file `.mp3`.
- Tự đo chính xác thời lượng từng file âm thanh để làm phụ đề `.srt`.
- Tự nhận diện ảnh ngang (16:9) hay ảnh dọc (9:16).
- Áp hiệu ứng Ken Burns lia nhẹ 3% luân phiên (tránh hình tĩnh gây nhàm chán).
- Ghép audio, burn hardsub chữ nhỏ thanh lịch ở đáy màn hình.
- Xuất file video `projects/ten_video_moi/ten_video_moi.mp4`.

---

## 3. BẢNG LỆNH DÒNG LỆNH (CLI CHEATSHEET)

| Tác vụ | Lệnh | Ghi chú |
|---|---|---|
| **Xem danh sách video** | `python make_video.py --list` | Kiểm tra số ảnh, số câu thoại, trạng thái render |
| **Tạo dự án mới** | `python make_video.py --new <ten>` | Tự tạo cấu trúc `imgs/` và `script.txt` mẫu |
| **Render video mặc định** | `python make_video.py <ten>` | Giọng nam Mỹ phóng sự (`en-US-ChristopherNeural`) |
| **Đổi giọng đọc AI** | `python make_video.py <ten> --voice <voice_id>` | Xem bảng giọng đọc bên dưới |
| **Render ép buộc** | `python make_video.py <ten> --force` | Bỏ qua cache audio cũ, sinh lại toàn bộ giọng mới |

---

## 4. BẢNG MÃ GIỌNG ĐỌC AI PHỔ BIẾN (AZURE NEURAL TTS)

| Ngôn ngữ | Giới tính | Tên Voice (`--voice`) | Đặc trưng phong cách |
|---|---|---|---|
| **Tiếng Anh (Mỹ)** | Nam | `en-US-ChristopherNeural` *(Mặc định)* | Trầm ấm, chuyên nghiệp, chuẩn Tech Documentary |
| **Tiếng Anh (Mỹ)** | Nữ | `en-US-JennyNeural` | Tự nhiên, truyền cảm, dễ nghe |
| **Tiếng Anh (Mỹ)** | Nam | `en-US-GuyNeural` | Trẻ trung, tự nhiên, phong cách trò chuyện |
| **Tiếng Anh (Anh)** | Nam | `en-GB-RyanNeural` | Giọng Anh-Anh sắc sảo, đĩnh đạc |
| **Tiếng Việt** | Nữ | `vi-VN-HoaiMyNeural` | Giọng nữ miền Bắc rõ ràng, chuẩn tin tức |
| **Tiếng Việt** | Nam | `vi-VN-NamMinhNeural` | Giọng nam miền Bắc trầm ấm, dõng dạc |

*Ví dụ render video tiếng Việt:*
```bash
python make_video.py video_tieng_viet --voice vi-VN-NamMinhNeural
```

---

## 5. TỰ ĐỘNG NHẬN DIỆN TỶ LỆ KHUNG HÌNH (ORIENTATION)

Hệ thống tự động phân tích kích thước ảnh đầu tiên để chọn tỷ lệ xuất video:
- **Ảnh Ngang ($Width \ge Height$)**: Render chuẩn **1920x1080 (16:9 Full HD)** dành cho YouTube, Website, Màn hình máy tính. Phụ đề cỡ 15pt đặt sát đáy lề 24px.
- **Ảnh Dọc ($Height > Width$)**: Render chuẩn **1080x1920 (9:16 Vertical)** dành cho TikTok, Reels, YouTube Shorts. Phụ đề cỡ 18pt căn lề 60px để không bị che bởi các nút Like/Share của TikTok.

---

## 6. XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

1. **Lỗi: "Count mismatch: X images vs Y audio/script lines"**:
   - *Nguyên nhân*: Số lượng ảnh trong thư mục `imgs/` không bằng số câu thoại trong `script.txt`.
   - *Khắc phục*: Đếm lại số dòng script và số ảnh tải về. Mỗi ảnh bắt buộc đi kèm đúng 1 câu thoại.

2. **Lỗi: Thiếu thư viện**:
   - Chạy lệnh cài đặt bổ sung:
     ```bash
     pip install -r requirements.txt
     ```

3. **Muốn chỉnh lại âm lượng hoặc hiệu ứng chuyển động**:
   - Mở file `core/config.py` để tùy biến:
     - `DEFAULT_MAX_ZOOM = 1.03`: Biên độ lia zoom (mặc định 3%).
     - `DEFAULT_FPS = 25`: Số khung hình/giây.
     - `DEFAULT_SUB_STYLE`: Màu chữ, font chữ, độ đậm viền phụ đề.
