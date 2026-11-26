# Quy Chuẩn Viết Kịch Bản Video Dài & 4 Cụm Hook Tách Shorts (V3 - Anti-Swipe)

Áp dụng cho **Vắt Chanh Công Nghệ** (`script_vi.txt`) và **Squeezing Tech** (`script_en.txt`). Tổng độ dài: **28–32 câu** (~4–5.5 giây/cảnh).

## 1. Mở Đầu Giữ Chân 3 Giây Đầu — "Con Số Sốc -> Bóc Mẽ -> Open Loop" (Câu 01–03)

**CẤM** mở đầu bằng câu hỏi sáo rỗng (*"Chắc hẳn bạn từng..."*, *"Bạn có bao giờ tự hỏi..."*) hoặc chào hỏi dài dòng:
- **Câu 01 (Con số sốc / Nghịch lý mất tiền trực diện — Dùng làm Hook Mở Màn Tập 1 Shorts)**:
  - *VI*: `"Một bộ ắc quy Graphene giá chỉ 4 triệu so với 12 triệu của pin Lithium — nhưng sau 5 năm chạy xe, người mua rẻ lại tốn gấp đôi tiền."`
  - *EN*: `"A graphene lead-acid pack costs just $160 versus $480 for lithium — yet over five years, the cheap buyer pays double."`
- **Câu 02 (Bóc mẽ nguyên nhân cốt lõi)**:
  - *VI*: `"Cái bẫy nằm ở chỗ người mua chỉ nhìn giá lúc dắt xe khỏi tiệm, mà bỏ qua vòng đời sạc và khối lượng chết đè lên động cơ."`
- **Câu 03 (Cài Open Loop giữ chân đến cuối video)**:
  - *VI*: `"Trong 3 phút tới, cùng Vắt Chanh Công Nghệ bóc trần 4 sự thật bên trong vỏ bình — kèm quy tắc nhẩm 3 giây ở cuối video để không mất tiền oan."`

## 2. Nhịp Câu & Định Dạng Con Số Cho Gemini TTS + Highlight Phụ Đề Shorts

1. **Xen kẽ câu ngắn đanh thép & dấu ngắt nhịp (`.`, ` — `)**:
   - Không viết 30 câu đều đều 20 từ. Dùng ` — ` hoặc `.` giữa câu để giọng TTS (`voice_5mxlq1k9luls` / `Charon`) tạo điểm nhấn.
2. **Viết mọi con số bằng Chữ Số + Đơn Vị Chuẩn (`200 km`, `65%`, `150 triệu`, `50°C`, `3.000 chu kỳ`)**:
   - **CẤM** viết chữ (*"hai trăm cây số"*, *"một trăm năm mươi triệu"*).
   - Engine dựng Shorts (`make_shorts.py`) sẽ tự động phát hiện và **tô màu nổi bật (Highlight Accent)** cho các cụm chữ số trên khung phụ đề để hút mắt người xem ngay lập tức.

## 3. Thân Bài 4 Cụm Độc Lập — Công Thức "Hook Giật Mình Đầu Mỗi Cụm" (Câu 04 đến N-3)

Một video dài cắt thành **4 tập YouTube Shorts**. Cảnh đầu tiên của mỗi tập quyết định **tỷ lệ dừng lại xem (Viewed vs. Swiped Away > 75%)**:

### Quy Tắc Sống Còn Cho Câu Đầu Tiên Của Mỗi Cụm (Cảnh `04`, `10`, `16`, `22`):
1. **CẤM văn phong chuyển đoạn bài giảng / mục lục học thuật**:
   - **CẤM TUYỆT ĐỐI**: *"Xét về bài toán..."*, *"Với lộ trình..."*, *"Trong bài toán chọn mua..."*, *"Điểm khác biệt rõ nhất nằm ở..."*, *"Khi mua xe..., lầm tưởng lớn nhất là..."*, *"Thủ phạm thứ hai là..."*, *"Nhưng..."*.
   - Những câu trên làm người lướt Shorts (khi gặp ngẫu nhiên Tập 2, 3, 4) cảm giác đang nghe giữa chừng một bài thuyết trình khô khan và **vuốt bỏ ngay ở giây thứ 2**.
2. **BẮT BUỘC mở đầu mỗi cụm bằng công thức `CON SỐ SỐC / HẬU QUẢ MẤT TIỀN + CHỦ ĐỀ CHÍNH + GÓC NHÌN`**:
   - *Sai (Văn bài giảng — Rớt view)*: `"Xét về bài toán giá thành pin mật độ cao 500 Wh/kg, nguyên liệu chế tạo chính là bức tường ngăn cản pin thể rắn giảm giá trước năm 2030."`
   - *Đúng (Hook Shorts 3s — Giữ chân)*: `"Đắt gấp 20 lần pin thường và tự bốc khí độc mùi trứng thối khi gặp ẩm — đó là lý do pin thể rắn 500 Wh/kg không thể có giá rẻ trước năm 2030!"`
   - *Sai (Chậm — Rớt view)*: `"Trên cùng một chiếc xe máy điện, trọng lượng của bộ ắc quy dưới sàn để chân đang âm thầm ăn bớt từng cây số quãng đường của bạn."`
   - *Đúng (Đập thẳng số 40 kg vs 10 kg ngay câu đầu)*: `"Nặng tới 40 kg so với 10 kg của pin Lithium — bộ ắc quy chì dưới sàn xe máy điện giống như bắt bạn đèo thêm bao gạo 30 kg mỗi ngày!"`
3. **BẮT BUỘC gán nhãn `[VIDEO] (.mp4)` cho Câu Đầu Mỗi Cụm**:
   - Các câu mở đầu Cụm 1, 2, 3, 4 (hoặc Cảnh `01` cho Tập 1 và Câu đầu Cụm 2, 3, 4 cho Tập 2, 3, 4) **bắt buộc phải nằm trong `prompts_{vi,en}_video.txt`** để render thành clip hoạt họa `.mp4`.
   - **CẤM** để bất kỳ tập Short nào mở đầu bằng ảnh tĩnh `.jpg`.

## 4. Lời Kết 3 Nhịp (3 Câu Cuối)

- **Câu N-2 (Trả Open Loop / Quy tắc bỏ túi có con số — `[IMG]` Bento Card)**: Chốt công thức ngắn gọn nhất (dùng làm cảnh kết cho Tập 4 Shorts).
- **Câu N-1 (Câu hỏi khảo sát con số thực tế — `[VIDEO]` riêng theo đúng chủ đề)**: Khơi gợi bình luận. **BẮT BUỘC viết prompt `[VIDEO]` mới cho cảnh 29 (`N-1`)** có mặt thiết bị/chủ đề chính của video cùng Mascot Chanh chuyển động (tuyệt đối không copy file `29_mascot_survey.mp4` hình xe máy điện cũ sang chủ đề khác).
- **Câu N (Lời chào thương hiệu & Slogan — `[VIDEO]` riêng theo đúng chủ đề)**: **BẮT BUỘC viết prompt `[VIDEO]` mới cho cảnh 30 (`N`)** có mặt thiết bị/chủ đề chính của video + biểu tượng nút nguồn chanh + Mascot Chanh vẫy tay chào (tuyệt đối không copy file `30_mascot_outro.mp4` khác chủ đề).

## 5. Nhịp Điệu Thị Giác 3 Dạng Cảnh (Visual Archetypes)
1. **Dạng A - Tình huống đời thường / Nỗi đau trực diện** (Ưu tiên làm cảnh `[VIDEO]` mở đầu cụm).
2. **Dạng B - Mặt cắt giải phẫu / Ẩn dụ vật lý** (Cưa đôi vỏ bình, cốc giác hơi hút nước, bao gạo 30 kg).
3. **Dạng C - Bảng tổng kết Bento Card** (Chốt quy tắc cuối cụm).
