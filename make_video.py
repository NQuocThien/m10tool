import os
import sys
import argparse

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from core.config import PROJECTS_DIR, DEFAULT_VOICE
from core.sorter import get_sorted_images
from core.tts import generate_audio
from core.subtitles import generate_subtitles
from core.renderer import render_project

def resolve_project_dir(name_or_path):
    if os.path.isabs(name_or_path) and os.path.exists(name_or_path):
        return name_or_path
    proj_in_root = os.path.join(PROJECTS_DIR, name_or_path)
    if os.path.exists(proj_in_root):
        return proj_in_root
    if os.path.exists(name_or_path):
        return os.path.abspath(name_or_path)
    return proj_in_root

def get_script_path(proj_dir, lang="vi"):
    """
    Returns path to script file based on language:
    lang='vi' -> script_vi.txt (fallback script.txt)
    lang='en' -> script_en.txt (fallback script.txt)
    """
    if lang == "vi":
        cand = os.path.join(proj_dir, "script_vi.txt")
        if os.path.exists(cand):
            return cand
    elif lang == "en":
        cand = os.path.join(proj_dir, "script_en.txt")
        if os.path.exists(cand):
            return cand

    default_cand = os.path.join(proj_dir, "script.txt")
    if os.path.exists(default_cand):
        return default_cand
    return os.path.join(proj_dir, f"script_{lang}.txt")

def cmd_list_projects():
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    items = sorted(os.listdir(PROJECTS_DIR))
    projects = [d for d in items if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
    
    print("\n[DANH SACH CAC DU AN VIDEO]")
    print("-" * 75)
    print(f"{'Ten Folder':<22} | {'Anh (imgs/)':<12} | {'Kich Ban Sanch':<16} | {'Video MP4'}")
    print("-" * 75)
    
    if not projects:
        print("  (Chua co du an nao. Dung 'python make_video.py --new <ten_video>' de tao)")
        return

    for p in projects:
        p_dir = os.path.join(PROJECTS_DIR, p)
        imgs_dir = os.path.join(p_dir, "imgs")
        img_count = len([f for f in os.listdir(imgs_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]) if os.path.exists(imgs_dir) else 0
        
        scripts = []
        if os.path.exists(os.path.join(p_dir, "script_vi.txt")):
            scripts.append("VI")
        if os.path.exists(os.path.join(p_dir, "script_en.txt")):
            scripts.append("EN")
        if os.path.exists(os.path.join(p_dir, "script.txt")) and not scripts:
            scripts.append("Mặc định")
        script_info = "/".join(scripts) if scripts else "Chưa có"

        mp4_files = [f for f in os.listdir(p_dir) if f.lower().endswith('.mp4')]
        mp4_status = f"[OK] ({len(mp4_files)} video)" if mp4_files else "[Chua render]"
        
        print(f"{p:<22} | {img_count:<12} | {script_info:<16} | {mp4_status}")
    print("-" * 75)
    print("-> Chay video: python make_video.py <ten_folder> [--lang vi|en]\n")

def cmd_new_project(name):
    proj_dir = os.path.join(PROJECTS_DIR, name)
    imgs_dir = os.path.join(proj_dir, "imgs")
    imgs_vi_dir = os.path.join(proj_dir, "imgs_vi")
    imgs_en_dir = os.path.join(proj_dir, "imgs_en")
    video_vi_dir = os.path.join(proj_dir, "video_vi")
    video_en_dir = os.path.join(proj_dir, "video_en")
    script_vi = os.path.join(proj_dir, "script_vi.txt")
    script_en = os.path.join(proj_dir, "script_en.txt")
    prompts_vi_vid = os.path.join(proj_dir, "prompts_vi_video.txt")
    prompts_vi_img = os.path.join(proj_dir, "prompts_vi_img.txt")
    prompts_en_vid = os.path.join(proj_dir, "prompts_en_video.txt")
    prompts_en_img = os.path.join(proj_dir, "prompts_en_img.txt")
    
    if os.path.exists(proj_dir):
        print(f"[ERROR] Thu muc du an da ton tai: {proj_dir}")
        return
        
    for d in [imgs_dir, imgs_vi_dir, imgs_en_dir, video_vi_dir, video_en_dir]:
        os.makedirs(d, exist_ok=True)
    
    with open(script_vi, "w", encoding="utf-8") as f:
        f.write("01. Cau thoai tieng Viet canh mot o day.\n02. Cau thoai tieng Viet canh hai o day.\n")
    with open(script_en, "w", encoding="utf-8") as f:
        f.write("01. English narration for scene one.\n02. English narration for scene two.\n")
    with open(prompts_vi_vid, "w", encoding="utf-8") as f:
        f.write("# BỘ PROMPT [VIDEO] KÊNH TIẾNG VIỆT (NỀN VÀNG KEM #FAF7F2) - 4-6 CẢNH HOOK/CLIMAX\n")
    with open(prompts_vi_img, "w", encoding="utf-8") as f:
        f.write("# BỘ PROMPT [IMG] KÊNH TIẾNG VIỆT (NỀN VÀNG KEM #FAF7F2) - 20-24 CẢNH TĨNH\n")
    with open(prompts_en_vid, "w", encoding="utf-8") as f:
        f.write("# BỘ PROMPT [VIDEO] KÊNH TIẾNG ANH (NỀN XANH ĐEN #0B132B) - 4-6 CẢNH HOOK/CLIMAX\n")
    with open(prompts_en_img, "w", encoding="utf-8") as f:
        f.write("# BỘ PROMPT [IMG] KÊNH TIẾNG ANH (NỀN XANH ĐEN #0B132B) - 20-24 CẢNH TĨNH\n")
        
    print(f"\n[OK] Da khoi tao du an moi tai: {proj_dir}")
    print(f"1. Kich ban   : {script_vi} (VI) | {script_en} (EN)")
    print(f"2. Prompts VI : {prompts_vi_vid} | {prompts_vi_img}")
    print(f"3. Prompts EN : {prompts_en_vid} | {prompts_en_img}")
    print(f"4. Media VI   : {imgs_vi_dir} hoac {video_vi_dir}")
    print(f"5. Media EN   : {imgs_en_dir} hoac {video_en_dir}")
    print(f"6. Render     : python make_video.py {name} --lang vi (hoac --lang en)\n")

def get_media_dir(proj_dir, lang="vi", custom_media_dir=None):
    if custom_media_dir and os.path.exists(custom_media_dir):
        return custom_media_dir
    candidates = [
        os.path.join(proj_dir, f"video_{lang}"),
        os.path.join(proj_dir, f"imgs_{lang}-clean"),
        os.path.join(proj_dir, f"imgs_{lang}"),
        os.path.join(proj_dir, "video"),
        os.path.join(proj_dir, "videos"),
        os.path.join(proj_dir, "imgs-clean"),
        os.path.join(proj_dir, "imgs")
    ]
    for c in candidates:
        if os.path.exists(c) and len(os.listdir(c)) > 0:
            return c
    return os.path.join(proj_dir, "imgs")

def build_video_for_project(proj_path, lang="vi", voice=None, force=False, media_dir=None, motion_25d=False):
    proj_dir = resolve_project_dir(proj_path)
    if not os.path.exists(proj_dir):
        print(f"[ERROR] Khong tim thay thu muc du an: {proj_dir}")
        print("Goi y: Dung 'python make_video.py --list' de xem danh sach.")
        sys.exit(1)
        
    proj_name = os.path.basename(os.path.normpath(proj_dir))
    media_dir = get_media_dir(proj_dir, lang=lang, custom_media_dir=media_dir)
    script_path = get_script_path(proj_dir, lang=lang)

    # Determine default voice based on language
    if voice is None:
        if lang == "vi":
            voice = "gemini:voice_5mxlq1k9luls"
        else:
            voice = "gemini:Charon"

    # Distinguish audio, sub, and video outputs per language
    audio_dir = os.path.join(proj_dir, f"audio_{lang}")
    srt_path = os.path.join(proj_dir, f"subtitles_{lang}.srt")
    output_mp4 = os.path.join(proj_dir, f"{proj_name}_{lang}.mp4")
    
    print(f"\n========================================================")
    print(f"BAT DAU PIPELINE DUNG VIDEO [{lang.upper()}]: {proj_name}")
    print(f"Thu muc: {proj_dir}")
    print(f"Nguon media: {os.path.basename(media_dir)}")
    print(f"File thoai: {os.path.basename(script_path)}")
    print(f"Giong doc: {voice}")
    print(f"========================================================")
    
    # 1. Sort & get media files
    print("\n[Buoc 1/4] Quet va chuan hoa thu tu media...")
    media_paths = get_sorted_images(media_dir)
    print(f"  -> Tim thay {len(media_paths)} file media hop le trong '{os.path.basename(media_dir)}'.")
    
    # 2. TTS Generation
    print(f"\n[Buoc 2/4] Tao giong doc AI ({voice})...")
    audio_items = generate_audio(script_path, audio_dir, voice=voice, force=force)
    
    if len(media_paths) != len(audio_items):
        print(f"\n[ERROR] LOI KHONG KHOP SO LUONG:")
        print(f"  - So media tim thay: {len(media_paths)}")
        print(f"  - So cau thoai trong {os.path.basename(script_path)}: {len(audio_items)}")
        print("  -> Vui long dam bao 1 media tuong ung chinh xac 1 cau thoai.")
        sys.exit(1)
        
    # 3. Subtitles sync
    print(f"\n[Buoc 3/4] Dong bo thoi luong & sinh file phu de SRT ({lang.upper()})...")
    enriched_items = generate_subtitles(audio_items, srt_path)
    
    # 4. Render Video
    print(f"\n[Buoc 4/4] Dung video Full HD ({lang.upper()})...")
    final_video = render_project(media_paths, enriched_items, srt_path, output_mp4, lang=lang, motion_25d=motion_25d)
    
    print(f"\n========================================================")
    print(f"HOAN THANH VIDEO: {os.path.basename(final_video)}")
    print(f"Duong dan file: {final_video}")
    print(f"========================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Multi-Video Generator Engine")
    parser.add_argument("project", nargs="?", help="Ten folder du an trong projects/ hoac duong dan thu muc")
    parser.add_argument("--lang", choices=["vi", "en"], default="vi", help="Ngon ngu video: 'vi' (Tieng Viet) hoac 'en' (Tieng Anh)")
    parser.add_argument("--new", metavar="NAME", help="Tao nhanh 1 folder du an moi voi cau truc mau")
    parser.add_argument("--list", action="store_true", help="Liet ke toan bo cac du an video hien co")
    parser.add_argument("--voice", default=None, help="Giong doc TTS (mac dinh: gemini:Charon; hoac edge-tts vi-VN-NamMinhNeural)")
    parser.add_argument("--media-dir", default=None, help="Duong dan thu muc media tuy chon (mac dinh tu nhan video_vi hoac imgs)")
    parser.add_argument("--force", action="store_true", help="Ep tao lai audio ngay ca khi da cache")
    parser.add_argument("--25d", dest="use_25d", action="store_true", help="Bat hieu ung tach lop 2.5D (chi dung cho anh chup chan dung/vat the don)")
    parser.add_argument("--no-25d", action="store_true", help="Tat hieu ung tach lop Motion 2.5D cho anh tinh (mac dinh)")
    
    args = parser.parse_args()
    
    if args.list:
        cmd_list_projects()
        return
        
    if args.new:
        cmd_new_project(args.new)
        return
        
    if args.project:
        build_video_for_project(proj_path=args.project, lang=args.lang, voice=args.voice, force=args.force, media_dir=args.media_dir, motion_25d=bool(args.use_25d and not args.no_25d))
        return
        
    cmd_list_projects()
    print("Cach dung:")
    print("  python make_video.py <ten_folder> --lang vi    # Render ban Tieng Viet")
    print("  python make_video.py <ten_folder> --lang en    # Render ban Tieng Anh")
    print("  python make_video.py --new <ten_moi>           # Tao folder du an video moi")
    print("  python make_video.py --list                    # Xem lai danh sach du an\n")

if __name__ == "__main__":
    main()
