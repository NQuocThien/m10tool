import os
import imageio_ffmpeg

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

# Video Settings
DEFAULT_FPS = 25
DEFAULT_RESOLUTION = (1920, 1080)
DEFAULT_MAX_ZOOM = 1.03  # Subtle 3% Ken Burns zoom

# Audio / TTS Settings
DEFAULT_VOICE = "en-US-ChristopherNeural"  # Professional tech narrator
# Alternative popular voices:
# "en-US-JennyNeural" (US Female)
# "en-US-GuyNeural" (US Casual Male)
# "vi-VN-HoaiMyNeural" (VN Female)
# "vi-VN-NamMinhNeural" (VN Male)

# Subtitle Styling (Compact, sleek, placed at bottom without blocking content)
DEFAULT_SUB_STYLE = (
    "FontName=Arial,FontSize=15,"
    "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
    "BorderStyle=1,Outline=1.2,Shadow=0.5,"
    "MarginV=24,Bold=0,Alignment=2"
)
