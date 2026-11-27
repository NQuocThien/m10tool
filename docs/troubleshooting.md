# Xử lý sự cố

## 1. Lỗi số lượng

| Thông báo | Nguyên nhân | Cách sửa |
|---|---|---|
| `LOI KHONG KHOP SO LUONG` (make_video) | Số media ≠ số câu trong `script_vi.txt` | Đếm lại; mỗi câu đúng 1 file media. Xóa file thừa (ảnh trùng, file `.crdownload`) |
| `Script lines (X) != media count (Y)` (build_shorts) | Như trên cho Short | Kiểm tra `video_short_vi/` và `script_short_vi.txt` |
| `scene N out of range 1..M` | `scenes`/`thumb_scene` trong config vượt số câu | Sửa `shorts_config_vi.json` |
| `missing fields: [...]` | Config thiếu trường bắt buộc | Bổ sung theo [configuration-reference.md §4](configuration-reference.md#4-shorts_config_vijson) |
| Sort Resource báo `Số lượng không khớp` | Số file tải về ≠ số dòng `# Cảnh XX` trong file prompt | Tải đủ hoặc xóa file thừa, rồi Sort lại |

## 2. Media sai thứ tự

- `get_sorted_images` **tự đổi tên** file chưa có tiền tố số thành `01_..` theo thứ tự tên. Nếu thứ tự sai, đổi tên tay theo đúng số cảnh rồi render lại.
- Sort Resource ghép theo **thời gian tải** (`mtime`). Tải lần lượt đúng thứ tự prompt, hoặc đổi tên tay.
- File đã có tiền tố số nằm ngoài danh sách cảnh của prompt (vd. mascot tái sử dụng) được giữ nguyên.

## 3. TTS / giọng đọc

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| `Model ... chạm giới hạn 429 Quota` | Hết quota model đó | Tự chuyển model kế tiếp; nếu tất cả hết → chờ reset quota hoặc chọn giọng Edge TTS |
| `Tất cả Gemini TTS models đều lỗi hoặc hết quota` | Hết quota / sai key / model ngừng | Kiểm tra `GEMINI_API_KEY`; rà `GEMINI_TTS_FALLBACK_MODELS` |
| Lỗi xác thực / thiếu API key | Chưa đặt biến môi trường | Xem [deployment-guide.md §3](deployment-guide.md#3-cấu-hình-api-key) |
| Giọng đổi khác giữa các câu | Một số câu rơi về model cũ (voice tự đổi thành `Charon`) | Chạy lại `--force` / `--force-tts` khi quota ổn định |
| Câu bị cắt dính chữ câu bên cạnh | Tách WAV theo khoảng lặng chọn sai điểm | Xóa file `NN_voice.mp3` lỗi rồi chạy lại (chỉ câu đó được tạo lại) |
| `Thư mục audio cũ chưa có tts_manifest.json` | Dự án tạo trước khi có cache theo hash | Nếu kịch bản từng sửa, chạy 1 lần với `--force` |
| Đọc sai thuật ngữ / đơn vị | Chưa có trong từ điển | Thêm vào `resources/pronunciation_vi.json` |
| Edge TTS `NoAudioReceived` | Mạng chập chờn | Tự retry 8 lần; kiểm tra mạng |

## 4. Phụ đề / caption

| Triệu chứng | Cách sửa |
|---|---|
| Từ ghép bị cắt đôi ("nhu / cầu") | Thêm cụm vào `resources/vi_compound_words.txt` |
| Caption lệch nhịp so với giọng | Thời gian đang ước lượng theo số ký tự — rút ngắn câu, tránh câu quá dài; về lâu dài cần forced alignment |
| Lỗi burn phụ đề `FFmpeg subtitle burn error` | Đường dẫn dự án có ký tự đặc biệt (`'`, `[`, `]`) — đổi tên thư mục |

## 5. Render

| Thông báo | Cách sửa |
|---|---|
| `FFmpeg error on scene N` | Media hỏng hoặc định dạng lạ — mở thử file, convert lại sang `.mp4` H.264 / `.png` |
| `2.5D split failed on scene N, using Ken Burns` | Không ảnh hưởng kết quả; kiểm tra `rembg` đã tải model chưa |
| Render rất chậm khi bật 2.5D | Lần đầu tải model + tách nền tuần tự; lần sau dùng cache `cache_25d/` |
| Short không có nhạc nền | Thiếu `resources/bgm_shorts.mp3` và cả `bgm_vi.mp3`/`bgm.mp3` |
| Còn thư mục `_temp_*` trong `shorts_vi/` | Render bị ngắt; lần chạy sau tự dọn |
| Video dài bị khung dọc | Media đầu tiên là ảnh dọc → hệ thống chọn 1080x1920. Đặt media ngang ở cảnh 01 |

## 6. Bot Google Flow

| Triệu chứng | Cách sửa |
|---|---|
| `Hết thời gian chờ 300s. Không tìm thấy ô nhập Prompt` | Đăng nhập Google và mở đúng trang dự án Flow trong cửa sổ Chrome của bot, rồi chạy lại |
| Bot đứng ở `CHỜ SẴN SÀNG` | Bấm **🚀 Sẵn Sàng** trên Studio hoặc nút xanh trên đỉnh trang Chrome |
| `Mất liên kết với ô nhập Prompt` | Flow đổi giao diện / tải lại trang — bot tự thử câu tiếp sau 10s; nếu lặp lại, cần cập nhật `find_flow_input` |
| Chrome không mở | Chưa cài Google Chrome, hoặc hồ sơ `user_data/` đang bị Chrome khác chiếm — đóng hết cửa sổ Chrome của bot |
| Lỗi prompt rỗng | File prompt chỉ có dòng `#` |

## 7. Studio

| Triệu chứng | Cách sửa |
|---|---|
| Lỗi font / ký tự tiếng Việt trong console | Mở bằng `run_studio.bat` thay vì `python app.py` |
| Mất cài đặt lần trước | `app_settings.json` hỏng — xóa file, Studio tự tạo lại |
| Không nghe được preview | `winsound` chỉ phát WAV trên Windows; kiểm tra thiết bị âm thanh |
