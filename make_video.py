import os
import re
import sys
import json
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
from core.tts_cache import read_cached_voice
from core.subtitles import generate_subtitles
from core.renderer import render_project, render_long_thumbnail

def resolve_project_dir(name_or_path):
    if os.path.isabs(name_or_path) and os.path.exists(name_or_path):
        return name_or_path
    proj_in_root = os.path.join(PROJECTS_DIR, name_or_path)
    if os.path.exists(proj_in_root):
        return proj_in_root
    if os.path.exists(name_or_path):
        return os.path.abspath(name_or_path)
    return proj_in_root

def get_script_path(proj_dir):
    """Returns script_vi.txt (fallback: legacy script.txt)."""
    cand = os.path.join(proj_dir, "script_vi.txt")
    if os.path.exists(cand):
        return cand
    legacy = os.path.join(proj_dir, "script.txt")
    if os.path.exists(legacy):
        return legacy
    return cand

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
        valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.mp4', '.mov', '.webm')
        m_dir = os.path.join(p_dir, "video_short_vi")
        if not (os.path.exists(m_dir) and any(f.lower().endswith(valid_exts) for f in os.listdir(m_dir))):
            m_dir = get_media_dir(p_dir)
        img_count = len([f for f in os.listdir(m_dir) if f.lower().endswith(valid_exts)]) if os.path.exists(m_dir) else 0
        
        scripts = []
        if os.path.exists(os.path.join(p_dir, "script_short_vi.txt")):
            scripts.append("SHORT-VI")
        if os.path.exists(os.path.join(p_dir, "script_vi.txt")):
            scripts.append("VI")
        if os.path.exists(os.path.join(p_dir, "script.txt")) and not scripts:
            scripts.append("Mặc định")
        script_info = "/".join(scripts) if scripts else "Chưa có"

        mp4_files = [f for f in os.listdir(p_dir) if f.lower().endswith('.mp4')]
        shorts_dir = os.path.join(p_dir, "shorts_vi")
        shorts_cnt = len([f for f in os.listdir(shorts_dir) if f.lower().endswith('.mp4')]) if os.path.exists(shorts_dir) else 0
        status_parts = []
        if shorts_cnt:
            status_parts.append(f"{shorts_cnt} Shorts")
        if mp4_files:
            status_parts.append(f"{len(mp4_files)} Long")
        mp4_status = f"[OK] ({', '.join(status_parts)})" if status_parts else "[Chua render]"
        
        print(f"{p:<22} | {img_count:<12} | {script_info:<16} | {mp4_status}")
    print("-" * 75)
    print("-> Dựng Short 9:16 : python .agents/skills/shorts-maker/scripts/build_shorts.py <ten_folder>")
    print("-> Dựng Video 16:9 : python make_video.py <ten_folder>\n")

def cmd_new_project(name, short_first=False):
    proj_dir = os.path.join(PROJECTS_DIR, name)
    if os.path.exists(proj_dir):
        print(f"[ERROR] Thu muc du an da ton tai: {proj_dir}")
        return

    if short_first:
        video_short_vi = os.path.join(proj_dir, "video_short_vi")
        video_vi_dir = os.path.join(proj_dir, "video_vi")
        os.makedirs(video_short_vi, exist_ok=True)
        os.makedirs(video_vi_dir, exist_ok=True)

        script_short_vi = os.path.join(proj_dir, "script_short_vi.txt")
        prompts_vid = os.path.join(proj_dir, "prompts_short_vi_video.txt")
        prompts_img = os.path.join(proj_dir, "prompts_short_vi_img.txt")
        shorts_cfg_path = os.path.join(proj_dir, "shorts_config_vi.json")

        with open(script_short_vi, "w", encoding="utf-8") as f:
            f.write(
                "01. Củ sạc 65W giá 150K vẫn báo sạc siêu nhanh — nhưng âm thầm nướng phồng pin mỗi đêm.\n"
                "02. Thủ phạm là con chip điều áp nhiệt PPS bị cắt bỏ trong vỏ nhựa rẻ.\n"
                "03. Sạc GaN thật hạ dòng êm theo nhiệt, còn sạc nhái đẩy pin vọt quá 45°C.\n"
                "04. Vượt mốc 45°C liên tục làm màng hóa học trong pin rách vĩnh viễn.\n"
                "05. Cầm thử trên tay: sạc 65W chuẩn luôn nặng đầm trên 90 gram nhờ tản nhiệt đặc.\n"
                "06. Đăng ký Vắt Chanh để không mất tiền oan — và kiểm tra ngay củ sạc của bạn vì...\n"
            )
        with open(prompts_vid, "w", encoding="utf-8") as f:
            f.write(
                "# BỘ PROMPT [VIDEO] DỌC 9:16 (SHORTS-FIRST, 2-3 CẢNH CHUYỂN ĐỘNG --ar 9:16)\n"
                "# Cảnh 01 [VIDEO]: Hook vật thật / hiện tượng cận cảnh + Mascot Chanh cảnh báo (--ar 9:16)\n"
                "# Cảnh 03 [VIDEO]: Giải phẫu đối lập trực diện cơ chế vật lý (--ar 9:16)\n"
            )
        with open(prompts_img, "w", encoding="utf-8") as f:
            f.write(
                "# BỘ PROMPT [IMG] DỌC 9:16 (SHORTS-FIRST, 3-4 CẢNH MẶT CẮT/BENTO --ar 9:16)\n"
                "# Cảnh 02 [IMG]: Mặt cắt 2D linh kiện bên trong (--ar 9:16)\n"
                "# Cảnh 04 [IMG]: Cận cảnh tác động nhiệt/vật lý (--ar 9:16)\n"
                "# Cảnh 05 [IMG]: Mẹo kiểm tra thực chiến 3 giây (--ar 9:16)\n"
                "# Cảnh 06 [IMG]: Thẻ quy tắc bỏ túi nối vòng lặp (--ar 9:16)\n"
            )
        sample_cfg = [{
            "id": f"short_01_{name}",
            "main_topic": name.replace("_", " ").upper(),
            "badge": "BÓC MẼ PHẦN CỨNG",
            "title_line1": "BẪY SẠC NHANH GIÁ RẺ!",
            "title_line2": "Kiểm Tra Ngay Trước Khi Phồng Pin",
            "accent_color": "#D35400",
            "scenes": [1, 2, 3, 4, 5, 6],
            "thumb_scene": 1,
            "thumb_big_text": "BÁO SẠC SIÊU NHANH\nNHƯNG NƯỚNG PHỒNG PIN?!",
            "thumb_sub_badge": "VẮT CHANH CÔNG NGHỆ",
            "skip_outro": True,
            "has_related_video": False,
            "yt_titles": [
                "Cái bẫy đằng sau củ sạc 65W giá 150K vẫn báo 'Sạc siêu nhanh'! #shorts",
                "Cầm củ sạc lên thấy dấu hiệu này: Rút khỏi ổ điện ngay lập tức! #shorts",
                "Vì sao điện thoại báo Sạc Siêu Nhanh nhưng pin tụt dốc sau 6 tháng? #shorts"
            ],
            "yt_description": (
                "Củ sạc giá rẻ vẫn hiện thông báo Sạc Siêu Nhanh trên màn hình, nhưng bên trong đã cắt bỏ mạch điều áp nhiệt PPS!\n\n"
                "🔔 Đăng ký Vắt Chanh Công Nghệ — Vắt sạch thông số, giữ lại cách dùng!\n\n"
                "#VatChanhCongNghe #SacNhanh #GaN #PinDienThoai #MeoCongNghe #Shorts"
            ),
            "yt_pinned_comment": "Củ sạc bạn đang cắm ở đầu giường là sạc theo máy hay sạc mua ngoài, lúc sạc đầy sờ vào ấm nhẹ hay bỏng tay? 👇",
            "thumb_desc": "Cận cảnh củ sạc rực đỏ nhiệt độ cao bên cạnh mặt cắt pin phồng và linh vật chanh đeo kính cảnh báo (--ar 9:16).",
            "thumb_prompt": "Vertical 9:16 YouTube Shorts thumbnail, bold 2D flat vector editorial tech infographic on a warm cream background (#FAF7F2), clean rounded charcoal line art (#1C1917), glowing red-hot cheap wall charger pumping jagged terracotta orange (#D35400) voltage spikes into a swelling smartphone battery while a cute nerdy lemon mascot wearing round glasses points in alarm, clean space at top for bold text, no text, no watermark --ar 9:16"
        }]
        with open(shorts_cfg_path, "w", encoding="utf-8") as f:
            json.dump(sample_cfg, f, ensure_ascii=False, indent=2)

        print(f"\n[OK] Đã khởi tạo dự án SHORTS-FIRST (9:16 độc lập, 24-34s) tại: {proj_dir}")
        print(f"1. Kịch bản Short (6-7 câu): {script_short_vi}")
        print(f"2. Prompts 9:16            : {prompts_vid} | {prompts_img}")
        print(f"3. Thư mục Media 9:16      : {video_short_vi}")
        print(f"4. Cấu hình Short V3       : {shorts_cfg_path}")
        print(f"5. Dựng ngay 1 lệnh        : python .agents/skills/shorts-maker/scripts/build_shorts.py {name}\n")
        return

    imgs_dir = os.path.join(proj_dir, "imgs")
    imgs_vi_dir = os.path.join(proj_dir, "imgs_vi")
    video_vi_dir = os.path.join(proj_dir, "video_vi")
    script_vi = os.path.join(proj_dir, "script_vi.txt")
    prompts_vi_vid = os.path.join(proj_dir, "prompts_vi_video.txt")
    prompts_vi_img = os.path.join(proj_dir, "prompts_vi_img.txt")
        
    for d in [imgs_dir, imgs_vi_dir, video_vi_dir]:
        os.makedirs(d, exist_ok=True)
    
    with open(script_vi, "w", encoding="utf-8") as f:
        f.write("01. Cau thoai tieng Viet canh mot o day.\n02. Cau thoai tieng Viet canh hai o day.\n")
    with open(prompts_vi_vid, "w", encoding="utf-8") as f:
        f.write("# BỘ PROMPT [VIDEO] KÊNH TIẾNG VIỆT (NỀN VÀNG KEM #FAF7F2) - 6-8 CẢNH HOOK/CLIMAX\n")
    with open(prompts_vi_img, "w", encoding="utf-8") as f:
        f.write("# BỘ PROMPT [IMG] KÊNH TIẾNG VIỆT (NỀN VÀNG KEM #FAF7F2) - 18-20 CẢNH TĨNH\n")
        
    print(f"\n[OK] Da khoi tao du an moi tai: {proj_dir}")
    print(f"1. Kich ban : {script_vi}")
    print(f"2. Prompts  : {prompts_vi_vid} | {prompts_vi_img}")
    print(f"3. Media    : {imgs_vi_dir} hoac {video_vi_dir}")
    print(f"4. Render   : python make_video.py {name}\n")

def get_media_dir(proj_dir, custom_media_dir=None):
    if custom_media_dir and os.path.exists(custom_media_dir):
        return custom_media_dir
    candidates = [
        os.path.join(proj_dir, "video_vi"),
        os.path.join(proj_dir, "imgs_vi-clean"),
        os.path.join(proj_dir, "imgs_vi"),
        os.path.join(proj_dir, "video"),
        os.path.join(proj_dir, "videos"),
        os.path.join(proj_dir, "imgs-clean"),
        os.path.join(proj_dir, "imgs")
    ]
    for c in candidates:
        if os.path.exists(c) and len(os.listdir(c)) > 0:
            return c
    return os.path.join(proj_dir, "imgs")

def _extract_thumb_lines_from_youtube_md(proj_dir, proj_name):
    """Extract 2 short overlay lines from the Thumbnail section of youtube_vi.md, avoiding header slugs/.mp4."""
    yt_md = os.path.join(proj_dir, "youtube_vi.md")
    if os.path.isfile(yt_md):
        with open(yt_md, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        thumb_sec = re.split(r"(?i)##\s*5\.|thiết kế\s+(?:thumbnail|ảnh bìa)", content)[-1]
        candidates = (
            re.findall(r":\s*\*\*([^*]{4,36})\*\*", thumb_sec)
            + re.findall(r":\s*`([^`]{4,36})`", thumb_sec)
        )
        clean_cands = [
            c.strip() for c in candidates
            if not c.lower().endswith(".mp4") and not c.startswith("#") and "_" not in c
        ]
        if len(clean_cands) >= 2:
            return clean_cands[0], clean_cands[1]
    clean_title = proj_name.replace("_", " ").upper()
    return clean_title[:24], "SỰ THẬT BÊN TRONG!"


def build_video_for_project(
    proj_path,
    voice=None,
    force=False,
    media_dir=None,
    motion_25d=False,
    use_intro=False,
    thumb_top=None,
    thumb_bottom=None,
):
    proj_dir = resolve_project_dir(proj_path)
    if not os.path.exists(proj_dir):
        print(f"[ERROR] Khong tim thay thu muc du an: {proj_dir}")
        print("Goi y: Dung 'python make_video.py --list' de xem danh sach.")
        sys.exit(1)
        
    proj_name = os.path.basename(os.path.normpath(proj_dir))
    media_dir = get_media_dir(proj_dir, custom_media_dir=media_dir)
    script_path = get_script_path(proj_dir)

    audio_dir = os.path.join(proj_dir, "audio_vi")

    # Default voice: the one already cached for this project, else the channel default
    if voice is None:
        voice = read_cached_voice(audio_dir) or DEFAULT_VOICE
    srt_path = os.path.join(proj_dir, "subtitles_vi.srt")
    output_mp4 = os.path.join(proj_dir, f"{proj_name}_vi.mp4")
    
    print(f"\n========================================================")
    print(f"BAT DAU PIPELINE DUNG VIDEO: {proj_name}")
    print(f"Thu muc: {proj_dir}")
    print(f"Nguon media: {os.path.basename(media_dir)}")
    print(f"File thoai: {os.path.basename(script_path)}")
    print(f"Giong doc: {voice} | Intro 00:00: {'BAT' if use_intro else 'TAT (Chuan Retention)'}")
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
    print(f"\n[Buoc 3/4] Dong bo thoi luong & sinh file phu de SRT...")
    enriched_items = generate_subtitles(audio_items, srt_path)
    
    # 4. Render Video (default use_intro=False so Hook hits at 00:00)
    print(f"\n[Buoc 4/4] Dung video Full HD...")
    final_video = render_project(
        media_paths,
        enriched_items,
        srt_path,
        output_mp4,
        use_intro=use_intro,
        motion_25d=motion_25d,
    )

    # Auto-generate high-contrast 16:9 thumbnail so long-form never uploads without a custom cover
    thumb_out = os.path.join(proj_dir, "thumbnail_vi.jpg")
    if force or thumb_top or not os.path.exists(thumb_out):
        auto_top, auto_bot = _extract_thumb_lines_from_youtube_md(proj_dir, proj_name)
        render_long_thumbnail(
            media_paths[0],
            thumb_out,
            headline_top=thumb_top or auto_top,
            headline_bottom=thumb_bottom or auto_bot,
        )
        print(f"[THUMBNAIL 16:9 OK] {thumb_out}")
    
    print(f"\n========================================================")
    print(f"HOAN THANH VIDEO: {os.path.basename(final_video)}")
    print(f"Duong dan file: {final_video}")
    print(f"========================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Multi-Video Generator Engine (V3 Retention-First)")
    parser.add_argument("project", nargs="?", help="Ten folder du an trong projects/ hoac duong dan thu muc")
    parser.add_argument("--lang", choices=["vi"], default="vi", help="Chi con kenh tieng Viet (giu de tuong thich lenh cu)")
    parser.add_argument("--new", metavar="NAME", help="Tao nhanh 1 folder du an moi")
    parser.add_argument("--new-short", metavar="NAME", help="Tao nhanh du an SHORTS-FIRST 9:16 doc lap (6-7 cau, 24-34s)")
    parser.add_argument("--short-first", action="store_true", help="Ket hop voi --new de tao du an SHORTS-FIRST 9:16")
    parser.add_argument("--list", action="store_true", help="Liet ke toan bo cac du an video hien co")
    parser.add_argument("--voice", default=None, help="Giong doc TTS (mac dinh: gemini:voice_5mxlq1k9luls)")
    parser.add_argument("--media-dir", default=None, help="Duong dan thu muc media tuy chon")
    parser.add_argument("--force", action="store_true", help="Ep tao lai audio va thumbnail ngay ca khi da cache")
    parser.add_argument("--with-intro", action="store_true", help="Ghep intro 3s vao dau video (mac dinh TAT de giu Retention 00:00)")
    parser.add_argument("--thumb-top", default=None, help="Dong chu lon thu 1 tren Thumbnail 16:9")
    parser.add_argument("--thumb-bottom", default=None, help="Dong chu nhan thu 2 tren Thumbnail 16:9")
    parser.add_argument("--25d", dest="use_25d", action="store_true", help="Bat hieu ung tach lop 2.5D")
    parser.add_argument("--no-25d", action="store_true", help="Tat hieu ung tach lop Motion 2.5D cho anh tinh (mac dinh)")
    
    args = parser.parse_args()
    
    if args.list:
        cmd_list_projects()
        return
        
    if args.new_short:
        cmd_new_project(args.new_short, short_first=True)
        return

    if args.new:
        cmd_new_project(args.new, short_first=args.short_first)
        return
        
    if args.project:
        build_video_for_project(
            proj_path=args.project,
            voice=args.voice,
            force=args.force,
            media_dir=args.media_dir,
            motion_25d=bool(args.use_25d and not args.no_25d),
            use_intro=args.with_intro,
            thumb_top=args.thumb_top,
            thumb_bottom=args.thumb_bottom,
        )
        return
        
    cmd_list_projects()
    print("Cach dung (Flow V3 Shorts-First):")
    print("  python make_video.py --new-short <ten_moi>     # Buoc 1: Tao du an Short 9:16 do duong (24-34s)")
    print("  python make_video.py <ten_folder>              # Buoc 2: Render Video dai 16:9 (khi Short no view)\n")

if __name__ == "__main__":
    main()
