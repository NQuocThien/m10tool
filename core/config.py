import os
import imageio_ffmpeg

# Project Information
CHANNEL_NAME_EN = "Squeezing Tech"
CHANNEL_NAME_VI = "Vắt Chanh Công Nghệ"
SLOGAN_EN = "Extracting Value from Everyday Tech"
SLOGAN_VI = "Vắt sạch thông số, giữ lại cách dùng."

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

# Intro paths
INTRO_EN_PATH = os.path.join(RESOURCES_DIR, "intro_en.mp4")
INTRO_VI_PATH = os.path.join(RESOURCES_DIR, "intro_vi.mp4")
GLOBAL_INTRO_PATH = os.path.join(BASE_DIR, "intro.mp4")

# Video Settings
DEFAULT_FPS = 25
DEFAULT_RESOLUTION = (1920, 1080)
DEFAULT_MAX_ZOOM = 1.03  # Subtle 3% Ken Burns zoom

# Audio / TTS Settings
DEFAULT_VOICE = "en-US-ChristopherNeural"  # Professional tech narrator

VOICES_VI = [
    ("Tiếng Việt - Nam Minh (Trầm ấm, thời sự)", "vi-VN-NamMinhNeural"),
    ("Tiếng Việt - Hoài My (Truyền cảm, rõ ràng)", "vi-VN-HoaiMyNeural"),
]

VOICES_EN = [
    ("English (US) - Christopher (Tech Documentary)", "en-US-ChristopherNeural"),
    ("English (US) - Jenny (Natural & Engaging)", "en-US-JennyNeural"),
    ("English (US) - Guy (Casual Conversational)", "en-US-GuyNeural"),
    ("English (UK) - Ryan (British Accent)", "en-GB-RyanNeural"),
]

# Subtitle Styling (Compact, modern, bottom-aligned)
DEFAULT_SUB_STYLE = (
    "FontName=Arial,FontSize=15,"
    "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
    "BorderStyle=1,Outline=1.2,Shadow=0.5,"
    "MarginV=24,Bold=0,Alignment=2"
)

# Outro templates
OUTRO_SCRIPT_VI = "Vắt sạch thông số, giữ lại cách dùng. Đăng ký kênh để không bỏ lỡ video tiếp theo!"
OUTRO_SCRIPT_EN = "Extracting value from everyday tech. Subscribe for the next deep dive!"
