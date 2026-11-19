import time
import os
import sys
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

# Force UTF-8 encoding on standard I/O for Windows consoles/pipes
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def log_msg(tag, msg):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{tag}] {msg}", flush=True)

# 1. Cấu hình
DEFAULT_PROMPT_FILE = "prompts_battery_infographic.txt"
if len(sys.argv) > 1:
    PROMPT_FILE = sys.argv[1]
else:
    if os.path.exists("prompts.txt"):
        PROMPT_FILE = "prompts.txt"
    elif os.path.exists(DEFAULT_PROMPT_FILE):
        PROMPT_FILE = DEFAULT_PROMPT_FILE
    else:
        PROMPT_FILE = "prompts.txt"

GOOGLE_FLOW_URL = "https://flow.google/"
WAIT_MIN = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 25
WAIT_MAX = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 40
if WAIT_MIN < 1:
    WAIT_MIN = 1
if WAIT_MAX < WAIT_MIN:
    WAIT_MAX = WAIT_MIN
READY_FLAG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".bot_ready")

# Xóa cờ sẵn sàng cũ nếu còn tồn tại
if os.path.exists(READY_FLAG_FILE):
    try:
        os.remove(READY_FLAG_FILE)
    except Exception:
        pass

# 2. Đọc file prompt
if not os.path.exists(PROMPT_FILE):
    log_msg("LỖI", f"Không tìm thấy file prompt '{PROMPT_FILE}'!")
    sys.exit(1)

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    prompts = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

if not prompts:
    log_msg("LỖI", f"File prompt '{PROMPT_FILE}' rỗng hoặc toàn dòng ghi chú (#)!")
    sys.exit(1)

log_msg("THÔNG TIN", f"Đã nạp thành công {len(prompts)} câu prompt từ '{os.path.basename(PROMPT_FILE)}' (Thời gian chờ: {WAIT_MIN}s - {WAIT_MAX}s).")


def find_flow_input(page):
    """
    Tìm chính xác ô 'What do you want to create?' ở góc dưới màn hình Google Flow
    """
    selectors = [
        'textarea[placeholder*="What do you want to create" i]',
        'input[placeholder*="What do you want to create" i]',
        '[placeholder*="What do you want to create" i]',
        'div[contenteditable="true"]:visible',
        'textarea:visible:not([name*="recaptcha"])'
    ]

    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0 and loc.is_visible():
                return loc
        except Exception:
            pass

    try:
        active = page.evaluate("() => document.activeElement && document.activeElement.tagName !== 'BODY'")
        if active:
            return page.locator("*:focus")
    except Exception:
        pass

    return None


def click_send_button(page, input_box):
    """
    Nhấn nút mũi tên gửi (hoặc phím Enter) trên thanh công cụ tạo của Flow
    """
    sent = False
    try:
        input_box.press("Enter")
        time.sleep(0.4)
        sent = True
    except Exception:
        pass

    arrow_buttons = [
        'button:has(svg):right-of(:focus)',
        'div:has(> [placeholder*="create" i]) button',
        'button[aria-label*="Send" i]',
        'button[aria-label*="Submit" i]'
    ]
    for btn_sel in arrow_buttons:
        try:
            btn = page.locator(btn_sel).last
            if btn.count() > 0 and btn.is_visible():
                btn.click(timeout=1000)
                sent = True
                break
        except Exception:
            pass
    return sent


def inject_ready_button(page):
    """
    Hiển thị nút Sẵn Sàng nổi trên đỉnh trình duyệt Google Flow
    """
    try:
        page.evaluate("""
            () => {
                if (document.getElementById('bot-ready-btn-overlay')) return;
                const btn = document.createElement('button');
                btn.id = 'bot-ready-btn-overlay';
                btn.innerHTML = '🚀 BẤM VÀO ĐÂY KHI BẠN ĐÃ SẴN SÀNG CHẠY PROMPT';
                btn.style.position = 'fixed';
                btn.style.top = '18px';
                btn.style.left = '50%';
                btn.style.transform = 'translateX(-50%)';
                btn.style.zIndex = '2147483647';
                btn.style.padding = '12px 26px';
                btn.style.backgroundColor = '#16a34a';
                btn.style.color = '#ffffff';
                btn.style.border = '2px solid #ffffff';
                btn.style.borderRadius = '30px';
                btn.style.fontSize = '15px';
                btn.style.fontWeight = 'bold';
                btn.style.cursor = 'pointer';
                btn.style.boxShadow = '0 6px 22px rgba(0,0,0,0.6)';
                btn.style.transition = 'all 0.2s ease';

                const style = document.createElement('style');
                style.id = 'bot-ready-btn-style';
                style.innerHTML = `
                    @keyframes pulseReady {
                        0% { transform: translateX(-50%) scale(1); box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.7); }
                        70% { transform: translateX(-50%) scale(1.05); box-shadow: 0 0 0 14px rgba(22, 163, 74, 0); }
                        100% { transform: translateX(-50%) scale(1); box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }
                    }
                    #bot-ready-btn-overlay {
                        animation: pulseReady 1.8s infinite;
                    }
                `;
                if (!document.getElementById('bot-ready-btn-style')) {
                    document.head.appendChild(style);
                }
                btn.onclick = () => {
                    window.__BOT_IS_READY__ = true;
                    btn.innerHTML = '⏳ Đang khởi động nạp Prompt...';
                    btn.style.backgroundColor = '#0284c7';
                };
                document.body.appendChild(btn);
            }
        """)
    except Exception:
        pass


# 3. Khởi chạy Playwright
log_msg("BƯỚC 1/4", "Khởi động trình duyệt Google Chrome với hồ sơ đăng nhập (user_data)...")
try:
    with sync_playwright() as p:
        user_data_path = os.path.abspath("./user_data")
        os.makedirs(user_data_path, exist_ok=True)

        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_path,
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-first-run",
                "--no-default-browser-check"
            ],
            ignore_default_args=["--enable-automation"],
            no_viewport=True,
        )

        page = context.pages[0] if context.pages else context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        log_msg("BƯỚC 2/4", f"Đang truy cập Google Flow: {GOOGLE_FLOW_URL} ...")
        page.goto(GOOGLE_FLOW_URL, timeout=60000)
        time.sleep(4)

        log_msg("BƯỚC 3/4", "Tìm ô nhập Prompt 'What do you want to create?' trên Flow...")
        input_box = None
        max_wait = 300
        poll_step = 3
        
        for elapsed in range(0, max_wait, poll_step):
            input_box = find_flow_input(page)
            if input_box:
                log_msg("THÀNH CÔNG", "Đã kết nối trực tiếp với ô nhập Prompt của Google Flow!")
                break

            if elapsed == 0:
                log_msg("CHỜ ĐĂNG NHẬP", "Chưa thấy ô nhập Prompt. Vui lòng đăng nhập Google / mở trang dự án trên Chrome...")
            elif elapsed % 15 == 0:
                log_msg("ĐANG CHỜ", f"Đang đợi bạn vào giao diện chính của Flow ({elapsed}/{max_wait}s)...")

            time.sleep(poll_step)

        if not input_box:
            log_msg("LỖI", f"Hết thời gian chờ {max_wait}s. Không tìm thấy ô nhập Prompt trên Google Flow!")
            log_msg("HƯỚNG DẪN", "Vui lòng mở Chrome đăng nhập sẵn vào flow.google rồi bấm Chạy lại Bot.")
            sys.exit(1)

        # Chờ người dùng sẵn sàng (không tự động chạy ngay)
        log_msg("CHỜ SẴN SÀNG", "Đã đăng nhập và tìm thấy ô Prompt! Tạm dừng để bạn kiểm tra dự án.")
        log_msg("HƯỚNG DẪN", "👉 Bấm nút '🚀 Sẵn Sàng' trên Tool Studio HOẶC bấm nút xanh trên đỉnh Chrome để bắt đầu chạy prompt.")
        print("STATE:WAITING_READY", flush=True)

        while True:
            if page.is_closed():
                log_msg("LỖI", "Trình duyệt đã bị đóng trước khi bấm Sẵn Sàng!")
                sys.exit(1)

            # 1. Kiểm tra cờ từ App Studio
            if os.path.exists(READY_FLAG_FILE):
                break

            # 2. Kiểm tra click trên trình duyệt
            try:
                inject_ready_button(page)
                clicked = page.evaluate("() => window.__BOT_IS_READY__ === true")
                if clicked:
                    break
            except Exception:
                pass

            time.sleep(0.5)

        # Dọn dẹp nút overlay và cờ
        try:
            page.evaluate("() => { const el = document.getElementById('bot-ready-btn-overlay'); if (el) el.remove(); }")
        except Exception:
            pass
        if os.path.exists(READY_FLAG_FILE):
            try:
                os.remove(READY_FLAG_FILE)
            except Exception:
                pass

        log_msg("BẮT ĐẦU", "Đã nhận lệnh Sẵn Sàng! Đang kết nối lại ô nhập Prompt...")
        input_box = find_flow_input(page)
        if not input_box:
            for _ in range(10):
                time.sleep(1)
                input_box = find_flow_input(page)
                if input_box:
                    break

        if not input_box:
            log_msg("LỖI", "Không tìm thấy ô nhập Prompt sau khi bấm Sẵn Sàng! Vui lòng đảm bảo màn hình đang mở đúng dự án Flow.")
            sys.exit(1)

        # 4. Gửi lần lượt từng prompt
        total = len(prompts)
        log_msg("BƯỚC 4/4", f"Bắt đầu nạp tự động {total} câu prompt vào Flow...")

        for i, prompt in enumerate(prompts, 1):
            # Phát tín hiệu tiến độ để UI bắt và cập nhật Progress Bar
            print(f"PROGRESS:{i}/{total}", flush=True)

            log_msg("THAO TÁC", f"--------------------------------------------------")
            log_msg("THAO TÁC", f"▶ [CÂU {i}/{total}] Đang xử lý câu prompt {i}:")
            snippet = prompt[:80] + "..." if len(prompt) > 80 else prompt
            log_msg("NỘI DUNG", f"\"{snippet}\"")

            try:
                # Re-locate input_box in case DOM refreshed
                input_box = find_flow_input(page)
                if not input_box:
                    time.sleep(2)
                    input_box = find_flow_input(page)

                if not input_box:
                    raise Exception("Mất liên kết với ô nhập Prompt trên màn hình!")

                log_msg("THAO TÁC", "1. Click kích hoạt ô nhập liệu...")
                input_box.click()
                time.sleep(0.3)

                log_msg("THAO TÁC", "2. Điền text an toàn (xóa text cũ + điền prompt mới)...")
                input_box.fill("")
                input_box.fill(prompt)
                time.sleep(0.8)

                log_msg("THAO TÁC", "3. Gửi lệnh tạo ảnh (nhấn nút Send / Enter)...")
                click_send_button(page, input_box)
                log_msg("THÀNH CÔNG", f"Đã gửi thành công prompt [{i}/{total}] lên Google Flow!")

                if i < total:
                    # Chờ sinh ảnh ngẫu nhiên trong khoảng đã chọn
                    wait_time = random.randint(WAIT_MIN, WAIT_MAX)
                    log_msg("CHỜ SINH", f"Đang chờ Flow xử lý ({wait_time}s, cấu hình {WAIT_MIN}-{WAIT_MAX}s) trước khi nạp prompt tiếp theo...")

                    # Countdown in 5s increments for clear visual feedback
                    remaining = wait_time
                    while remaining > 0:
                        step = min(5, remaining)
                        time.sleep(step)
                        remaining -= step
                        if remaining > 0 and (remaining % 10 == 0 or remaining <= 5):
                            log_msg("CHỜ SINH", f"Còn {remaining}s trước khi gửi prompt tiếp theo...")

            except Exception as e:
                log_msg("LỖI", f"Lỗi ở prompt {i}: {e}")
                log_msg("TẠM DỪNG", "Tạm nghỉ 10s trước khi thử câu tiếp theo...")
                time.sleep(10)

        # Hoàn tất
        print(f"PROGRESS:{total}/{total}", flush=True)
        log_msg("HOÀN TẤT", "🎉 ĐÃ GỬI XONG TOÀN BỘ DANH SÁCH PROMPT LÊN GOOGLE FLOW!")
        log_msg("HƯỚNG DẪN", "💡 Vào menu góc trên phải Google Flow chọn 'Download project' để tải toàn bộ ảnh zip về máy.")
        log_msg("HƯỚNG DẪN", "Trình duyệt sẽ giữ mở 60s để bạn tải ảnh hoặc xem kết quả...")
        time.sleep(60)

except Exception as e:
    log_msg("LỖI KHỞI ĐỘNG", f"Lỗi ngoài dự kiến: {e}")
    sys.exit(1)
