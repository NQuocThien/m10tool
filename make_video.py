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
    """Resolves project directory from name or relative/absolute path."""
    if os.path.isabs(name_or_path) and os.path.exists(name_or_path):
        return name_or_path
    
    # Check in projects/ directory
    proj_in_root = os.path.join(PROJECTS_DIR, name_or_path)
    if os.path.exists(proj_in_root):
        return proj_in_root
        
    # Check if direct relative path
    if os.path.exists(name_or_path):
        return os.path.abspath(name_or_path)
        
    return proj_in_root

def cmd_list_projects():
    """Lists all video projects in projects/ and their readiness."""
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    items = sorted(os.listdir(PROJECTS_DIR))
    projects = [d for d in items if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
    
    print("\n[DANH SACH CAC DU AN VIDEO]")
    print("-" * 70)
    print(f"{'Ten Folder':<25} | {'Anh (imgs/)':<12} | {'Thoai (script)':<14} | {'Video MP4'}")
    print("-" * 70)
    
    if not projects:
        print("  (Chua co du an nao. Dung 'python make_video.py --new <ten_video>' de tao)")
        return

    for p in projects:
        p_dir = os.path.join(PROJECTS_DIR, p)
        imgs_dir = os.path.join(p_dir, "imgs")
        img_count = len([f for f in os.listdir(imgs_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]) if os.path.exists(imgs_dir) else 0
        
        script_file = os.path.join(p_dir, "script.txt")
        line_count = 0
        if os.path.exists(script_file):
            with open(script_file, "r", encoding="utf-8", errors="ignore") as f:
                line_count = len([line.strip() for line in f if line.strip()])
                
        mp4_files = [f for f in os.listdir(p_dir) if f.lower().endswith('.mp4')]
        mp4_status = "[OK] " + mp4_files[0] if mp4_files else "[Chua render]"
        
        print(f"{p:<25} | {img_count:<12} | {line_count:<14} | {mp4_status}")
    print("-" * 70)
    print("-> Chay video: python make_video.py <ten_folder>\n")

def cmd_new_project(name):
    """Scaffolds a new project folder with imgs/ and sample script.txt."""
    proj_dir = os.path.join(PROJECTS_DIR, name)
    imgs_dir = os.path.join(proj_dir, "imgs")
    script_file = os.path.join(proj_dir, "script.txt")
    
    if os.path.exists(proj_dir):
        print(f"[ERROR] Thu muc du an da ton tai: {proj_dir}")
        return
        
    os.makedirs(imgs_dir, exist_ok=True)
    
    template_script = (
        "01. When choosing an electric two-wheeler, the biggest decision starts inside the battery pack.\n"
        "02. In this showdown, it comes down to a classic trade-off: rugged durability against energy density.\n"
        "03. Both chemistries power modern mobility, but create two entirely different riding experiences.\n"
    )
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(template_script)
        
    print(f"\n[OK] Da khoi tao du an moi tai: {proj_dir}")
    print(f"1. Bo cac file anh vao: {imgs_dir}")
    print(f"2. Chinh sua cau thoai trong: {script_file}")
    print(f"3. Render video bang lenh: python make_video.py {name}\n")

def build_video_for_project(proj_path, voice=DEFAULT_VOICE, force=False):
    """Executes the complete pipeline for a specific project folder."""
    proj_dir = resolve_project_dir(proj_path)
    if not os.path.exists(proj_dir):
        print(f"[ERROR] Khong tim thay thu muc du an: {proj_dir}")
        print("Goi y: Dung 'python make_video.py --list' de xem danh sach.")
        sys.exit(1)
        
    proj_name = os.path.basename(os.path.normpath(proj_dir))
    imgs_dir = os.path.join(proj_dir, "imgs")
    script_path = os.path.join(proj_dir, "script.txt")
    audio_dir = os.path.join(proj_dir, "audio")
    srt_path = os.path.join(proj_dir, "subtitles.srt")
    output_mp4 = os.path.join(proj_dir, f"{proj_name}.mp4")
    
    print(f"\n========================================================")
    print(f"BAT DAU PIPELINE TU DONG DUNG VIDEO: [{proj_name}]")
    print(f"Thu muc: {proj_dir}")
    print(f"========================================================")
    
    # 1. Sort & get images
    print("\n[Buoc 1/4] Quet va chuan hoa thu tu anh...")
    image_paths = get_sorted_images(imgs_dir)
    print(f"  -> Tim thay {len(image_paths)} anh hop le.")
    
    # 2. TTS Generation
    print("\n[Buoc 2/4] Tao giong doc AI (Azure Neural TTS)...")
    audio_items = generate_audio(script_path, audio_dir, voice=voice, force=force)
    
    if len(image_paths) != len(audio_items):
        print(f"\n[ERROR] LOI KHONG KHOP SO LUONG:")
        print(f"  - So anh tim thay: {len(image_paths)}")
        print(f"  - So cau thoai trong script: {len(audio_items)}")
        print("  -> Vui long dam bao 1 anh tuong ung chinh xac 1 cau thoai.")
        sys.exit(1)
        
    # 3. Subtitles sync
    print("\n[Buoc 3/4] Dong bo thoi luong & sinh file phu de SRT...")
    enriched_items = generate_subtitles(audio_items, srt_path)
    
    # 4. Render Video
    print("\n[Buoc 4/4] Dung video Full HD (Ken Burns 3% + Hardsub)...")
    final_video = render_project(image_paths, enriched_items, srt_path, output_mp4)
    
    print(f"\n========================================================")
    print(f"HOAN THANH VIDEO: {os.path.basename(final_video)}")
    print(f"Duong dan file: {final_video}")
    print(f"========================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Multi-Video Generator Engine")
    parser.add_argument("project", nargs="?", help="Ten folder du an trong projects/ hoac duong dan thu muc")
    parser.add_argument("--new", metavar="NAME", help="Tao nhanh 1 folder du an moi voi cau truc mau")
    parser.add_argument("--list", action="store_true", help="Liet ke toan bo cac du an video hien co")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Giong doc Azure Neural TTS (mac dinh: en-US-ChristopherNeural)")
    parser.add_argument("--force", action="store_true", help="Ep tao lai audio ngay ca khi da cache")
    
    args = parser.parse_args()
    
    if args.list:
        cmd_list_projects()
        return
        
    if args.new:
        cmd_new_project(args.new)
        return
        
    if args.project:
        build_video_for_project(args.project, voice=args.voice, force=args.force)
        return
        
    cmd_list_projects()
    print("Cach dung:")
    print("  python make_video.py <ten_folder>     # Render video cho folder do")
    print("  python make_video.py --new <ten_moi>  # Tao folder du an video moi")
    print("  python make_video.py --list           # Xem lai danh sach du an\n")

if __name__ == "__main__":
    main()
