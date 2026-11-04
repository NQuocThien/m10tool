# Hướng dẫn tạo video mới trong thư mục này

Mỗi khi muốn làm một video mới, bạn chỉ cần tạo một thư mục con trong `projects/`:

```
C:\Workspace2\Video\projects\<tên_video_mới>\
├── imgs/         <- Bỏ tất cả ảnh (tải từ Google Flow hoặc Midjourney) vào đây
└── script.txt    <- File text chứa các câu thoại (mỗi dòng 1 câu tương ứng 1 ảnh)
```

### Các bước thực hiện:
1. Bỏ ảnh vào `imgs/` (ảnh sẽ tự động được sắp xếp và đánh số).
2. Viết câu thoại vào `script.txt` (đảm bảo số câu thoại bằng đúng số lượng ảnh).
3. Mở terminal tại `C:\Workspace2\Video` và gõ:
   ```bash
   python make_video.py <tên_video_mới>
   ```

Hệ thống sẽ tự động:
- Đổi tên và đánh số thứ tự ảnh.
- Tạo giọng đọc AI Studio tự nhiên (Azure Neural TTS).
- Tự động canh mili-giây và tạo phụ đề chuẩn.
- Dựng video Full HD 1080p với hiệu ứng lia zoom nhẹ (Ken Burns).
- Đè phụ đề chữ nhỏ, thanh lịch sát đáy.
- Xuất file `<tên_video_mới>.mp4` ngay trong thư mục này!
