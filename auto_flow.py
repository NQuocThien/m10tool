import time
import os
import sys
import random
from playwright.sync_api import sync_playwright

# 1. Cấu hình
DEFAULT_PROMPT_FILE = "prompts_battery_infographic.txt"
if len(sys.argv) > 1:
    PROMPT_FILE = sys.argv[1]
else:
    # Look for prompts.txt in current directory or sample
    if os.path.exists("prompts.txt"):
        PROMPT_FILE = "prompts.txt"
    elif os.path.exists(DEFAULT_PROMPT_FILE):
        PROMPT_FILE = DEFAULT_PROMPT_FILE
    else:
        PROMPT_FILE = "prompts.txt"

GOOGLE_FLOW_URL = "https://flow.google/"

WAIT_MIN = 25
WAIT_MAX = 40

# 2. Đọc file prompt
if not os.path.exists(PROMPT_FILE):
    print(f"❌ Lỗi: Không tìm thấy file prompt '{PROMPT_FILE}'!")
    print("Cách dùng: python auto_flow.py <duong_dan_file_prompt>")
    sys.exit(1)

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    prompts = [line.strip() for line in f if line.strip()]

print(f"📄 Đã nạp {len(prompts)} prompt từ '{PROMPT_FILE}'.")


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
        loc = page.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            return loc

    try:
        active = page.evaluate("() => document.activeElement && document.activeElement.tagName !== 'BODY'")
        if active:
            return page.locator("*:focus")
    except Exception:
        pass

    raise Exception("Không tìm thấy ô nhập 'What do you want to create?' trên màn hình Google Flow!")


def click_send_button(page, input_box):
    """
    Nhấn nút mũi tên gửi (hoặc phím Enter) trên thanh công cụ tạo của Flow
    """
    try:
        input_box.press("Enter")
        time.sleep(0.5)
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
                break
        except Exception:
            pass


# 3. Khởi chạy Playwright
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir="./user_data",
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

    print(f"🌐 Đang mở Google Flow: {GOOGLE_FLOW_URL}...")
    page.goto(GOOGLE_FLOW_URL, timeout=60000)

    print("⏳ Chờ trang Flow tải hoàn tất...")
    time.sleep(5)

    input_box = None
    try:
        input_box = find_flow_input(page)
        print("✅ Đã kết nối với ô nhập Prompt.")
    except Exception as e:
        print(f"⚠️ {e}")
        print("👉 Vui lòng đăng nhập hoặc mở dự án Flow trên cửa sổ Chrome vừa hiện lên.")
        input("Nhấn Enter tại terminal này sau khi đã vào được màn hình chính của Flow để tiếp tục: ")
        input_box = find_flow_input(page)

    # 4. Gửi lần lượt từng prompt
    for i, prompt in enumerate(prompts, 1):
        print(f"\n==========================================")
        print(f"🚀 [{i}/{len(prompts)}] Đang gửi prompt:")
        print(f"\"{prompt[:80]}...\"")

        try:
            input_box = find_flow_input(page)
            input_box.click()
            time.sleep(0.5)

            # Điền text an toàn
            input_box.fill("")
            input_box.fill(prompt)
            time.sleep(1)

            # Gửi
            click_send_button(page, input_box)
            print("✅ Đã nhấn tạo!")

            # Nghỉ chờ Flow sinh ảnh
            wait_time = random.randint(WAIT_MIN, WAIT_MAX)
            print(f"⏱️ Chờ {wait_time}s trước prompt tiếp theo...")
            time.sleep(wait_time)

        except Exception as e:
            print(f"❌ Lỗi khi gửi prompt {i}: {e}")
            print("Tạm dừng 10s rồi thử lại...")
            time.sleep(10)

    print("\n🎉 ĐÃ GỬI XONG TẤT CẢ PROMPT!")
    print("💡 Hãy vào menu góc phải trên Flow chọn 'Download project' để tải toàn bộ ảnh dạng zip.")
    input("Nhấn Enter để đóng trình duyệt...")
    context.close()
