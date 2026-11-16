import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

from core.config import FFMPEG_PATH, DEFAULT_FPS, PROJECTS_DIR, RESOURCES_DIR
from core.sorter import get_sorted_images
from core.tts import load_script
from core.subtitles import generate_subtitles

# 4 cấu hình YouTube Shorts cho dự án lfp_vs_ncm
SHORTS_CONFIG = [
    {
        "id": "short_01_kich_thuoc_thuc_dung",
        "badge": "TẬP 1 • KÍCH THƯỚC & TIỆN ÍCH",
        "title_line1": "PIN XE ĐIỆN LFP vs NCM",
        "title_line2": "Cốp Rộng Nhẹ Tênh Hay Đầm Chắc?",
        "accent_color": "#D35400",  # Terracotta Orange
        "scenes": [1, 2, 9, 10, 11, 12, 13, 30],
        "thumb_scene": 10,
        "thumb_big_text": "NẶNG ĐẦM CHẮC\nhay NHẸ CỐP RỘNG?",
        "thumb_sub_badge": "SO GĂNG THỂ TÍCH: LFP vs NCM",
        "yt_titles": [
            "Pin xe máy điện LFP vs NCM: Chọn cốp rộng nhẹ tênh hay đầm chắc? #shorts",
            "Tại sao pin LFP luôn to nặng gấp rưỡi pin NCM trên xe máy điện? #shorts",
            "Mua xe điện ở chung cư: Nên chọn pin LFP hay pin NCM tháo rời? #shorts",
        ],
        "yt_description": (
            "Mua xe máy điện sợ nhất pin chai hoặc cháy nổ, nhưng chọn pin LFP hay NCM mới thực sự hợp nhu cầu đi lại hàng ngày?\n\n"
            "📌 Nội dung chính trong video:\n"
            "• NCM nhồi năng lượng gấp 1.5 lần: Nhỏ gọn, cốp rộng để vừa 2 mũ bảo hiểm, nhẹ nhàng xách lên chung cư sạc.\n"
            "• LFP to và nặng hơn gấp rưỡi: Đặt dưới sàn giúp hạ trọng tâm xe, vào cua đầm chắc không bồng bềnh.\n\n"
            "👉 Bạn chọn cốp rộng nhẹ nhàng (NCM) hay đầm chắc bền bỉ (LFP)? Bình luận ngay mẫu xe bạn đang nhắm tới nhé!\n\n"
            "🔔 Đăng ký kênh Vắt Chanh Công Nghệ — “Vắt sạch thông số, giữ lại cách dùng”\n\n"
            "#VatChanhCongNghe #XeMayDien #PinLFP #PinNCM #PinXeDien #KienThucXeDien #Shorts"
        ),
        "yt_pinned_comment": "Anh em đang đi xe điện dùng pin LFP hay NCM? Cốp có đủ rộng để 2 mũ bảo hiểm không, chia sẻ bên dưới nhé! 👇",
        "thumb_desc": (
            "So sánh trực diện kích thước 2 khối pin đặt cạnh nhau trên nền vàng kem #FAF7F2: "
            "Bên trái là khối pin LFP viền xanh lá lớn hơn 1.5 lần kèm icon trọng tâm thấp đầm chắc; "
            "bên phải là khối pin NCM viền vàng cam nhỏ gọn kèm icon cốp xe chứa 2 mũ bảo hiểm. "
            "Chữ tiêu đề lớn: 'NẶNG ĐẦM CHẮC hay NHẸ CỐP RỘNG?'."
        ),
        "thumb_prompt": (
            "Vertical 9:16 YouTube Shorts thumbnail, bold 2D flat vector editorial tech infographic on a warm cream background (#FAF7F2), "
            "split comparison: left shows a large heavy LFP battery pack in lime green (#7CB342) under a scooter floorboard lowering center of gravity, "
            "right shows a compact lightweight NCM battery pack in golden lemon (#F4C430) and terracotta (#D35400) beside a spacious scooter trunk fitting two helmets, "
            "cute nerdy lemon mascot with round glasses in center, clean rounded charcoal line art (#1C1917), high contrast, no text, no watermark --ar 9:16"
        ),
    },
    {
        "id": "short_02_an_toan_chong_chay_no",
        "badge": "TẬP 2 • AN TOÀN & CHỐNG CHÁY NỔ",
        "title_line1": "ĐÂM ĐINH KHÔNG NỔ?",
        "title_line2": "Vì Sao LFP An Toàn Hơn Pin NCM",
        "accent_color": "#7CB342",  # Lime Green
        "scenes": [14, 6, 15, 16, 17, 18, 28],
        "thumb_scene": 14,
        "thumb_big_text": "ĐÂM ĐINH XUYÊN THỦNG\nKHÔNG BÉN LỬA!",
        "thumb_sub_badge": "BÍ MẬT CHỐNG CHÁY NỔ PIN LFP",
        "yt_titles": [
            "Tại sao pin LFP đâm đinh không nổ, còn pin NCM dễ cháy dây chuyền? #shorts",
            "Sự thật việc cắm sạc xe điện qua đêm: Vì sao pin LFP an toàn tuyệt đối? #shorts",
            "Bên trong viên pin LFP có gì mà chịu nhiệt & chống cháy nổ đỉnh vậy? #shorts",
        ],
        "yt_description": (
            "Nỗi sợ lớn nhất khi sạc xe điện tại nhà qua đêm là chập cháy. Vậy bản chất hóa học của pin LFP và NCM khác nhau thế nào khi gặp sự cố?\n\n"
            "📌 Nội dung chính trong video:\n"
            "• Thử nghiệm đâm đinh xuyên thủng: Cell pin LFP chỉ xì khói trắng nhẹ, tuyệt đối không phát nổ.\n"
            "• Mạng tinh thể LFP bền vững như pháo đài bê tông dưới nhiệt độ khắc nghiệt.\n"
            "• NCM khi quá nhiệt tự giải phóng khí oxy gây hiệu ứng cháy domino, bắt buộc phải có mạch BMS và vách ngăn chịu nhiệt tinh vi.\n\n"
            "👉 Bạn có hay cắm sạc xe máy điện qua đêm tại nhà không? Để lại ý kiến bên dưới nhé!\n\n"
            "🔔 Đăng ký kênh Vắt Chanh Công Nghệ — “Vắt sạch thông số, giữ lại cách dùng”\n\n"
            "#VatChanhCongNghe #AnToanPinXeDien #PinLFP #PinNCM #ChongChayNo #XeMayDien #Shorts"
        ),
        "yt_pinned_comment": "Nhà anh em có hay cắm sạc xe điện qua đêm không? Chọn LFP cho an tâm tuyệt đối nhé! 👇",
        "thumb_desc": (
            "Cận cảnh bài test đinh thép đâm xuyên cell pin LFP trên nền vàng kem #FAF7F2: "
            "Pin LFP màu xanh lá chỉ tỏa làn khói trắng nhẹ kèm khiên bảo vệ an toàn, đối lập với biểu tượng cảnh báo nhiệt đỏ cam của NCM. "
            "Chữ tiêu đề lớn: 'ĐÂM ĐINH XUYÊN THỦNG KHÔNG BÉN LỬA!'."
        ),
        "thumb_prompt": (
            "Vertical 9:16 YouTube Shorts thumbnail, dramatic 2D flat vector tech illustration on a warm cream background (#FAF7F2), "
            "a sharp steel nail puncturing a lime green LFP battery cell (#7CB342) releasing only a tiny harmless white puff with a green safety shield icon, "
            "contrasted with a small warning flame icon on an orange NCM cell (#D35400), clean rounded charcoal line art (#1C1917), modern editorial infographic, no text, no watermark --ar 9:16"
        ),
    },
    {
        "id": "short_03_cam_giac_lai_meo_sac",
        "badge": "TẬP 3 • VẬN HÀNH & MẸO SẠC PIN",
        "title_line1": "TRÁNH BÁO PIN ẢO!",
        "title_line2": "Mẹo Sạc Pin LFP 100% & NCM 80%",
        "accent_color": "#F4C430",  # Golden Lemon
        "scenes": [19, 20, 21, 22, 23, 24, 25],
        "thumb_scene": 23,
        "thumb_big_text": "LFP SẠC 100%\nNCM CHỈ SẠC 80%?",
        "thumb_sub_badge": "MẸO SẠC KHÔNG BÁO PIN ẢO & CHAI PIN",
        "yt_titles": [
            "Sai lầm khi sạc pin xe điện LFP & NCM khiến xe báo pin ảo, nhanh chai! #shorts",
            "Tại sao pin LFP phải sạc đầy 100%, còn pin NCM chỉ nên sạc 80%? #shorts",
            "Khắc phục lỗi xe máy điện báo pin ảo tụt đột ngột cực dễ tại nhà! #shorts",
        ],
        "yt_description": (
            "Nhiều người dùng chung một thói quen sạc cho mọi loại xe điện mà không biết pin LFP và NCM có nguyên lý đo áp hoàn toàn trái ngược!\n\n"
            "📌 Nội dung chính trong video:\n"
            "• Cảm giác lái: NCM xả dòng mạnh vặn ga dính lưng, đi mùa đông giữ phong độ tốt; LFP êm mượt đi phố.\n"
            "• Đường cong xả phẳng của LFP dễ làm đồng hồ báo pin ảo -> Mẹo: Sạc đầy 100% định kỳ để BMS cân chỉnh lại vạch pin.\n"
            "• Pin NCM báo % cực chuẩn theo điện áp -> Mẹo: Chỉ nên sạc 80% hàng ngày để kéo dài tuổi thọ tối đa.\n\n"
            "👉 Xe bạn có bao giờ đang báo còn 30% pin mà vặn ga tụt thẳng về 0% chưa? Comment ngay nhé!\n\n"
            "🔔 Đăng ký kênh Vắt Chanh Công Nghệ — “Vắt sạch thông số, giữ lại cách dùng”\n\n"
            "#VatChanhCongNghe #MeoSacPinXeDien #BaoPinAo #PinLFP #PinNCM #XeMayDien #Shorts"
        ),
        "yt_pinned_comment": "Anh em nhớ quy tắc vàng nhé: Pin LFP định kỳ sạc đầy 100% để chống báo ảo, còn pin NCM sạc 80% hàng ngày để bền nhất! 💡",
        "thumb_desc": (
            "Hai biểu tượng vạch sạc pin đặt song song trên nền vàng kem #FAF7F2: "
            "Pin LFP xanh lá hiển thị mức sạc 100% (kèm dấu tích xanh cân bằng cell), "
            "Pin NCM vàng cam hiển thị mức giới hạn 80% bảo vệ tuổi thọ. "
            "Chữ tiêu đề lớn: 'LFP SẠC 100% - NCM CHỈ SẠC 80%?'."
        ),
        "thumb_prompt": (
            "Vertical 9:16 YouTube Shorts thumbnail, 2D flat vector tech infographic on a warm cream background (#FAF7F2), "
            "two large battery charging gauges: left lime green LFP battery gauge (#7CB342) glowing at full bar with a calibration checkmark icon, "
            "right golden lemon and terracotta NCM battery gauge (#F4C430, #D35400) stopping at 80 percent optimal health zone with a heart shield icon, "
            "clean rounded charcoal line art (#1C1917), no text, no watermark --ar 9:16"
        ),
    },
    {
        "id": "short_04_do_ben_3000_chu_ky",
        "badge": "TẬP 4 • ĐỘ BỀN & BÀI TOÁN KINH TẾ",
        "title_line1": "BỀN 3.000 CHU KỲ SẠC",
        "title_line2": "Xe Hỏng Pin Chưa Chai: Chọn Loại Nào?",
        "accent_color": "#D35400",  # Terracotta Orange
        "scenes": [26, 4, 5, 27, 28, 29, 30],
        "thumb_scene": 26,
        "thumb_big_text": "3.000 LẦN SẠC!\nXE HỎNG PIN CHƯA CHAI",
        "thumb_sub_badge": "BÀI TOÁN KINH TẾ: LFP vs NCM",
        "yt_titles": [
            "Xe hỏng mà pin chưa chai: Sự thật về 3.000 chu kỳ sạc của pin LFP! #shorts",
            "Chạy dịch vụ, giao hàng hay đi phố: Nên mua xe điện pin LFP hay NCM? #shorts",
            "So sánh tuổi thọ & chi phí thực tế giữa pin LFP và pin NCM sau 5 năm! #shorts",
        ],
        "yt_description": (
            "Với hơn 3.000 chu kỳ sạc-xả, pin LFP có thể đồng hành gần 10 năm mà chưa chai. Nhưng khi nào pin NCM vẫn đáng tiền hơn?\n\n"
            "📌 Nội dung chính trong video:\n"
            "• LFP làm từ sắt & phốt phát dồi dào, giá rẻ, bền hơn 3.000 chu kỳ sạc (xe hỏng pin chưa hỏng).\n"
            "• NCM dùng Niken & Coban đắt đỏ nhưng khi hết vòng đời lại có giá trị thu hồi tái chế kim loại quý rất cao.\n"
            "• Chốt lựa chọn: Cày cuốc giao hàng, xe ôm công nghệ, sạc qua đêm tại nhà -> Chọn LFP chi phí/km rẻ nhất!\n\n"
            "👉 Bạn chọn ăn chắc mặc bền (LFP) hay nhẹ nhàng bốc khỏe (NCM)? Để lại bình luận mẫu xe bạn chọn nhé!\n\n"
            "🔔 Đăng ký kênh Vắt Chanh Công Nghệ — “Vắt sạch thông số, giữ lại cách dùng”\n\n"
            "#VatChanhCongNghe #TuoiThoPinXeDien #PinLFP #PinNCM #XeOmCongNghe #XeMayDien #Shorts"
        ),
        "yt_pinned_comment": "Hơn 3.000 chu kỳ sạc tương đương gần 8-10 năm sạc mỗi ngày! Anh em chạy dịch vụ hay đi làm văn phòng, chọn đội nào? 👇",
        "thumb_desc": (
            "Hình ảnh chiếc xe máy điện đặt cạnh khối pin LFP xanh lá lấp lánh biểu tượng vô cực 3.000 chu kỳ sạc và chiếc xe giao hàng tiết kiệm chi phí trên nền vàng kem #FAF7F2. "
            "Chữ tiêu đề lớn: '3.000 LẦN SẠC! XE HỎNG PIN CHƯA CHAI'."
        ),
        "thumb_prompt": (
            "Vertical 9:16 YouTube Shorts thumbnail, 2D flat vector editorial tech illustration on a warm cream background (#FAF7F2), "
            "a sturdy lime green LFP battery pack (#7CB342) crowned with a golden trophy and cycle arrows beside an electric delivery scooter with coin savings icons, "
            "warm golden lemon (#F4C430) and terracotta (#D35400) accents, clean rounded charcoal line art (#1C1917), no text, no watermark --ar 9:16"
        ),
    },
]

# 4 cấu hình YouTube Shorts Tiếng Anh (Squeezing Tech - #0B132B) cho dự án lfp_vs_ncm
SHORTS_CONFIG_EN = [
    {
        "id": "short_01_size_and_utility",
        "badge": "EPISODE 1 • SIZE & PRACTICAL UTILITY",
        "title_line1": "LFP vs NCM BATTERY SIZE",
        "title_line2": "Heavy Stability or Lightweight Trunk?",
        "accent_color": "#00E5FF",  # Electric Cyan
        "scenes": [1, 2, 9, 10, 11, 12, 13, 30],
        "thumb_scene": 1,
        "thumb_big_text": "HEAVY & STABLE\nor LIGHT & PORTABLE?",
        "thumb_sub_badge": "VOLUME SHOWDOWN: LFP vs NCM",
        "yt_titles": [
            "LFP vs NCM EV Battery: Heavy Stability or Lightweight Swappable Pack? #shorts",
            "Why Are LFP Batteries So Much Bulkier & Heavier Than NCM Packs? #shorts",
            "Buying an Electric Scooter for Apartment Living: LFP vs NCM Battery! #shorts",
        ],
        "yt_description": (
            "Choosing an electric scooter or motorbike starts inside the battery pack: LFP vs NCM. Which chemistry actually fits your daily commute?\n\n"
            "📌 Key Takeaways:\n"
            "• NCM Energy Density: Packs way more energy per cubic centimeter—giving you a spacious under-seat helmet trunk and a lightweight swappable pack to carry upstairs.\n"
            "• LFP Bulk & Stability: Noticeably larger and heavier for the same capacity, but mounting it under the footboard lowers the center of gravity for rock-solid cornering stability.\n\n"
            "👉 Would you pick a lightweight swappable battery (NCM) or rock-solid low-center stability (LFP)? Drop your choice in the comments!\n\n"
            "🔔 Subscribe to Squeezing Tech — “Extracting Value from Everyday Tech”\n\n"
            "#SqueezingTech #LFPvsNCM #EVBattery #ElectricScooter #BatteryTech #ElectricMobility #Shorts"
        ),
        "yt_pinned_comment": "Do you prefer a lightweight removable battery you can carry upstairs (NCM) or a rock-solid floor-mounted pack (LFP)? Let us know below! 👇",
        "thumb_desc": (
            "Side-by-side 2D flat vector comparison on a dark navy blue background (#0B132B): "
            "Left shows a heavy-duty neon lime LFP battery pack (#76FF03) mounted low under a scooter floorboard for stability; "
            "Right shows a compact electric cyan NCM battery pack (#00E5FF) with glowing amber accents (#FFB300) beside a spacious under-seat helmet trunk and portable handle. "
            "Big Hook Text: 'HEAVY & STABLE or LIGHT & PORTABLE?'."
        ),
        "thumb_prompt": (
            "Vertical 9:16 YouTube Shorts thumbnail, premium liquid glass Bento grid tech infographic on a dark navy blue background (#0B132B), "
            "split comparison: left shows a large heavy LFP battery pack in glowing neon lime green (#76FF03) mounted low under an electric scooter floorboard with a stability target icon, "
            "right shows a compact lightweight NCM battery module in electric cyan (#00E5FF) and glowing amber (#FFB300) with a carry handle beside a spacious under-seat trunk fitting two helmets, "
            "minimalist 2D flat vector infographic, sharp glowing geometric vector line art, high contrast, no text, no watermark, no google logo, no gemini logo, no star icon --no 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 9:16"
        ),
    },
    {
        "id": "short_02_thermal_safety",
        "badge": "EPISODE 2 • THERMAL SAFETY & FIRE TEST",
        "title_line1": "PUNCTURED WITH A STEEL NAIL!",
        "title_line2": "Why LFP Batteries Don't Catch Fire",
        "accent_color": "#76FF03",  # Neon Lime Green
        "scenes": [14, 6, 15, 16, 17, 18, 28],
        "thumb_scene": 14,
        "thumb_crop_center_col": True,
        "thumb_big_text": "NAIL PUNCTURE TEST:\nZERO FIRE, ZERO EXPLOSION!",
        "thumb_sub_badge": "THERMAL SAFETY: LFP vs NCM",
        "yt_titles": [
            "Why LFP Batteries Don't Explode When Punctured by a Steel Nail! #shorts",
            "Charging Your EV Overnight at Home? The Truth About LFP vs NCM Safety #shorts",
            "Inside Battery Thermal Runaway: Why LFP Is Practically Fireproof! #shorts",
        ],
        "yt_description": (
            "What happens when an electric vehicle battery is punctured by a steel nail or exposed to extreme heat? The atomic physics of LFP and NCM couldn't be more different.\n\n"
            "📌 Key Takeaways:\n"
            "• Nail Penetration Test: LFP emits only harmless white vapor—no flame, no thermal runaway.\n"
            "• Atomic Fortress: LFP’s rigid olivine crystal lattice holds onto oxygen tightly with indestructible covalent bonds.\n"
            "• NCM Thermal Management: Overheating NCM cathodes can release internal oxygen, requiring advanced BMS circuits and multi-layer thermal barriers to prevent chain-reaction runaway.\n\n"
            "👉 Do you charge your electric two-wheeler overnight at home? Tell us in the comments!\n\n"
            "🔔 Subscribe to Squeezing Tech — “Extracting Value from Everyday Tech”\n\n"
            "#SqueezingTech #BatterySafety #LFPBattery #NCMBattery #ThermalRunaway #EVSafety #Shorts"
        ),
        "yt_pinned_comment": "Do you plug your EV or e-scooter in overnight at home? LFP chemistry gives you 100% peace of mind with zero combustion risk! 🛡️👇",
        "thumb_desc": (
            "Dramatic 2D vector cutaway of the steel nail penetration safety test on a dark navy blue background (#0B132B): "
            "A sharp steel nail punctures a neon lime LFP cell (#76FF03) releasing only harmless white vapor with a glowing green safety shield, "
            "contrasted with an overheating NCM cell releasing red-amber oxygen bubbles (#FFB300). "
            "Big Hook Text: 'NAIL PUNCTURE TEST: ZERO FIRE, ZERO EXPLOSION!'."
        ),
        "thumb_prompt": (
            "Vertical 9:16 YouTube Shorts thumbnail, dramatic 2D flat vector technical schematic on a dark navy blue background (#0B132B), "
            "a sharp steel nail puncturing a glowing neon lime green LFP battery cell (#76FF03) releasing only minimal harmless white vapor lines with a glowing green safety shield icon, "
            "contrasted with a warning thermal runaway radar on an electric cyan and amber-red NCM cell (#00E5FF, #FFB300), "
            "minimalist 2D flat vector infographic, sharp glowing geometric line art, no text, no watermark, no google logo, no gemini logo, no star icon --no 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 9:16"
        ),
    },
    {
        "id": "short_03_riding_and_charging",
        "badge": "EPISODE 3 • PERFORMANCE & CHARGING RULES",
        "title_line1": "CHARGE LFP TO 100%, NCM TO 80%?",
        "title_line2": "Stop Killing Your EV Battery Lifespan!",
        "accent_color": "#FFB300",  # Glowing Amber
        "scenes": [19, 20, 21, 22, 23, 24, 25],
        "thumb_scene": 25,
        "thumb_big_text": "LFP NEEDS 100%\nNCM CAPPED AT 80%?!",
        "thumb_sub_badge": "SMART CHARGING RULES: LFP vs NCM",
        "yt_titles": [
            "Why You Must Charge LFP Batteries to 100%—But Cap NCM at 80%! #shorts",
            "Why Does Your EV Battery Percentage Drop Suddenly? LFP vs NCM Explained #shorts",
            "Stop Using the Same Charging Habit for Every EV Battery! (LFP vs NCM) #shorts",
        ],
        "yt_description": (
            "Using the wrong daily charging habit can either degrade your battery early or make your dashboard meter wildly inaccurate! Here is how LFP and NCM behave on the road and on the charger.\n\n"
            "📌 Key Takeaways:\n"
            "• Ride & Winter Feel: NCM delivers explosive peak current bursts and strong freezing-weather ion flow, while LFP offers calm, steady city cruising.\n"
            "• LFP’s Flat Voltage Curve: Makes state-of-charge hard for the BMS to track -> Rule: Charge LFP to 100% periodically for active cell balancing and calibration!\n"
            "• NCM’s Linear Voltage Slope: Gives predictable battery % readings -> Rule: Cap daily charging at 80% to minimize cell stress and maximize lifespan.\n\n"
            "👉 Has your battery meter ever dropped suddenly while riding? Share your experience below!\n\n"
            "🔔 Subscribe to Squeezing Tech — “Extracting Value from Everyday Tech”\n\n"
            "#SqueezingTech #EVChargingTips #BatteryBMS #LFPvsNCM #BatteryHealth #ElectricScooter #Shorts"
        ),
        "yt_pinned_comment": "Golden Rule to remember: Charge LFP to 100% periodically to calibrate the BMS, and cap NCM at 80% daily to reduce cell stress! 💡👇",
        "thumb_desc": (
            "Dual battery charging gauge infographic on a dark navy blue background (#0B132B): "
            "Top/Left shows a neon lime LFP battery gauge (#76FF03) charged to 100% with active BMS cell balancing arrows; "
            "Bottom/Right shows an electric cyan NCM battery gauge (#00E5FF) capped at the optimal 80% zone with a glowing amber health shield (#FFB300). "
            "Big Hook Text: 'LFP NEEDS 100% / NCM CAPPED AT 80%?!'."
        ),
        "thumb_prompt": (
            "Vertical 9:16 YouTube Shorts thumbnail, 2D flat vector Bento grid infographic on a dark navy blue background (#0B132B), "
            "two large glowing battery charging gauges side by side: left neon lime green LFP battery gauge (#76FF03) filled to top bar with BMS cell balancing checkmark icon, "
            "right electric cyan NCM battery gauge (#00E5FF) capped at 80 percent optimal health zone with a glowing amber shield icon (#FFB300), "
            "minimalist 2D flat vector infographic, sharp glowing geometric vector line art, no text, no watermark, no google logo, no gemini logo, no star icon --no 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 9:16"
        ),
    },
    {
        "id": "short_04_longevity_and_cost",
        "badge": "EPISODE 4 • 3,000 CYCLES & REAL COST",
        "title_line1": "3,000+ CHARGE CYCLES!",
        "title_line2": "The Battery That Outlasts Your Vehicle",
        "accent_color": "#76FF03",  # Neon Lime Green
        "scenes": [26, 4, 5, 27, 28, 29, 30],
        "thumb_scene": 26,
        "thumb_big_text": "3,000+ CYCLES!\nOUTLASTS THE VEHICLE",
        "thumb_sub_badge": "LIFESPAN & COST: LFP vs NCM",
        "yt_titles": [
            "3,000+ Charge Cycles: Why LFP Batteries Outlast the Vehicle Itself! #shorts",
            "LFP vs NCM Total Cost: Which EV Battery Saves You the Most Money? #shorts",
            "Delivery Couriers vs Speed Riders: Should You Buy an LFP or NCM EV? #shorts",
        ],
        "yt_description": (
            "Surviving over 3,000 charge cycles—nearly 8 to 10 years of daily riding—an LFP battery can literally outlast the scooter itself. So when is NCM still worth the premium price?\n\n"
            "📌 Key Takeaways:\n"
            "• LFP Economics: Built from abundant, non-toxic iron and phosphate with 3,000+ cycles, delivering the lowest cost per mile for daily commuters and delivery fleets.\n"
            "• NCM Circular Value: Uses premium nickel and cobalt for extreme performance, and retains high economic value through battery recycling at retirement.\n"
            "• Final Verdict: Pick LFP for unbeatable longevity and overnight peace of mind; pick NCM for high-speed thrills and swappable convenience.\n\n"
            "👉 Team Longevity (LFP) or Team Performance (NCM)—which side are you on? Comment below!\n\n"
            "🔔 Subscribe to Squeezing Tech — “Extracting Value from Everyday Tech”\n\n"
            "#SqueezingTech #BatteryLifespan #LFPvsNCM #EVBattery #CleanTech #ElectricVehicles #Shorts"
        ),
        "yt_pinned_comment": "Over 3,000 charge cycles equals nearly 8–10 years of daily charging! Are you on Team LFP (Longevity) or Team NCM (Performance)? 👇",
        "thumb_desc": (
            "Concept illustration on a dark navy blue background (#0B132B): "
            "A glowing neon lime LFP battery pack (#76FF03) crowned with an infinity lifecycle loop inside an electric scooter silhouette, "
            "flanked by electric cyan (#00E5FF) and glowing amber (#FFB300) cost-per-mile and recycling icons. "
            "Big Hook Text: '3,000+ CYCLES! OUTLASTS THE VEHICLE'."
        ),
        "thumb_prompt": (
            "Vertical 9:16 YouTube Shorts thumbnail, 2D flat vector editorial tech infographic on a dark navy blue background (#0B132B), "
            "a glowing neon lime green LFP battery pack (#76FF03) crowned with a glowing infinity lifecycle symbol inside a sleek electric scooter silhouette, "
            "surrounded by electric cyan (#00E5FF) and glowing amber (#FFB300) circular economy and cost savings icons, "
            "minimalist 2D flat vector infographic, sharp glowing geometric vector line art, no text, no watermark, no google logo, no gemini logo, no star icon --no 3d, realistic, photorealistic, logo, watermark, gemini, google, star, sparkle, text --ar 9:16"
        ),
    },
]


def _load_font(size, bold=True):
    font_candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\tahomabd.ttf" if bold else r"C:\Windows\Fonts\tahoma.ttf",
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def _wrap_text_lines(draw, text, font, max_width):
    words = text.split()
    lines = []
    cur = []
    for w in words:
        test_line = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) <= max_width or not cur:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def create_short_overlay(
    output_png,
    badge_text,
    title_line1,
    title_line2,
    subtitle_text="",
    step_label="",
    accent_hex="#D35400",
):
    """
    Tạo khung overlay 1080x1920 (RGBA) theo chuẩn Kênh Vắt Chanh Công Nghệ (#FAF7F2):
    - Nền vàng kem ấm #FAF7F2
    - Header: Logo kênh + Tên kênh + Bento Title Card
    - Cửa sổ trong suốt ở giữa (x=24..1056, y=555..1135 -> 1032x580 chuẩn 16:9)
    - Khung Bento Phụ đề (y=1175..1545) căn giữa chính xác từng câu thoại
    """
    W, H = 1080, 1920
    bg_cream = (250, 247, 242, 255)      # #FAF7F2
    charcoal = (28, 25, 23, 255)         # #1C1917
    card_white = (255, 253, 249, 255)    # #FFFDF9
    lemon_yellow = (244, 196, 48, 255)   # #F4C430
    terracotta = (211, 84, 0, 255)       # #D35400
    lime_green = (124, 179, 66, 255)     # #7CB342
    muted_gray = (120, 113, 108, 255)

    accent_hex_clean = accent_hex.lstrip("#")
    accent_rgb = tuple(int(accent_hex_clean[i:i+2], 16) for i in (0, 2, 4)) + (255,)

    img = Image.new("RGBA", (W, H), bg_cream)
    draw = ImageDraw.Draw(img)

    # 1. Họa tiết trang trí nhẹ ở góc trên & dưới
    draw.ellipse((-120, -120, 220, 220), fill=(244, 196, 48, 35))
    draw.ellipse((W - 240, H - 360, W + 120, H), fill=(124, 179, 66, 30))

    # 2. Header Brand Pill (y = 115..191)
    logo_path = os.path.join(RESOURCES_DIR, "logo_vi.jpg")
    pill_w, pill_h = 520, 76
    pill_x = (W - pill_w) // 2
    pill_y = 115
    draw.rounded_rectangle(
        (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
        radius=38,
        fill=card_white,
        outline=charcoal,
        width=3,
    )

    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA").resize((56, 56), Image.LANCZOS)
            mask = Image.new("L", (56, 56), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 56, 56), fill=255)
            img.paste(logo, (pill_x + 14, pill_y + 10), mask)
        except Exception:
            pass

    font_brand = _load_font(28, bold=True)
    draw.text((pill_x + 84, pill_y + 21), "VẮT CHANH CÔNG NGHỆ", font=font_brand, fill=charcoal)

    # 3. Bento Title Card (y = 220..515)
    card_x1, card_y1, card_x2, card_y2 = 44, 220, W - 44, 515
    draw.rounded_rectangle(
        (card_x1 + 6, card_y1 + 8, card_x2 + 6, card_y2 + 8),
        radius=28,
        fill=(28, 25, 23, 35),
    )
    draw.rounded_rectangle(
        (card_x1, card_y1, card_x2, card_y2),
        radius=28,
        fill=card_white,
        outline=charcoal,
        width=4,
    )

    # Badge tập (hỗ trợ hiển thị Chủ đề chính + Tập, tự co chữ nếu dài)
    font_badge = _load_font(23, bold=True)
    b_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    if (b_bbox[2] - b_bbox[0]) > (card_x2 - card_x1 - 80):
        font_badge = _load_font(19, bold=True)
        b_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    b_w = (b_bbox[2] - b_bbox[0]) + 44
    b_h = 46
    b_x = (W - b_w) // 2
    b_y = card_y1 + 24
    draw.rounded_rectangle(
        (b_x, b_y, b_x + b_w, b_y + b_h),
        radius=23,
        fill=accent_rgb,
        outline=charcoal,
        width=2,
    )
    badge_fg = charcoal if accent_hex_clean.upper() == "F4C430" else (255, 255, 255, 255)
    text_offset_y = (b_h - (b_bbox[3] - b_bbox[1])) // 2 - b_bbox[1]
    draw.text((b_x + 22, b_y + text_offset_y), badge_text, font=font_badge, fill=badge_fg)

    # Title Line 1
    font_t1 = _load_font(50, bold=True)
    t1_bbox = draw.textbbox((0, 0), title_line1, font=font_t1)
    t1_w = t1_bbox[2] - t1_bbox[0]
    draw.text(((W - t1_w) // 2, card_y1 + 92), title_line1, font=font_t1, fill=terracotta)

    # Title Line 2
    font_t2 = _load_font(36, bold=True)
    t2_bbox = draw.textbbox((0, 0), title_line2, font=font_t2)
    t2_w = t2_bbox[2] - t2_bbox[0]
    if t2_w > (card_x2 - card_x1 - 40):
        font_t2 = _load_font(32, bold=True)
        t2_bbox = draw.textbbox((0, 0), title_line2, font=font_t2)
        t2_w = t2_bbox[2] - t2_bbox[0]
    draw.text(((W - t2_w) // 2, card_y1 + 168), title_line2, font=font_t2, fill=charcoal)

    # Thanh nhấn 3 màu thương hiệu
    bar_w = 240
    bar_x = (W - bar_w) // 2
    bar_y = card_y2 - 28
    draw.rounded_rectangle((bar_x, bar_y, bar_x + 75, bar_y + 8), radius=4, fill=lemon_yellow)
    draw.rounded_rectangle((bar_x + 82, bar_y, bar_x + 157, bar_y + 8), radius=4, fill=terracotta)
    draw.rounded_rectangle((bar_x + 164, bar_y, bar_x + 240, bar_y + 8), radius=4, fill=lime_green)

    # 4. Cửa sổ Video 16:9 ở chính giữa (x = 24..1056, y = 555..1135 -> 1032x580)
    vx1, vy1, vx2, vy2 = 24, 555, 1056, 1135
    draw.rounded_rectangle(
        (vx1 + 6, vy1 + 8, vx2 + 6, vy2 + 8),
        radius=26,
        fill=(28, 25, 23, 45),
    )
    draw.rounded_rectangle(
        (vx1, vy1, vx2, vy2),
        radius=24,
        fill=(0, 0, 0, 0),
        outline=charcoal,
        width=6,
    )

    # 5. Khung Bento chứa Phụ đề (y = 1175..1545)
    sx1, sy1, sx2, sy2 = 44, 1175, W - 44, 1545
    draw.rounded_rectangle(
        (sx1 + 5, sy1 + 6, sx2 + 5, sy2 + 6),
        radius=26,
        fill=(28, 25, 23, 25),
    )
    draw.rounded_rectangle(
        (sx1, sy1, sx2, sy2),
        radius=26,
        fill=card_white,
        outline=charcoal,
        width=3,
    )
    # Nhãn góc trên khung phụ đề
    draw.ellipse((sx1 + 32, sy1 + 22, sx1 + 50, sy1 + 40), fill=lime_green, outline=charcoal, width=2)
    font_sub_tag = _load_font(22, bold=True)
    draw.text((sx1 + 60, sy1 + 19), "ĐIỂM CỐT LÕI", font=font_sub_tag, fill=lime_green)
    if step_label:
        sp_bbox = draw.textbbox((0, 0), step_label, font=font_sub_tag)
        draw.text((sx2 - (sp_bbox[2] - sp_bbox[0]) - 32, sy1 + 19), step_label, font=font_sub_tag, fill=muted_gray)
    draw.line((sx1 + 32, sy1 + 56, sx2 - 32, sy1 + 56), fill=(230, 224, 214, 255), width=2)

    # Vẽ câu thoại căn giữa hoàn hảo trong vùng (sx1+36 .. sx2-36, sy1+64 .. sy2-20)
    if subtitle_text:
        font_sub = _load_font(38, bold=True)
        max_sub_w = (sx2 - sx1) - 72
        lines = _wrap_text_lines(draw, subtitle_text, font_sub, max_sub_w)
        if len(lines) > 4:
            font_sub = _load_font(34, bold=True)
            lines = _wrap_text_lines(draw, subtitle_text, font_sub, max_sub_w)

        line_h = 54
        total_text_h = len(lines) * line_h
        avail_y1 = sy1 + 64
        avail_y2 = sy2 - 16
        start_y = avail_y1 + max(0, (avail_y2 - avail_y1 - total_text_h) // 2)

        for idx_l, line_str in enumerate(lines):
            lb = draw.textbbox((0, 0), line_str, font=font_sub)
            lw = lb[2] - lb[0]
            lx = sx1 + ((sx2 - sx1) - lw) // 2
            ly = start_y + idx_l * line_h
            draw.text((lx, ly), line_str, font=font_sub, fill=charcoal)

    # 6. Footer Slogan (y = 1585..1650)
    font_slogan = _load_font(25, bold=False)
    slogan_txt = "“Vắt sạch thông số, giữ lại cách dùng”"
    s_bbox = draw.textbbox((0, 0), slogan_txt, font=font_slogan)
    s_w = s_bbox[2] - s_bbox[0]
    draw.text(((W - s_w) // 2, 1590), slogan_txt, font=font_slogan, fill=muted_gray)

    img.save(output_png, "PNG")
    return (vx1, vy1, vx2 - vx1, vy2 - vy1)


def _draw_squeezing_tech_emblem(draw, cx, cy, r=28):
    """Vẽ biểu tượng lõi pin tròn phát sáng chuẩn nhận diện kênh Squeezing Tech."""
    navy_dark = (11, 19, 43, 255)
    neon_lime = (118, 255, 3, 255)
    elec_cyan = (0, 229, 255, 255)
    amber = (255, 179, 0, 255)

    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=navy_dark, outline=neon_lime, width=3)
    # Thân pin ở tâm
    bw, bh = 20, 28
    bx1, by1 = cx - bw // 2, cy - bh // 2 + 2
    bx2, by2 = cx + bw // 2, cy + bh // 2 + 2
    draw.rounded_rectangle((bx1, by1, bx2, by2), radius=4, fill=navy_dark, outline=elec_cyan, width=2)
    # Đầu cực dương
    draw.rectangle((cx - 5, by1 - 4, cx + 5, by1), fill=elec_cyan)
    # 3 vạch năng lượng phát sáng
    draw.rectangle((bx1 + 4, by2 - 7, bx2 - 4, by2 - 4), fill=neon_lime)
    draw.rectangle((bx1 + 4, by2 - 14, bx2 - 4, by2 - 11), fill=neon_lime)
    draw.rectangle((bx1 + 4, by2 - 21, bx2 - 4, by2 - 18), fill=amber)


def create_short_overlay_en(
    output_png,
    badge_text,
    title_line1,
    title_line2,
    subtitle_text="",
    step_label="",
    accent_hex="#00E5FF",
):
    """
    Tạo khung overlay 1080x1920 (RGBA) chuẩn Kênh Tiếng Anh Squeezing Tech (#0B132B):
    - Nền xanh đen thẫm #0B132B
    - Header: Biểu tượng năng lượng tròn + SQUEEZING TECH + Bento Title Card
    - Cửa sổ trong suốt ở giữa (x=24..1056, y=555..1135 -> 1032x580 chuẩn 16:9)
    - Khung Bento Phụ đề (y=1175..1545) căn giữa chính xác từng câu thoại
    """
    W, H = 1080, 1920
    bg_navy = (11, 19, 43, 255)          # #0B132B
    card_slate = (19, 31, 66, 255)       # #131F42
    neon_lime = (118, 255, 3, 255)       # #76FF03
    elec_cyan = (0, 229, 255, 255)       # #00E5FF
    amber = (255, 179, 0, 255)           # #FFB300
    white_text = (248, 250, 252, 255)    # #F8FAFC
    muted_slate = (148, 163, 184, 255)   # #94A3B8

    accent_hex_clean = accent_hex.lstrip("#")
    accent_rgb = tuple(int(accent_hex_clean[i:i+2], 16) for i in (0, 2, 4)) + (255,)

    img = Image.new("RGBA", (W, H), bg_navy)
    draw = ImageDraw.Draw(img)

    # 1. Họa tiết quầng sáng công nghệ ở góc trên & dưới
    draw.ellipse((-120, -120, 240, 240), fill=(13, 42, 76, 255))
    draw.ellipse((W - 240, H - 360, W + 120, H), fill=(18, 46, 52, 255))

    # 2. Header Brand Pill (y = 115..191)
    pill_w, pill_h = 460, 76
    pill_x = (W - pill_w) // 2
    pill_y = 115
    draw.rounded_rectangle(
        (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
        radius=38,
        fill=card_slate,
        outline=elec_cyan,
        width=3,
    )
    _draw_squeezing_tech_emblem(draw, pill_x + 44, pill_y + 38, r=26)

    font_brand = _load_font(30, bold=True)
    draw.text((pill_x + 86, pill_y + 20), "SQUEEZING TECH", font=font_brand, fill=elec_cyan)

    # 3. Bento Title Card (y = 220..515)
    card_x1, card_y1, card_x2, card_y2 = 44, 220, W - 44, 515
    draw.rounded_rectangle(
        (card_x1 + 6, card_y1 + 8, card_x2 + 6, card_y2 + 8),
        radius=28,
        fill=(5, 10, 24, 255),
    )
    draw.rounded_rectangle(
        (card_x1, card_y1, card_x2, card_y2),
        radius=28,
        fill=card_slate,
        outline=elec_cyan,
        width=3,
    )

    # Episode Badge (hỗ trợ hiển thị Main Topic + Episode, tự co chữ nếu dài)
    font_badge = _load_font(22, bold=True)
    b_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    if (b_bbox[2] - b_bbox[0]) > (card_x2 - card_x1 - 80):
        font_badge = _load_font(19, bold=True)
        b_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    b_w = (b_bbox[2] - b_bbox[0]) + 44
    b_h = 46
    b_x = (W - b_w) // 2
    b_y = card_y1 + 24
    draw.rounded_rectangle(
        (b_x, b_y, b_x + b_w, b_y + b_h),
        radius=23,
        fill=accent_rgb,
        outline=bg_navy,
        width=2,
    )
    text_offset_y = (b_h - (b_bbox[3] - b_bbox[1])) // 2 - b_bbox[1]
    draw.text((b_x + 22, b_y + text_offset_y), badge_text, font=font_badge, fill=bg_navy)

    # Title Line 1
    font_t1 = _load_font(46, bold=True)
    t1_bbox = draw.textbbox((0, 0), title_line1, font=font_t1)
    t1_w = t1_bbox[2] - t1_bbox[0]
    if t1_w > (card_x2 - card_x1 - 36):
        font_t1 = _load_font(40, bold=True)
        t1_bbox = draw.textbbox((0, 0), title_line1, font=font_t1)
        t1_w = t1_bbox[2] - t1_bbox[0]
    draw.text(((W - t1_w) // 2, card_y1 + 92), title_line1, font=font_t1, fill=neon_lime)

    # Title Line 2
    font_t2 = _load_font(34, bold=True)
    t2_bbox = draw.textbbox((0, 0), title_line2, font=font_t2)
    t2_w = t2_bbox[2] - t2_bbox[0]
    if t2_w > (card_x2 - card_x1 - 40):
        font_t2 = _load_font(30, bold=True)
        t2_bbox = draw.textbbox((0, 0), title_line2, font=font_t2)
        t2_w = t2_bbox[2] - t2_bbox[0]
    draw.text(((W - t2_w) // 2, card_y1 + 168), title_line2, font=font_t2, fill=white_text)

    # Thanh nhấn 3 màu thương hiệu
    bar_w = 240
    bar_x = (W - bar_w) // 2
    bar_y = card_y2 - 28
    draw.rounded_rectangle((bar_x, bar_y, bar_x + 75, bar_y + 8), radius=4, fill=neon_lime)
    draw.rounded_rectangle((bar_x + 82, bar_y, bar_x + 157, bar_y + 8), radius=4, fill=elec_cyan)
    draw.rounded_rectangle((bar_x + 164, bar_y, bar_x + 240, bar_y + 8), radius=4, fill=amber)

    # 4. Cửa sổ Video 16:9 ở chính giữa (x = 24..1056, y = 555..1135 -> 1032x580)
    vx1, vy1, vx2, vy2 = 24, 555, 1056, 1135
    draw.rounded_rectangle(
        (vx1 + 6, vy1 + 8, vx2 + 6, vy2 + 8),
        radius=26,
        fill=(0, 0, 0, 110),
    )
    draw.rounded_rectangle(
        (vx1, vy1, vx2, vy2),
        radius=24,
        fill=(0, 0, 0, 0),
        outline=elec_cyan,
        width=5,
    )

    # 5. Khung Bento chứa Phụ đề (y = 1175..1545)
    sx1, sy1, sx2, sy2 = 44, 1175, W - 44, 1545
    draw.rounded_rectangle(
        (sx1 + 5, sy1 + 6, sx2 + 5, sy2 + 6),
        radius=26,
        fill=(0, 0, 0, 85),
    )
    draw.rounded_rectangle(
        (sx1, sy1, sx2, sy2),
        radius=26,
        fill=card_slate,
        outline=elec_cyan,
        width=3,
    )
    # Nhãn góc trên khung phụ đề
    draw.ellipse((sx1 + 32, sy1 + 22, sx1 + 50, sy1 + 40), fill=neon_lime)
    font_sub_tag = _load_font(22, bold=True)
    draw.text((sx1 + 60, sy1 + 19), "KEY TAKEAWAY", font=font_sub_tag, fill=neon_lime)
    if step_label:
        sp_bbox = draw.textbbox((0, 0), step_label, font=font_sub_tag)
        draw.text((sx2 - (sp_bbox[2] - sp_bbox[0]) - 32, sy1 + 19), step_label, font=font_sub_tag, fill=muted_slate)
    draw.line((sx1 + 32, sy1 + 56, sx2 - 32, sy1 + 56), fill=(38, 56, 105, 255), width=2)

    # Vẽ câu thoại căn giữa hoàn hảo
    if subtitle_text:
        font_sub = _load_font(38, bold=True)
        max_sub_w = (sx2 - sx1) - 72
        lines = _wrap_text_lines(draw, subtitle_text, font_sub, max_sub_w)
        if len(lines) > 4:
            font_sub = _load_font(34, bold=True)
            lines = _wrap_text_lines(draw, subtitle_text, font_sub, max_sub_w)

        line_h = 54
        total_text_h = len(lines) * line_h
        avail_y1 = sy1 + 64
        avail_y2 = sy2 - 16
        start_y = avail_y1 + max(0, (avail_y2 - avail_y1 - total_text_h) // 2)

        for idx_l, line_str in enumerate(lines):
            lb = draw.textbbox((0, 0), line_str, font=font_sub)
            lw = lb[2] - lb[0]
            lx = sx1 + ((sx2 - sx1) - lw) // 2
            ly = start_y + idx_l * line_h
            draw.text((lx, ly), line_str, font=font_sub, fill=white_text)

    # 6. Footer Slogan (y = 1585..1650)
    font_slogan = _load_font(25, bold=False)
    slogan_txt = "“Extracting Value from Everyday Tech”"
    s_bbox = draw.textbbox((0, 0), slogan_txt, font=font_slogan)
    s_w = s_bbox[2] - s_bbox[0]
    draw.text(((W - s_w) // 2, 1590), slogan_txt, font=font_slogan, fill=muted_slate)

    img.save(output_png, "PNG")
    return (vx1, vy1, vx2 - vx1, vy2 - vy1)


def _render_short_scene(order_idx, media_path, audio_path, dur, overlay_png, box_rect, fps, temp_dir, bg_hex="#FAF7F2"):
    vx, vy, vw, vh = box_rect
    clip_path = os.path.join(temp_dir, f"short_clip_{order_idx:02d}.mp4")
    ext = os.path.splitext(media_path)[1].lower()
    is_vid = ext in {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}

    if is_vid:
        filter_complex = (
            f"[0:v]scale={vw}:{vh}:force_original_aspect_ratio=increase,crop={vw}:{vh},fps={fps}[vid];"
            f"color=c={bg_hex}:s=1080x1920:r={fps}[bg];"
            f"[bg][vid]overlay={vx}:{vy}:shortest=1[tmp];"
            f"[tmp][2:v]overlay=0:0:shortest=1,format=yuv420p[outv]"
        )
        cmd = [
            FFMPEG_PATH, "-y",
            "-stream_loop", "-1",
            "-t", f"{dur:.3f}",
            "-i", media_path,
            "-i", audio_path,
            "-loop", "1", "-t", f"{dur:.3f}", "-i", overlay_png,
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest",
            clip_path,
        ]
    else:
        total_frames = max(1, int(dur * fps))
        max_zoom = 1.06
        step = (max_zoom - 1.00) / max(1, total_frames)
        if order_idx % 2 == 1:
            zoom_expr = f"min(zoom+{step:.6f},{max_zoom})"
        else:
            zoom_expr = f"max({max_zoom}-on*{step:.6f},1.00)"

        filter_complex = (
            f"[0:v]scale={vw}:{vh}:force_original_aspect_ratio=increase,crop={vw}:{vh},"
            f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={vw}x{vh}:fps={fps}[vid];"
            f"color=c={bg_hex}:s=1080x1920:r={fps}[bg];"
            f"[bg][vid]overlay={vx}:{vy}:shortest=1[tmp];"
            f"[tmp][2:v]overlay=0:0:shortest=1,format=yuv420p[outv]"
        )
        cmd = [
            FFMPEG_PATH, "-y",
            "-loop", "1", "-t", f"{dur:.3f}", "-i", media_path,
            "-i", audio_path,
            "-loop", "1", "-t", f"{dur:.3f}", "-i", overlay_png,
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest",
            clip_path,
        ]

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg error on short scene {order_idx}: {res.stderr[-400:]}")
    return clip_path


def build_shorts_for_project(proj_name="lfp_vs_ncm", lang="vi"):
    proj_dir = os.path.join(PROJECTS_DIR, proj_name)
    if lang == "en":
        script_path = os.path.join(proj_dir, "script_en.txt")
        media_dir = os.path.join(proj_dir, "imgs-clean")
        audio_dir = os.path.join(proj_dir, "audio")
        shorts_out_dir = os.path.join(proj_dir, "shorts_en")
        configs = SHORTS_CONFIG_EN
        bg_hex = "#0B132B"
    else:
        script_path = os.path.join(proj_dir, "script_vi.txt")
        media_dir = os.path.join(proj_dir, "video_vi")
        audio_dir = os.path.join(proj_dir, "audio_vi")
        shorts_out_dir = os.path.join(proj_dir, "shorts_vi")
        configs = SHORTS_CONFIG
        bg_hex = "#FAF7F2"

    os.makedirs(shorts_out_dir, exist_ok=True)

    all_lines = load_script(script_path)
    all_media = get_sorted_images(media_dir)

    if len(all_lines) != len(all_media):
        raise ValueError(f"Số câu thoại ({len(all_lines)}) khác số media ({len(all_media)})")

    generated_files = []

    for cfg in configs:
        short_id = cfg["id"]
        scene_nums = cfg["scenes"]
        print(f"\n========================================================")
        print(f"ĐANG DỰNG YOUTUBE SHORT [{lang.upper()}]: {short_id}")
        print(f"Các cảnh ghép: {scene_nums}")
        print(f"========================================================")

        temp_dir = os.path.join(shorts_out_dir, f"_temp_{short_id}")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            selected_audio_items = []
            selected_media_paths = []
            for order_idx, sc_num in enumerate(scene_nums, 1):
                text = all_lines[sc_num - 1]
                audio_p = os.path.join(audio_dir, f"{sc_num:02d}_voice.mp3")
                media_p = all_media[sc_num - 1]
                selected_audio_items.append({
                    "index": order_idx,
                    "scene_num": sc_num,
                    "text": text,
                    "audio_path": audio_p,
                })
                selected_media_paths.append(media_p)

            srt_out = os.path.join(temp_dir, f"{short_id}.srt")
            enriched_items = generate_subtitles(selected_audio_items, srt_out)

            txt_out = os.path.join(shorts_out_dir, f"{short_id}_script.txt")
            scene_word = "Scene" if lang == "en" else "Cảnh"
            with open(txt_out, "w", encoding="utf-8") as f_txt:
                f_txt.write(f"# {cfg['badge']} - {cfg['title_line1']}: {cfg['title_line2']}\n")
                for item in enriched_items:
                    f_txt.write(f"{item['index']:02d} ({scene_word} {item['scene_num']:02d}). {item['text']}\n")

            tasks = []
            total_sc = len(enriched_items)
            with ThreadPoolExecutor(max_workers=4) as executor:
                for i, item in enumerate(enriched_items):
                    order_idx = i + 1
                    scene_overlay_png = os.path.join(temp_dir, f"overlay_{order_idx:02d}.png")
                    if lang == "en":
                        box_rect = create_short_overlay_en(
                            scene_overlay_png,
                            cfg["badge"],
                            cfg["title_line1"],
                            cfg["title_line2"],
                            subtitle_text=item["text"],
                            step_label=f"Scene {order_idx}/{total_sc}",
                            accent_hex=cfg["accent_color"],
                        )
                    else:
                        box_rect = create_short_overlay(
                            scene_overlay_png,
                            cfg["badge"],
                            cfg["title_line1"],
                            cfg["title_line2"],
                            subtitle_text=item["text"],
                            step_label=f"Cảnh {order_idx}/{total_sc}",
                            accent_hex=cfg["accent_color"],
                        )
                    fut = executor.submit(
                        _render_short_scene,
                        order_idx,
                        selected_media_paths[i],
                        item["audio_path"],
                        item["duration"],
                        scene_overlay_png,
                        box_rect,
                        DEFAULT_FPS,
                        temp_dir,
                        bg_hex,
                    )
                    tasks.append((order_idx, item["scene_num"], item["duration"], fut))

                clip_files = []
                for order_idx, sc_num, dur, fut in tasks:
                    clip_p = fut.result()
                    clip_files.append(clip_p)
                    print(f"  [{scene_word} {order_idx:02d}/{total_sc} - Orig #{sc_num:02d}] {dur:.2f}s -> OK")

            concat_txt = os.path.join(temp_dir, "concat.txt")
            with open(concat_txt, "w", encoding="utf-8") as f_cat:
                for c in clip_files:
                    f_cat.write(f"file '{c.replace(chr(92), '/')}'\n")

            output_mp4 = os.path.join(shorts_out_dir, f"{short_id}.mp4")
            cmd_concat = [
                FFMPEG_PATH, "-y",
                "-f", "concat", "-safe", "0",
                "-i", concat_txt,
                "-c", "copy",
                output_mp4,
            ]
            res = subprocess.run(cmd_concat, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg concat error: {res.stderr[-300:]}")

            total_dur = enriched_items[-1]["end"]
            size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
            print(f"[HOÀN TẤT] {os.path.basename(output_mp4)} | Thời lượng: {total_dur:.1f}s | Dung lượng: {size_mb:.2f} MB")
            generated_files.append((output_mp4, total_dur, size_mb))

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    return generated_files


def render_short_thumbnail(cfg, hero_video_path, output_jpg, temp_dir):
    """
    Render ảnh Thumbnail 1080x1920 (9:16) bắt mắt chuẩn YouTube Shorts cho từng tập:
    - Trích xuất frame nét nhất từ cảnh đắt giá nhất (thumb_scene) trong video_vi
    - Thiết kế Poster dọc với chữ Hook siêu to, độ tương phản cao để thu hút lượt bấm (CTR)
    """
    W, H = 1080, 1920
    bg_cream = (250, 247, 242, 255)      # #FAF7F2
    charcoal = (28, 25, 23, 255)         # #1C1917
    card_white = (255, 253, 249, 255)    # #FFFDF9
    lemon_yellow = (244, 196, 48, 255)   # #F4C430
    terracotta = (211, 84, 0, 255)       # #D35400
    lime_green = (124, 179, 66, 255)     # #7CB342

    accent_hex = cfg["accent_color"].lstrip("#")
    accent_rgb = tuple(int(accent_hex[i:i+2], 16) for i in (0, 2, 4)) + (255,)

    raw_frame_jpg = os.path.join(temp_dir, "hero_frame.jpg")
    subprocess.run(
        [FFMPEG_PATH, "-y", "-ss", "00:00:02.50", "-i", hero_video_path, "-frames:v", "1", "-update", "1", raw_frame_jpg],
        capture_output=True,
    )

    canvas = Image.new("RGBA", (W, H), bg_cream)
    draw = ImageDraw.Draw(canvas)

    # Vòng tròn trang trí nền
    draw.ellipse((-150, -150, 300, 300), fill=(244, 196, 48, 50))
    draw.ellipse((W - 300, H - 420, W + 160, H + 40), fill=(124, 179, 66, 45))

    # 1. Header Thương hiệu (y = 95..180)
    logo_path = os.path.join(RESOURCES_DIR, "logo_vi.jpg")
    pill_w, pill_h = 540, 80
    pill_x = (W - pill_w) // 2
    pill_y = 95
    draw.rounded_rectangle(
        (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
        radius=40,
        fill=card_white,
        outline=charcoal,
        width=4,
    )
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA").resize((60, 60), Image.LANCZOS)
            mask = Image.new("L", (60, 60), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 60, 60), fill=255)
            canvas.paste(logo, (pill_x + 14, pill_y + 10), mask)
        except Exception:
            pass
    font_brand = _load_font(29, bold=True)
    draw.text((pill_x + 88, pill_y + 23), "VẮT CHANH CÔNG NGHỆ", font=font_brand, fill=charcoal)

    # 2. Sub-badge tập (y = 215..275)
    sub_badge = cfg.get("thumb_sub_badge", cfg["badge"])
    font_badge = _load_font(28, bold=True)
    bb = draw.textbbox((0, 0), sub_badge, font=font_badge)
    bw = (bb[2] - bb[0]) + 56
    bh = 56
    bx = (W - bw) // 2
    by = 215
    draw.rounded_rectangle(
        (bx + 4, by + 5, bx + bw + 4, by + bh + 5),
        radius=28,
        fill=(28, 25, 23, 40),
    )
    draw.rounded_rectangle(
        (bx, by, bx + bw, by + bh),
        radius=28,
        fill=accent_rgb,
        outline=charcoal,
        width=3,
    )
    badge_fg = charcoal if accent_hex.upper() == "F4C430" else (255, 255, 255, 255)
    draw.text((bx + 28, by + 11), sub_badge, font=font_badge, fill=badge_fg)

    # 3. Khung ảnh Hero Minh Họa Phóng To ở giữa (y = 310..1120 -> 1016x810)
    vx1, vy1, vx2, vy2 = 32, 310, W - 32, 1120
    vw, vh = vx2 - vx1, vy2 - vy1
    draw.rounded_rectangle(
        (vx1 + 8, vy1 + 10, vx2 + 8, vy2 + 10),
        radius=32,
        fill=(28, 25, 23, 55),
    )
    if os.path.exists(raw_frame_jpg):
        hero_img = Image.open(raw_frame_jpg).convert("RGBA")
        # Phóng nhẹ giữ tâm để hình ảnh pin to, rõ trên thumbnail điện thoại
        hw, hh = hero_img.size
        scale = max(vw / hw, vh / hh)
        new_w, new_h = int(hw * scale), int(hh * scale)
        hero_resized = hero_img.resize((new_w, new_h), Image.LANCZOS)
        crop_x = (new_w - vw) // 2
        crop_y = (new_h - vh) // 2
        hero_cropped = hero_resized.crop((crop_x, crop_y, crop_x + vw, crop_y + vh))

        mask_v = Image.new("L", (vw, vh), 0)
        ImageDraw.Draw(mask_v).rounded_rectangle((0, 0, vw, vh), radius=28, fill=255)
        canvas.paste(hero_cropped, (vx1, vy1), mask_v)

    draw.rounded_rectangle(
        (vx1, vy1, vx2, vy2),
        radius=28,
        fill=None,
        outline=charcoal,
        width=7,
    )

    # 4. Banner Hook Chữ Siêu To phía dưới (y = 1165..1640)
    bx1, by1, bx2, by2 = 36, 1165, W - 36, 1640
    draw.rounded_rectangle(
        (bx1 + 8, by1 + 10, bx2 + 8, by2 + 10),
        radius=32,
        fill=(28, 25, 23, 50),
    )
    draw.rounded_rectangle(
        (bx1, by1, bx2, by2),
        radius=32,
        fill=card_white,
        outline=charcoal,
        width=6,
    )

    # Vẽ dải màu vàng chanh điểm nhấn trên đầu thẻ chữ
    draw.rounded_rectangle(
        (bx1 + 36, by1 + 26, bx2 - 36, by1 + 120),
        radius=20,
        fill=lemon_yellow,
        outline=charcoal,
        width=3,
    )
    font_top_hook = _load_font(48, bold=True)
    t1_str = cfg["title_line1"]
    t1_b = draw.textbbox((0, 0), t1_str, font=font_top_hook)
    draw.text(((W - (t1_b[2] - t1_b[0])) // 2, by1 + 44), t1_str, font=font_top_hook, fill=charcoal)

    # Chữ Big Hook 2 dòng
    big_lines = cfg.get("thumb_big_text", cfg["title_line2"]).split("\n")
    font_big = _load_font(66, bold=True)
    for idx_b, bline in enumerate(big_lines):
        bb_line = draw.textbbox((0, 0), bline, font=font_big)
        if (bb_line[2] - bb_line[0]) > (bx2 - bx1 - 48):
            font_big = _load_font(56, bold=True)
            bb_line = draw.textbbox((0, 0), bline, font=font_big)
        lw = bb_line[2] - bb_line[0]
        ly = by1 + 155 + idx_b * 96
        fill_col = terracotta if idx_b == 0 else lime_green
        draw.text(((W - lw) // 2, ly), bline, font=font_big, fill=fill_col)

    # Phụ đề nhỏ cuối thẻ
    font_sub = _load_font(34, bold=True)
    sub_str = cfg["title_line2"]
    sb = draw.textbbox((0, 0), sub_str, font=font_sub)
    draw.text(((W - (sb[2] - sb[0])) // 2, by2 - 74), sub_str, font=font_sub, fill=charcoal)

    canvas.convert("RGB").save(output_jpg, "JPEG", quality=95)
    return output_jpg


def render_short_thumbnail_en(cfg, hero_media_path, output_jpg, temp_dir):
    """
    Render ảnh Thumbnail 1080x1920 (9:16) chuẩn YouTube Shorts cho kênh Tiếng Anh Squeezing Tech (#0B132B):
    - Nền xanh đen thẫm #0B132B + thẻ Bento xanh slate #131F42 viền cyan/lime phát sáng
    - Hỗ trợ cả file ảnh (.jpg/.png) lẫn video (.mp4)
    - Nếu cfg['thumb_crop_center_col'] == True (như cảnh 3 cột), tự cắt cột trung tâm sắc nét
    """
    W, H = 1080, 1920
    bg_navy = (11, 19, 43, 255)          # #0B132B
    card_slate = (19, 31, 66, 255)       # #131F42
    neon_lime = (118, 255, 3, 255)       # #76FF03
    elec_cyan = (0, 229, 255, 255)       # #00E5FF
    amber = (255, 179, 0, 255)           # #FFB300
    white_text = (248, 250, 252, 255)    # #F8FAFC

    accent_hex = cfg["accent_color"].lstrip("#")
    accent_rgb = tuple(int(accent_hex[i:i+2], 16) for i in (0, 2, 4)) + (255,)

    ext = os.path.splitext(hero_media_path)[1].lower()
    if ext in {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}:
        raw_frame_jpg = os.path.join(temp_dir, "hero_frame_en.jpg")
        subprocess.run(
            [FFMPEG_PATH, "-y", "-ss", "00:00:02.50", "-i", hero_media_path, "-frames:v", "1", "-update", "1", raw_frame_jpg],
            capture_output=True,
        )
    else:
        raw_frame_jpg = hero_media_path

    canvas = Image.new("RGBA", (W, H), bg_navy)
    draw = ImageDraw.Draw(canvas)

    # Quầng sáng công nghệ ở góc
    draw.ellipse((-150, -150, 300, 300), fill=(14, 48, 86, 255))
    draw.ellipse((W - 300, H - 420, W + 160, H + 40), fill=(20, 52, 58, 255))

    # 1. Header Thương hiệu (y = 95..175)
    pill_w, pill_h = 480, 80
    pill_x = (W - pill_w) // 2
    pill_y = 95
    draw.rounded_rectangle(
        (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
        radius=40,
        fill=card_slate,
        outline=elec_cyan,
        width=4,
    )
    _draw_squeezing_tech_emblem(draw, pill_x + 48, pill_y + 40, r=28)
    font_brand = _load_font(31, bold=True)
    draw.text((pill_x + 92, pill_y + 22), "SQUEEZING TECH", font=font_brand, fill=elec_cyan)

    # 2. Sub-badge tập (y = 215..275)
    sub_badge = cfg.get("thumb_sub_badge", cfg["badge"])
    font_badge = _load_font(27, bold=True)
    bb = draw.textbbox((0, 0), sub_badge, font=font_badge)
    bw = (bb[2] - bb[0]) + 56
    bh = 56
    bx = (W - bw) // 2
    by = 215
    draw.rounded_rectangle(
        (bx + 4, by + 5, bx + bw + 4, by + bh + 5),
        radius=28,
        fill=(5, 10, 24, 255),
    )
    draw.rounded_rectangle(
        (bx, by, bx + bw, by + bh),
        radius=28,
        fill=accent_rgb,
        outline=bg_navy,
        width=3,
    )
    draw.text((bx + 28, by + 12), sub_badge, font=font_badge, fill=bg_navy)

    # 3. Khung ảnh Hero Minh Họa ở giữa (y = 310..1120 -> 1016x810)
    vx1, vy1, vx2, vy2 = 32, 310, W - 32, 1120
    vw, vh = vx2 - vx1, vy2 - vy1
    draw.rounded_rectangle(
        (vx1 + 8, vy1 + 10, vx2 + 8, vy2 + 10),
        radius=32,
        fill=(5, 10, 24, 255),
    )
    if os.path.exists(raw_frame_jpg):
        hero_img = Image.open(raw_frame_jpg).convert("RGBA")
        hw, hh = hero_img.size
        if cfg.get("thumb_crop_center_col"):
            # Cắt cột giữa (x = 32%..68%) và đặt trên nền xanh đen #0B132B
            c_x1 = int(hw * 0.325)
            c_x2 = int(hw * 0.675)
            col_img = hero_img.crop((c_x1, 0, c_x2, hh))
            cw, ch = col_img.size
            scale = min(vw / cw, vh / ch) * 0.96
            nw, nh = int(cw * scale), int(ch * scale)
            col_resized = col_img.resize((nw, nh), Image.LANCZOS)
            hero_cropped = Image.new("RGBA", (vw, vh), bg_navy)
            hero_cropped.paste(col_resized, ((vw - nw) // 2, (vh - nh) // 2))
        else:
            scale = max(vw / hw, vh / hh)
            new_w, new_h = int(hw * scale), int(hh * scale)
            hero_resized = hero_img.resize((new_w, new_h), Image.LANCZOS)
            crop_x = (new_w - vw) // 2
            crop_y = (new_h - vh) // 2
            hero_cropped = hero_resized.crop((crop_x, crop_y, crop_x + vw, crop_y + vh))

        mask_v = Image.new("L", (vw, vh), 0)
        ImageDraw.Draw(mask_v).rounded_rectangle((0, 0, vw, vh), radius=28, fill=255)
        canvas.paste(hero_cropped, (vx1, vy1), mask_v)

    draw.rounded_rectangle(
        (vx1, vy1, vx2, vy2),
        radius=28,
        fill=None,
        outline=elec_cyan,
        width=6,
    )

    # 4. Banner Hook Chữ Siêu To phía dưới (y = 1165..1640)
    bx1, by1, bx2, by2 = 36, 1165, W - 36, 1640
    draw.rounded_rectangle(
        (bx1 + 8, by1 + 10, bx2 + 8, by2 + 10),
        radius=32,
        fill=(5, 10, 24, 255),
    )
    draw.rounded_rectangle(
        (bx1, by1, bx2, by2),
        radius=32,
        fill=card_slate,
        outline=neon_lime,
        width=5,
    )

    # Dải màu vàng hổ phách / xanh neon trên đầu thẻ chữ
    draw.rounded_rectangle(
        (bx1 + 36, by1 + 26, bx2 - 36, by1 + 120),
        radius=20,
        fill=amber,
        outline=bg_navy,
        width=3,
    )
    font_top_hook = _load_font(44, bold=True)
    t1_str = cfg["title_line1"]
    t1_b = draw.textbbox((0, 0), t1_str, font=font_top_hook)
    if (t1_b[2] - t1_b[0]) > (bx2 - bx1 - 90):
        font_top_hook = _load_font(38, bold=True)
        t1_b = draw.textbbox((0, 0), t1_str, font=font_top_hook)
    draw.text(((W - (t1_b[2] - t1_b[0])) // 2, by1 + 48), t1_str, font=font_top_hook, fill=bg_navy)

    # Chữ Big Hook 2 dòng
    big_lines = cfg.get("thumb_big_text", cfg["title_line2"]).split("\n")
    for idx_b, bline in enumerate(big_lines):
        font_big = _load_font(62, bold=True)
        bb_line = draw.textbbox((0, 0), bline, font=font_big)
        if (bb_line[2] - bb_line[0]) > (bx2 - bx1 - 48):
            font_big = _load_font(50, bold=True)
            bb_line = draw.textbbox((0, 0), bline, font=font_big)
        lw = bb_line[2] - bb_line[0]
        ly = by1 + 158 + idx_b * 94
        fill_col = neon_lime if idx_b == 0 else elec_cyan
        draw.text(((W - lw) // 2, ly), bline, font=font_big, fill=fill_col)

    # Phụ đề nhỏ cuối thẻ
    font_sub = _load_font(33, bold=True)
    sub_str = cfg["title_line2"]
    sb = draw.textbbox((0, 0), sub_str, font=font_sub)
    draw.text(((W - (sb[2] - sb[0])) // 2, by2 - 74), sub_str, font=font_sub, fill=white_text)

    canvas.convert("RGB").save(output_jpg, "JPEG", quality=95)
    return output_jpg


def generate_metadata_and_thumbnails(proj_name="lfp_vs_ncm", lang="vi"):
    proj_dir = os.path.join(PROJECTS_DIR, proj_name)
    if lang == "en":
        media_dir = os.path.join(proj_dir, "imgs-clean")
        shorts_out_dir = os.path.join(proj_dir, "shorts_en")
        configs = SHORTS_CONFIG_EN
        summary_md_path = os.path.join(shorts_out_dir, "TONG_HOP_DANG_SHORTS_EN.md")
    else:
        media_dir = os.path.join(proj_dir, "video_vi")
        shorts_out_dir = os.path.join(proj_dir, "shorts_vi")
        configs = SHORTS_CONFIG
        summary_md_path = os.path.join(shorts_out_dir, "TONG_HOP_DANG_SHORTS.md")

    os.makedirs(shorts_out_dir, exist_ok=True)
    all_media = get_sorted_images(media_dir)

    md_lines = [
        f"# BỘ TIÊU ĐỀ, MÔ TẢ & THUMBNAIL ĐĂNG YOUTUBE SHORTS [{lang.upper()}] (LFP vs NCM)",
        "",
        f"Tất cả file video `.mp4`, ảnh thu nhỏ `*_thumb.jpg` và nội dung đăng bài nằm tại thư mục `projects/lfp_vs_ncm/{os.path.basename(shorts_out_dir)}/`.",
        "",
    ]

    temp_dir = os.path.join(shorts_out_dir, "_temp_thumbs")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        for idx, cfg in enumerate(configs, 1):
            short_id = cfg["id"]
            thumb_sc = cfg.get("thumb_scene", cfg["scenes"][0])
            hero_media = all_media[thumb_sc - 1]
            thumb_jpg = os.path.join(shorts_out_dir, f"{short_id}_thumb.jpg")

            if lang == "en":
                render_short_thumbnail_en(cfg, hero_media, thumb_jpg, temp_dir)
            else:
                render_short_thumbnail(cfg, hero_media, thumb_jpg, temp_dir)
            print(f"[THUMBNAIL OK] {os.path.basename(thumb_jpg)}")

            meta_txt = os.path.join(shorts_out_dir, f"{short_id}_dang_bai.txt")
            with open(meta_txt, "w", encoding="utf-8") as f:
                f.write(f"============================================================\n")
                f.write(f"{cfg['badge']} — {cfg['title_line1']}\n")
                f.write(f"File Video    : {short_id}.mp4\n")
                f.write(f"File Thumbnail: {short_id}_thumb.jpg\n")
                f.write(f"============================================================\n\n")
                f.write("1. TIÊU ĐỀ GỢI Ý (Chọn 1 trong 3):\n")
                for t_i, t_str in enumerate(cfg["yt_titles"], 1):
                    f.write(f"   Phương án {t_i}: {t_str}\n")
                f.write("\n2. MÔ TẢ VIDEO (Copy dán vào ô Description):\n")
                f.write("------------------------------------------------------------\n")
                f.write(cfg["yt_description"] + "\n")
                f.write("------------------------------------------------------------\n\n")
                f.write("3. BÌNH LUẬN GHIM (Pinned Comment tăng tương tác):\n")
                f.write(f"   {cfg['yt_pinned_comment']}\n\n")
                f.write("4. MÔ TẢ ẢNH THU NHỎ (Thumbnail Concept & Prompt AI):\n")
                f.write(f"   - Bố cục: {cfg['thumb_desc']}\n")
                f.write(f"   - Prompt AI (9:16): {cfg['thumb_prompt']}\n")

            md_lines.extend([
                f"---",
                f"## {idx}. {cfg['badge']} (`{short_id}.mp4`)",
                f"- **File Video**: `{short_id}.mp4`",
                f"- **File Ảnh Thu Nhỏ (Thumbnail đã render)**: `{short_id}_thumb.jpg`",
                f"- **File Text Đăng Bài**: `{short_id}_dang_bai.txt`",
                "",
                "### Tiêu đề gợi ý (Chọn 1):",
                *[f"{i}. `{t}`" for i, t in enumerate(cfg["yt_titles"], 1)],
                "",
                "### Mô tả Video (Description):",
                "```text",
                cfg["yt_description"],
                "```",
                "",
                "### Bình luận ghim (Pinned Comment):",
                f"> {cfg['yt_pinned_comment']}",
                "",
                "### Mô tả Ảnh thu nhỏ (Thumbnail) & Prompt:",
                f"- **Mô tả bố cục**: {cfg['thumb_desc']}",
                f"- **Prompt AI (nếu muốn sinh thêm qua Google Flow / AI Artist)**:",
                "```text",
                cfg["thumb_prompt"],
                "```",
                "",
            ])
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    with open(summary_md_path, "w", encoding="utf-8") as f_md:
        f_md.write("\n".join(md_lines))
    print(f"[METADATA OK] Đã xuất cẩm nang đăng bài: {summary_md_path}")


if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    lang_arg = "en" if "--en" in sys.argv or "en" in sys.argv else "vi"
    if "--meta-only" in sys.argv:
        generate_metadata_and_thumbnails("lfp_vs_ncm", lang=lang_arg)
    else:
        build_shorts_for_project("lfp_vs_ncm", lang=lang_arg)
        generate_metadata_and_thumbnails("lfp_vs_ncm", lang=lang_arg)
