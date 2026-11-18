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

# Intro & BGM paths
INTRO_EN_PATH = os.path.join(RESOURCES_DIR, "intro_en.mp4")
INTRO_VI_PATH = os.path.join(RESOURCES_DIR, "intro_vi.mp4")
GLOBAL_INTRO_PATH = os.path.join(BASE_DIR, "intro.mp4")
BGM_VI_PATH = os.path.join(RESOURCES_DIR, "bgm_vi.mp3")
BGM_EN_PATH = os.path.join(RESOURCES_DIR, "bgm_en.mp3")
GLOBAL_BGM_PATH = os.path.join(RESOURCES_DIR, "bgm.mp3")
DEFAULT_BGM_VOLUME = 0.08
SCENE_TAIL_PAD_SEC = 0.18

# Video Settings
DEFAULT_FPS = 25
DEFAULT_RESOLUTION = (1920, 1080)
DEFAULT_MAX_ZOOM = 1.03  # Subtle 3% Ken Burns zoom

# Audio / TTS Settings
GEMINI_TTS_MODEL = "gemini-3.8-flash-tts"
GEMINI_TTS_FALLBACK_MODELS = [
    "gemini-3.8-flash-tts",
    "gemini-3.8-flash-lite-tts",
    "gemini-3.1-flash-tts-preview",
    "gemini-2.5-flash-preview-tts",
    "gemini-2.5-pro-preview-tts",
]
GEMINI_STYLE_VI = (
    "Authoritative, crisp Northern Vietnamese male tech documentary narrator. "
    "Rich medium-low voice, deliberate punchy emphasis on key words, studio mic presence."
)
GEMINI_STYLE_EN = (
    "Speak like an engaging, authoritative tech documentary narrator. "
    "Crisp articulation, natural conversational rhythm, warm and confident."
)

DEFAULT_VOICE = "gemini:voice_5mxlq1k9luls"

VOICES_VI = [
    ("Gemini 3.8 - Tech Baritone (Chuẩn Vắt Chanh Công Nghệ)", "gemini:voice_5mxlq1k9luls"),
    ("Gemini 3.8 - Tech Fast (Trẻ trung, dứt khoát)", "gemini:voice_g38ftts_3c699d99b1a345a4a2db994baed44e86"),
    ("Gemini 3.8 - Training 6 (Bản địa VI, nhanh rõ)", "gemini:vi-vn-training-6"),
    ("Gemini 3.8 - Advisor 2 (Bản địa VI, podcast)", "gemini:vi-vn-advisor-2"),
    ("Gemini 3.8 - Charon (Nam, thông tin, rõ ràng)", "gemini:Charon"),
    ("Gemini 3.8 - Sulafat (Nữ, ấm áp, tự nhiên)", "gemini:Sulafat"),
    ("Edge TTS - Nam Minh (Cũ)", "vi-VN-NamMinhNeural"),
    ("Edge TTS - Hoài My (Cũ)", "vi-VN-HoaiMyNeural"),
]

VOICES_EN = [
    ("Gemini 3.8 - Charon (Informative, Tech Narrator)", "gemini:Charon"),
    ("Gemini 3.8 - Orus (Firm, Authoritative)", "gemini:Orus"),
    ("Gemini 3.8 - Puck (Upbeat, Engaging)", "gemini:Puck"),
    ("Gemini 3.8 - Sadaltager (Knowledgeable)", "gemini:Sadaltager"),
    ("Gemini 3.8 - Kore (Firm, Clear)", "gemini:Kore"),
    ("Gemini 3.8 - Aoede (Breezy, Natural)", "gemini:Aoede"),
    ("Edge TTS - Christopher (Old)", "en-US-ChristopherNeural"),
    ("Edge TTS - Jenny (Old)", "en-US-JennyNeural"),
]

# Subtitle Styling (Compact, bold, high-contrast bottom-aligned)
DEFAULT_SUB_STYLE = (
    "FontName=Segoe UI,FontSize=16,"
    "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
    "BorderStyle=1,Outline=1.6,Shadow=0.8,"
    "MarginV=28,Bold=1,Alignment=2"
)

# Outro templates
OUTRO_SCRIPT_VI = "Vắt sạch thông số, giữ lại cách dùng. Đăng ký kênh để không bỏ lỡ video tiếp theo!"
OUTRO_SCRIPT_EN = "Extracting value from everyday tech. Subscribe for the next deep dive!"
