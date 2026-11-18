import os
import re
import sys
import json
import shutil
import hashlib
import winsound
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageOps

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from core.config import BASE_DIR, PROJECTS_DIR, RESOURCES_DIR, FFMPEG_PATH, DEFAULT_BGM_VOLUME, VOICES_VI, VOICES_EN
from core.sorter import sort_media_by_prompts
from core.renderer import get_bgm_path
from core.tts import load_script, synthesize_preview
from make_video import get_media_dir, get_script_path

SETTINGS_FILE = os.path.join(BASE_DIR, "app_settings.json")

def load_settings():
    default_settings = {
        "last_project": "",
        "last_lang": "vi",
        "last_voice_vi_idx": 0,
        "last_voice_en_idx": 0,
        "watermark_mode": "batch",
        "watermark_in_path": "",
        "watermark_in_dir": "",
        "watermark_out_dir": os.path.join(os.path.expanduser("~"), "Downloads"),
        "watermark_naming_mode": "keep",
        "last_prompt_file": ""
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_settings.update(data)
        except Exception:
            pass
    return default_settings

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def remove_gemini_star_from_image(img):
    img = img.convert("RGB")
    w, h = img.size
    star_x1, star_x2 = int(w * 0.88), int(w * 0.96)
    star_y1, star_y2 = int(h * 0.78), int(h * 0.94)

    # Fast symmetrical mirroring with Pillow crop & paste
    clean_x1 = w - star_x2
    clean_x2 = w - star_x1
    clean_box = (max(0, clean_x1), max(0, star_y1), min(w, clean_x2), min(h, star_y2))
    
    clean_patch = img.crop(clean_box)
    clean_patch_mirrored = ImageOps.mirror(clean_patch)
    
    img.paste(clean_patch_mirrored, (star_x1, star_y1))
    return img

class SqueezingTechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Squeezing Tech Studio - Video Automation Suite")
        self.root.geometry("860x720")
        self.root.minsize(820, 640)
        self.root.configure(bg="#0F172A")

        self.bot_proc = None
        self.render_proc = None
        self.settings = load_settings()
        self.setup_styles()
        self.create_widgets()
        self.refresh_projects()
        self.restore_saved_state()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("TNotebook", background="#0F172A", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1E293B", foreground="#94A3B8", padding=[14, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#0284C7")], foreground=[("selected", "#FFFFFF")])

        style.configure("Dark.TFrame", background="#0F172A")
        style.configure("Card.TFrame", background="#1E293B", relief="flat")

        style.configure("Header.TLabel", background="#0F172A", foreground="#38BDF8", font=("Segoe UI", 16, "bold"))
        style.configure("SubHeader.TLabel", background="#0F172A", foreground="#94A3B8", font=("Segoe UI", 9))
        style.configure("Card.TLabel", background="#1E293B", foreground="#F8FAFC", font=("Segoe UI", 10))
        style.configure("CardMuted.TLabel", background="#1E293B", foreground="#94A3B8", font=("Segoe UI", 9))

        style.configure("Primary.TButton", background="#0284C7", foreground="#FFFFFF", font=("Segoe UI", 10, "bold"), padding=[10, 6])
        style.map("Primary.TButton", background=[("active", "#0369A1")])

        style.configure("Success.TButton", background="#16A34A", foreground="#FFFFFF", font=("Segoe UI", 10, "bold"), padding=[10, 6])
        style.map("Success.TButton", background=[("active", "#15803D")])

        style.configure("Danger.TButton", background="#DC2626", foreground="#FFFFFF", font=("Segoe UI", 9, "bold"), padding=[10, 6])
        style.map("Danger.TButton", background=[("active", "#B91C1C"), ("disabled", "#475569")])

        style.configure("Secondary.TButton", background="#334155", foreground="#F8FAFC", font=("Segoe UI", 9), padding=[8, 4])
        style.map("Secondary.TButton", background=[("active", "#475569")])

    def create_widgets(self):
        header_frame = ttk.Frame(self.root, style="Dark.TFrame")
        header_frame.pack(fill="x", padx=18, pady=(14, 8))

        lbl_title = ttk.Label(header_frame, text="SQUEEZING TECH STUDIO", style="Header.TLabel")
        lbl_title.pack(anchor="w")
        lbl_slogan = ttk.Label(header_frame, text="Vắt sạch thông số, giữ lại cách dùng. | Extracting Value from Everyday Tech", style="SubHeader.TLabel")
        lbl_slogan.pack(anchor="w", pady=(2, 0))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=18, pady=8)

        # Tab 1: Render Video
        tab_render = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(tab_render, text="  🎬 Dựng Video (Render)  ")
        self.build_render_tab(tab_render)

        # Tab 2: Xóa Logo/Star Gemini
        tab_watermark = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(tab_watermark, text="  ✨ Xóa Star/Logo Gemini  ")
        self.build_watermark_tab(tab_watermark)

        # Tab 3: Bot Auto Flow
        tab_bot = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(tab_bot, text="  🌐 Bot Google Flow  ")
        self.build_bot_tab(tab_bot)

        # Bottom Log Window
        log_frame = ttk.Frame(self.root, style="Dark.TFrame")
        log_frame.pack(fill="x", padx=18, pady=(4, 12))

        lbl_log = ttk.Label(log_frame, text="Nhật ký xử lý (Logs):", style="CardMuted.TLabel")
        lbl_log.pack(anchor="w", pady=(0, 2))

        self.txt_log = tk.Text(log_frame, height=7, bg="#020617", fg="#38BDF8", insertbackground="white", font=("Consolas", 9), relief="flat")
        self.txt_log.pack(fill="x")

    def build_render_tab(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        card.pack(fill="both", expand=True, padx=4, pady=6)

        # 1. Project selection
        p_frame = ttk.Frame(card, style="Card.TFrame")
        p_frame.pack(fill="x", pady=4)

        ttk.Label(p_frame, text="Chọn Thư Mục Dự Án:", style="Card.TLabel").pack(side="left")
        self.cbo_project = ttk.Combobox(p_frame, state="readonly", width=32, font=("Segoe UI", 9))
        self.cbo_project.pack(side="left", padx=8)
        self.cbo_project.bind("<<ComboboxSelected>>", self.on_project_selected)

        btn_refresh = ttk.Button(p_frame, text="Làm mới", style="Secondary.TButton", command=self.refresh_projects)
        btn_refresh.pack(side="left", padx=4)

        btn_new = ttk.Button(p_frame, text="+ Tạo Dự Án Mới", style="Primary.TButton", command=self.prompt_new_project)
        btn_new.pack(side="left", padx=4)

        # Project Info
        self.lbl_proj_info = ttk.Label(card, text="Trạng thái: Vui lòng chọn dự án...", style="CardMuted.TLabel")
        self.lbl_proj_info.pack(anchor="w", pady=(6, 10))

        # 2. Language Selection
        lang_frame = ttk.Frame(card, style="Card.TFrame")
        lang_frame.pack(fill="x", pady=4)

        ttk.Label(lang_frame, text="Ngôn Ngữ Video:", style="Card.TLabel", width=18).pack(side="left")
        self.var_lang = tk.StringVar(value="vi")
        
        rb_vi = tk.Radiobutton(lang_frame, text="🇻🇳 Tiếng Việt (Kênh Vắt Chanh)", variable=self.var_lang, value="vi", bg="#1E293B", fg="#4ADE80", selectcolor="#0F172A", activebackground="#1E293B", activeforeground="#4ADE80", font=("Segoe UI", 9, "bold"), command=self.on_lang_changed)
        rb_vi.pack(side="left", padx=(0, 16))

        rb_en = tk.Radiobutton(lang_frame, text="🇺🇸 Tiếng Anh (Kênh Squeezing Tech)", variable=self.var_lang, value="en", bg="#1E293B", fg="#38BDF8", selectcolor="#0F172A", activebackground="#1E293B", activeforeground="#38BDF8", font=("Segoe UI", 9, "bold"), command=self.on_lang_changed)
        rb_en.pack(side="left")

        # 3. Voice selection
        v_frame = ttk.Frame(card, style="Card.TFrame")
        v_frame.pack(fill="x", pady=6)

        ttk.Label(v_frame, text="Giọng Đọc AI (TTS):", style="Card.TLabel", width=18).pack(side="left")
        self.cbo_voice = ttk.Combobox(v_frame, state="readonly", width=38, font=("Segoe UI", 9))
        self.cbo_voice.pack(side="left", padx=4)

        self.btn_preview_voice = ttk.Button(v_frame, text="🔊 Nghe thử", style="Secondary.TButton", command=self.preview_voice_thread)
        self.btn_preview_voice.pack(side="left", padx=4)

        self.chk_force = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(v_frame, text="Ép tạo lại Audio", variable=self.chk_force, bg="#1E293B", fg="#94A3B8", selectcolor="#0F172A", activebackground="#1E293B", activeforeground="#FFFFFF")
        chk.pack(side="left", padx=6)

        self.chk_25d = tk.BooleanVar(value=False)
        chk_25d_btn = tk.Checkbutton(v_frame, text="✨ Tách nền 2.5D", variable=self.chk_25d, bg="#1E293B", fg="#94A3B8", selectcolor="#0F172A", activebackground="#1E293B", activeforeground="#38BDF8")
        chk_25d_btn.pack(side="left", padx=4)

        # 3b. BGM Preview & Selection
        bgm_frame = ttk.Frame(card, style="Card.TFrame")
        bgm_frame.pack(fill="x", pady=6)

        ttk.Label(bgm_frame, text="Nhạc Nền (BGM):", style="Card.TLabel", width=18).pack(side="left")
        self.lbl_bgm_info = ttk.Label(bgm_frame, text="Đang kiểm tra...", style="CardMuted.TLabel", width=28)
        self.lbl_bgm_info.pack(side="left", padx=4)

        self.btn_preview_bgm = ttk.Button(bgm_frame, text="🎵 Nghe Nhạc", style="Secondary.TButton", command=self.preview_bgm_thread)
        self.btn_preview_bgm.pack(side="left", padx=3)

        self.btn_preview_mix = ttk.Button(bgm_frame, text="🎧 Giọng + Nhạc", style="Secondary.TButton", command=self.preview_mix_thread)
        self.btn_preview_mix.pack(side="left", padx=3)

        self.btn_stop_audio = ttk.Button(bgm_frame, text="⏹ Dừng", style="Secondary.TButton", command=self.stop_audio_preview)
        self.btn_stop_audio.pack(side="left", padx=3)

        ttk.Button(bgm_frame, text="📂 Đổi Nhạc...", style="Secondary.TButton", command=self.change_bgm_file).pack(side="left", padx=3)

        # 4. Action Buttons
        act_frame = ttk.Frame(card, style="Card.TFrame")
        act_frame.pack(fill="x", pady=(18, 6))

        btn_open_folder = ttk.Button(act_frame, text="📂 Mở Thư Mục Ảnh (imgs)", style="Secondary.TButton", command=self.open_imgs_folder)
        btn_open_folder.pack(side="left", padx=4)

        self.btn_open_script = ttk.Button(act_frame, text="📝 Mở Thoại Tiếng Việt", style="Secondary.TButton", command=self.open_script_file)
        self.btn_open_script.pack(side="left", padx=4)

        self.btn_sort_media = ttk.Button(act_frame, text="🔀 Sort Resource", style="Primary.TButton", command=self.sort_project_resources)
        self.btn_sort_media.pack(side="left", padx=4)

        self.btn_stop_render = ttk.Button(act_frame, text="⏹ Hủy", style="Danger.TButton", command=self.stop_render_process, state="disabled")
        self.btn_stop_render.pack(side="right", padx=4)

        self.btn_render = ttk.Button(act_frame, text="🚀 BẮT ĐẦU RENDER VIDEO", style="Success.TButton", command=self.start_render_thread)
        self.btn_render.pack(side="right", padx=4)

        # 5. Render Progress Bar
        prog_frame = ttk.Frame(card, style="Card.TFrame")
        prog_frame.pack(fill="x", pady=(8, 2))

        self.render_progress = ttk.Progressbar(prog_frame, orient="horizontal", mode="determinate", maximum=100)
        self.render_progress.pack(side="left", fill="x", expand=True, padx=(4, 10))

        self.lbl_render_progress = ttk.Label(
            prog_frame,
            text="Tiến độ: Sẵn sàng (0%)",
            style="Card.TLabel",
            foreground="#94A3B8",
            font=("Segoe UI", 9, "bold"),
        )
        self.lbl_render_progress.pack(side="right", padx=4)

    def on_lang_changed(self):
        lang = self.var_lang.get()
        if lang == "vi":
            self.cbo_voice["values"] = [v[0] for v in VOICES_VI]
            saved_idx = self.settings.get("last_voice_vi_idx", 0)
            if 0 <= saved_idx < len(VOICES_VI):
                self.cbo_voice.current(saved_idx)
            else:
                self.cbo_voice.current(0)
            self.btn_open_script.config(text="📝 Mở Thoại Tiếng Việt (script_vi.txt)")
        else:
            self.cbo_voice["values"] = [v[0] for v in VOICES_EN]
            saved_idx = self.settings.get("last_voice_en_idx", 0)
            if 0 <= saved_idx < len(VOICES_EN):
                self.cbo_voice.current(saved_idx)
            else:
                self.cbo_voice.current(0)
            self.btn_open_script.config(text="📝 Mở Thoại Tiếng Anh (script_en.txt)")
        self.update_bgm_info()
        self.on_project_selected()

    def build_watermark_tab(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        card.pack(fill="both", expand=True, padx=4, pady=6)

        ttk.Label(card, text="Xóa logo ngôi sao 4 cánh của Google Flow (Đơn lẻ hoặc Toàn bộ thư mục):", style="Card.TLabel").pack(anchor="w", pady=(0, 6))

        self.var_wm_mode = tk.StringVar(value="batch")
        mode_frame = ttk.Frame(card, style="Card.TFrame")
        mode_frame.pack(fill="x", pady=(0, 8))

        rb_batch = tk.Radiobutton(mode_frame, text="📂 Xóa Toàn Bộ Ảnh Trong Thư Mục (Batch)", variable=self.var_wm_mode, value="batch", bg="#1E293B", fg="#38BDF8", selectcolor="#0F172A", activebackground="#1E293B", activeforeground="#38BDF8", font=("Segoe UI", 9, "bold"), command=self.toggle_wm_mode)
        rb_batch.pack(side="left", padx=(0, 16))

        rb_single = tk.Radiobutton(mode_frame, text="🖼️ Xóa 1 File Đơn Lẻ", variable=self.var_wm_mode, value="single", bg="#1E293B", fg="#94A3B8", selectcolor="#0F172A", activebackground="#1E293B", activeforeground="#FFFFFF", font=("Segoe UI", 9), command=self.toggle_wm_mode)
        rb_single.pack(side="left")

        self.f_in_dir = ttk.Frame(card, style="Card.TFrame")
        self.f_in_dir.pack(fill="x", pady=3)
        ttk.Label(self.f_in_dir, text="Thư mục ảnh gốc:", style="Card.TLabel", width=18).pack(side="left")
        self.ent_in_dir = ttk.Entry(self.f_in_dir, width=52)
        self.ent_in_dir.pack(side="left", padx=6)
        ttk.Button(self.f_in_dir, text="Chọn thư mục...", style="Secondary.TButton", command=self.browse_watermark_in_dir).pack(side="left")

        self.f_in_file = ttk.Frame(card, style="Card.TFrame")
        ttk.Label(self.f_in_file, text="File ảnh gốc:", style="Card.TLabel", width=18).pack(side="left")
        self.ent_img_in = ttk.Entry(self.f_in_file, width=52)
        self.ent_img_in.pack(side="left", padx=6)
        ttk.Button(self.f_in_file, text="Chọn file...", style="Secondary.TButton", command=self.browse_watermark_file).pack(side="left")

        f_out = ttk.Frame(card, style="Card.TFrame")
        f_out.pack(fill="x", pady=4)
        ttk.Label(f_out, text="Thư mục lưu ảnh sạch:", style="Card.TLabel", width=18).pack(side="left")
        self.ent_out_dir = ttk.Entry(f_out, width=52)
        self.ent_out_dir.pack(side="left", padx=6)
        ttk.Button(f_out, text="Đổi thư mục...", style="Secondary.TButton", command=self.browse_watermark_out_dir).pack(side="left")

        f_name_opt = ttk.Frame(card, style="Card.TFrame")
        f_name_opt.pack(fill="x", pady=6)
        ttk.Label(f_name_opt, text="Quy tắc đặt tên file:", style="Card.TLabel", width=18).pack(side="left")
        
        self.var_naming_mode = tk.StringVar(value="keep")
        rb_name_keep = tk.Radiobutton(f_name_opt, text="Giữ nguyên tên file gốc (Khuyên dùng)", variable=self.var_naming_mode, value="keep", bg="#1E293B", fg="#4ADE80", selectcolor="#0F172A", activebackground="#1E293B", activeforeground="#4ADE80", font=("Segoe UI", 9, "bold"))
        rb_name_keep.pack(side="left", padx=(0, 14))

        rb_name_prefix = tk.Radiobutton(f_name_opt, text="Thêm tiền tố 'clean_' vào trước tên file", variable=self.var_naming_mode, value="prefix", bg="#1E293B", fg="#94A3B8", selectcolor="#0F172A", activebackground="#1E293B", activeforeground="#FFFFFF", font=("Segoe UI", 9))
        rb_name_prefix.pack(side="left")

        btn_bar = ttk.Frame(card, style="Card.TFrame")
        btn_bar.pack(fill="x", pady=(12, 0))

        self.btn_clean_all = ttk.Button(btn_bar, text="🚀 XÓA SẠCH LOGO TOÀN BỘ THƯ MỤC", style="Primary.TButton", command=self.start_clean_watermark_thread)
        self.btn_clean_all.pack(side="left")

        btn_open_out = ttk.Button(btn_bar, text="📂 Mở Thư Mục Kết QuẢ", style="Secondary.TButton", command=self.open_out_dir)
        btn_open_out.pack(side="left", padx=10)

    def toggle_wm_mode(self):
        mode = self.var_wm_mode.get()
        if mode == "batch":
            self.f_in_file.pack_forget()
            self.f_in_dir.pack(fill="x", pady=3, before=self.ent_out_dir.master)
            self.btn_clean_all.config(text="🚀 XÓA SẠCH LOGO TOÀN BỘ THƯ MỤC")
        else:
            self.f_in_dir.pack_forget()
            self.f_in_file.pack(fill="x", pady=3, before=self.ent_out_dir.master)
            self.btn_clean_all.config(text="✨ Xóa Ngôi Sao File Này")

    def build_bot_tab(self, parent):
        card_ctrl = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card_ctrl.pack(fill="x", padx=4, pady=(6, 4))

        ttk.Label(card_ctrl, text="Tự động nạp danh sách prompt lên Flow.google qua Playwright:", style="Card.TLabel").pack(anchor="w", pady=(0, 6))

        f_p = ttk.Frame(card_ctrl, style="Card.TFrame")
        f_p.pack(fill="x", pady=2)
        ttk.Label(f_p, text="File prompt:", style="Card.TLabel", width=14).pack(side="left")
        self.ent_prompt_file = ttk.Entry(f_p, width=54)
        self.ent_prompt_file.pack(side="left", padx=6)
        ttk.Button(f_p, text="Chọn file...", style="Secondary.TButton", command=self.browse_prompt_file).pack(side="left")

        f_actions = ttk.Frame(card_ctrl, style="Card.TFrame")
        f_actions.pack(fill="x", pady=(10, 4))

        self.btn_run_bot = ttk.Button(f_actions, text="▶ Khởi Động Bot", style="Primary.TButton", command=self.run_bot_thread)
        self.btn_run_bot.pack(side="left", padx=(0, 8))

        self.btn_ready_bot = ttk.Button(f_actions, text="🚀 Sẵn Sàng", style="Success.TButton", command=self.on_bot_ready, state="disabled")
        self.btn_ready_bot.pack(side="left", padx=(0, 8))

        self.btn_stop_bot = ttk.Button(f_actions, text="⏹ Dừng Bot", style="Danger.TButton", command=self.stop_bot, state="disabled")
        self.btn_stop_bot.pack(side="left", padx=(0, 8))

        self.btn_clear_bot = ttk.Button(f_actions, text="🗑 Xóa Log", style="Secondary.TButton", command=self.clear_bot_log)
        self.btn_clear_bot.pack(side="left", padx=(0, 16))

        self.lbl_bot_status = ttk.Label(f_actions, text="Trạng thái: Sẵn sàng", style="Card.TLabel", foreground="#38BDF8", font=("Segoe UI", 9, "bold"))
        self.lbl_bot_status.pack(side="left", padx=(4, 0))

        f_prog = ttk.Frame(card_ctrl, style="Card.TFrame")
        f_prog.pack(fill="x", pady=(6, 2))
        self.bot_progress = ttk.Progressbar(f_prog, orient="horizontal", mode="determinate")
        self.bot_progress.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.lbl_bot_progress = ttk.Label(f_prog, text="Tiến độ: 0/0 prompt (0%)", style="CardMuted.TLabel")
        self.lbl_bot_progress.pack(side="right")

        card_log = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card_log.pack(fill="both", expand=True, padx=4, pady=(4, 6))

        f_log_header = ttk.Frame(card_log, style="Card.TFrame")
        f_log_header.pack(fill="x", pady=(0, 4))
        ttk.Label(f_log_header, text="Nhật ký chi tiết từng thao tác Bot:", style="Card.TLabel", font=("Segoe UI", 9, "bold")).pack(side="left")

        f_txt = ttk.Frame(card_log, style="Card.TFrame")
        f_txt.pack(fill="both", expand=True)

        scroll_y = ttk.Scrollbar(f_txt, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        self.txt_bot_log = tk.Text(
            f_txt, bg="#020617", fg="#F8FAFC", insertbackground="white",
            font=("Consolas", 9), relief="flat", wrap="word",
            yscrollcommand=scroll_y.set
        )
        self.txt_bot_log.pack(side="left", fill="both", expand=True)
        scroll_y.config(command=self.txt_bot_log.yview)

        self.txt_bot_log.tag_config("INFO", foreground="#38BDF8")
        self.txt_bot_log.tag_config("SUCCESS", foreground="#4ADE80")
        self.txt_bot_log.tag_config("WARN", foreground="#FBBF24")
        self.txt_bot_log.tag_config("ERROR", foreground="#F87171")
        self.txt_bot_log.tag_config("ACTION", foreground="#C084FC")
        self.txt_bot_log.tag_config("MUTED", foreground="#94A3B8")

    def restore_saved_state(self):
        saved_lang = self.settings.get("last_lang", "vi")
        self.var_lang.set(saved_lang)
        self.on_lang_changed()

        mode = self.settings.get("watermark_mode", "batch")
        self.var_wm_mode.set(mode)
        self.toggle_wm_mode()

        naming_mode = self.settings.get("watermark_naming_mode", "keep")
        self.var_naming_mode.set(naming_mode)

        in_dir = self.settings.get("watermark_in_dir", "")
        if in_dir and os.path.exists(in_dir):
            self.ent_in_dir.delete(0, "end")
            self.ent_in_dir.insert(0, in_dir)

        out_dir = self.settings.get("watermark_out_dir", "")
        if not out_dir or not os.path.exists(out_dir):
            out_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.ent_out_dir.delete(0, "end")
        self.ent_out_dir.insert(0, out_dir)

        in_file = self.settings.get("watermark_in_path", "")
        if in_file and os.path.exists(in_file):
            self.ent_img_in.delete(0, "end")
            self.ent_img_in.insert(0, in_file)

        p_file = self.settings.get("last_prompt_file", "")
        if p_file and os.path.exists(p_file):
            self.ent_prompt_file.delete(0, "end")
            self.ent_prompt_file.insert(0, p_file)

        last_proj = self.settings.get("last_project", "")
        if last_proj in self.cbo_project["values"]:
            self.cbo_project.set(last_proj)
            self.on_project_selected()

    def on_close(self):
        self.stop_audio_preview()
        if self.render_proc and self.render_proc.poll() is None:
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.render_proc.pid)], capture_output=True)
            except Exception:
                pass
        if self.bot_proc and self.bot_proc.poll() is None:
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.bot_proc.pid)], capture_output=True)
            except Exception:
                pass
        self.settings["last_lang"] = self.var_lang.get()
        if self.var_lang.get() == "vi":
            self.settings["last_voice_vi_idx"] = self.cbo_voice.current()
        else:
            self.settings["last_voice_en_idx"] = self.cbo_voice.current()
        self.settings["watermark_mode"] = self.var_wm_mode.get()
        self.settings["watermark_naming_mode"] = self.var_naming_mode.get()
        self.settings["watermark_in_dir"] = self.ent_in_dir.get().strip()
        self.settings["watermark_out_dir"] = self.ent_out_dir.get().strip()
        self.settings["watermark_in_path"] = self.ent_img_in.get().strip()
        self.settings["last_prompt_file"] = self.ent_prompt_file.get().strip()
        self.settings["last_project"] = self.cbo_project.get().strip()
        save_settings(self.settings)
        self.root.destroy()

    def log(self, text):
        self.txt_log.insert("end", text + "\n")
        self.txt_log.see("end")

    def refresh_projects(self):
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        items = sorted(os.listdir(PROJECTS_DIR))
        projs = [d for d in items if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
        self.cbo_project["values"] = projs
        if projs and not self.cbo_project.get():
            self.cbo_project.current(0)
            self.on_project_selected()

    def on_project_selected(self, event=None):
        proj_name = self.cbo_project.get()
        if not proj_name:
            return
        p_dir = os.path.join(PROJECTS_DIR, proj_name)
        lang = self.var_lang.get()

        media_dir = get_media_dir(p_dir, lang=lang)
        script_file = get_script_path(p_dir, lang=lang)

        valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.mp4', '.mov', '.webm')
        media_count = len([f for f in os.listdir(media_dir) if f.lower().endswith(valid_exts)]) if os.path.exists(media_dir) else 0
        line_count = 0
        if os.path.exists(script_file):
            with open(script_file, "r", encoding="utf-8", errors="ignore") as f:
                line_count = len([l.strip() for l in f if l.strip()])

        target_mp4 = f"{proj_name}_{lang}.mp4"
        is_rendered = os.path.exists(os.path.join(p_dir, target_mp4)) or (lang == "en" and os.path.exists(os.path.join(p_dir, f"{proj_name}.mp4")))
        video_txt = f"Video: {target_mp4}" if is_rendered else f"Video: Chưa render [{lang.upper()}]"
        
        self.lbl_proj_info.config(text=f"Trạng thái [{lang.upper()}]: 🖼️ {media_count} media ({os.path.basename(media_dir)}) | 📝 {line_count} câu ({os.path.basename(script_file)}) | 🎬 {video_txt}")

    def prompt_new_project(self):
        new_win = tk.Toplevel(self.root)
        new_win.title("Tạo dự án mới")
        new_win.geometry("380x140")
        new_win.configure(bg="#0F172A")
        new_win.grab_set()

        ttk.Label(new_win, text="Nhập tên thư mục dự án mới:", style="Card.TLabel").pack(pady=(16, 6))
        ent = ttk.Entry(new_win, width=32)
        ent.pack(pady=4)
        ent.focus()

        def do_create():
            name = ent.get().strip()
            if not name:
                return
            p_dir = os.path.join(PROJECTS_DIR, name)
            if os.path.exists(p_dir):
                messagebox.showerror("Lỗi", "Tên dự án đã tồn tại!")
                return
            os.makedirs(os.path.join(p_dir, "imgs"), exist_ok=True)
            with open(os.path.join(p_dir, "script_vi.txt"), "w", encoding="utf-8") as f:
                f.write("01. Cau thoai Tieng Viet canh mot.\n02. Cau thoai Tieng Viet canh hai.\n")
            with open(os.path.join(p_dir, "script_en.txt"), "w", encoding="utf-8") as f:
                f.write("01. English narration for scene one.\n02. English narration for scene two.\n")
            new_win.destroy()
            self.refresh_projects()
            self.cbo_project.set(name)
            self.on_project_selected()
            self.log(f"[OK] Đã tạo dự án mới: {name} (sẵn file script_vi.txt và script_en.txt)")

        ttk.Button(new_win, text="Tạo ngay", style="Primary.TButton", command=do_create).pack(pady=10)

    def open_imgs_folder(self):
        proj_name = self.cbo_project.get()
        if not proj_name:
            return
        p_dir = os.path.join(PROJECTS_DIR, proj_name)
        lang = self.var_lang.get()
        target_dir = get_media_dir(p_dir, lang=lang)
        os.makedirs(target_dir, exist_ok=True)
        os.startfile(target_dir)

    def open_script_file(self):
        proj_name = self.cbo_project.get()
        if not proj_name:
            return
        p_dir = os.path.join(PROJECTS_DIR, proj_name)
        lang = self.var_lang.get()
        script_file = get_script_path(p_dir, lang=lang)
        if not os.path.exists(script_file):
            with open(script_file, "w", encoding="utf-8") as f:
                f.write("01. Cau thoai dau tien.\n")
        os.startfile(script_file)

    def sort_project_resources(self):
        proj_name = self.cbo_project.get()
        if not proj_name:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dự án trước!")
            return

        p_dir = os.path.join(PROJECTS_DIR, proj_name)
        lang = self.var_lang.get()
        media_dir = get_media_dir(p_dir, lang=lang)
        video_prompt_file = os.path.join(p_dir, f"prompts_{lang}_video.txt")
        img_prompt_file = os.path.join(p_dir, f"prompts_{lang}_img.txt")

        has_vid_p = os.path.exists(video_prompt_file)
        has_img_p = os.path.exists(img_prompt_file)
        if not has_vid_p and not has_img_p:
            messagebox.showwarning(
                "Thiếu file prompt",
                f"Không tìm thấy prompts_{lang}_video.txt hoặc prompts_{lang}_img.txt trong {proj_name}!"
            )
            return

        if not os.path.exists(media_dir):
            messagebox.showwarning("Thiếu thư mục", f"Không tìm thấy thư mục media: {media_dir}")
            return

        self.log(f"--- SORT RESOURCE [{lang.upper()}]: {os.path.basename(media_dir)} ---")
        try:
            res = sort_media_by_prompts(
                media_dir,
                video_prompt_file=video_prompt_file if has_vid_p else None,
                img_prompt_file=img_prompt_file if has_img_p else None,
                sort_by="mtime"
            )
        except Exception as e:
            self.log(f"[LỖI SORT] {e}")
            messagebox.showerror("Lỗi", str(e))
            return

        for msg in res["skipped"]:
            self.log(f"  {msg}")
        for label, old_name, new_name in res["renamed"]:
            self.log(f"  [{label}] {old_name} -> {new_name}")
        for err in res["errors"]:
            self.log(f"  [CẢNH BÁO] {err}")

        self.on_project_selected()

        summary = f"Đã đổi tên {len(res['renamed'])} file theo thứ tự prompt."
        if res["errors"]:
            summary += "\n\nCảnh báo:\n" + "\n".join(res["errors"])
            messagebox.showwarning("Sort hoàn tất (Có cảnh báo)", summary)
        else:
            messagebox.showinfo("Sort hoàn tất", summary)

    # Audio & BGM Preview
    def update_bgm_info(self):
        lang = self.var_lang.get()
        bgm_path = get_bgm_path(lang=lang)
        if bgm_path:
            self.lbl_bgm_info.config(text=f"{os.path.basename(bgm_path)} (vol={DEFAULT_BGM_VOLUME})", foreground="#4ADE80")
        else:
            self.lbl_bgm_info.config(text=f"Chưa có bgm_{lang}.mp3 / bgm.mp3", foreground="#94A3B8")

    def _get_selected_voice(self):
        lang = self.var_lang.get()
        voice_list = VOICES_VI if lang == "vi" else VOICES_EN
        sel_idx = self.cbo_voice.current()
        voice_id = voice_list[sel_idx][1] if 0 <= sel_idx < len(voice_list) else voice_list[0][1]
        voice_label = voice_list[sel_idx][0] if 0 <= sel_idx < len(voice_list) else voice_list[0][0]
        return lang, voice_id, voice_label

    def _get_preview_sample_text(self, lang):
        if lang == "en":
            return "Hello, this is a voice preview for Squeezing Tech."
        return "Xin chào, đây là giọng đọc thử của kênh Vắt Chanh Công Nghệ."

    def _get_voice_preview_paths(self, lang, voice_id):
        safe_voice = "".join(c if c.isalnum() or c in "-_" else "_" for c in voice_id)
        pre_dir = os.path.join(RESOURCES_DIR, "voice_previews")
        mp3_path = os.path.join(pre_dir, f"{safe_voice}_{lang}.mp3")
        wav_path = os.path.join(pre_dir, f"{safe_voice}_{lang}.wav")
        return pre_dir, mp3_path, wav_path

    def _ensure_voice_preview_mp3(self, lang, voice_id, text):
        pre_dir, mp3_path, _ = self._get_voice_preview_paths(lang, voice_id)
        os.makedirs(pre_dir, exist_ok=True)
        synthesize_preview(text, mp3_path, voice=voice_id, lang=lang, force=self.chk_force.get())
        return mp3_path

    def _convert_to_wav(self, src_path, wav_path, max_sec=None):
        cmd = [FFMPEG_PATH, "-y"]
        if max_sec:
            cmd.extend(["-t", str(max_sec)])
        cmd.extend(["-i", src_path, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", wav_path])
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.decode("utf-8", errors="ignore")[-300:])
        return wav_path

    def _mix_to_wav(self, voice_mp3, bgm_path, wav_path):
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", voice_mp3,
            "-stream_loop", "-1", "-i", bgm_path,
            "-filter_complex",
            f"[1:a]volume={DEFAULT_BGM_VOLUME}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "[aout]",
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
            wav_path,
        ]
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.decode("utf-8", errors="ignore")[-300:])
        return wav_path

    def _play_wav(self, wav_path):
        winsound.PlaySound(None, 0)
        winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

    def stop_audio_preview(self):
        try:
            winsound.PlaySound(None, 0)
        except Exception:
            pass

    def _set_preview_buttons_state(self, state):
        self.btn_preview_voice.config(state=state)
        self.btn_preview_bgm.config(state=state)
        self.btn_preview_mix.config(state=state)

    def preview_voice_thread(self):
        lang, voice_id, voice_label = self._get_selected_voice()
        text = self._get_preview_sample_text(lang)
        self._set_preview_buttons_state("disabled")
        self.log(f"🔊 Đang tạo/phát thử giọng: {voice_label}")

        def run():
            try:
                _, _, wav_path = self._get_voice_preview_paths(lang, voice_id)
                if not self.chk_force.get() and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                    self.root.after(0, self._play_wav, wav_path)
                    self.root.after(0, self.log, f"  ▶ Phát ngay bản mẫu: {os.path.basename(wav_path)}")
                    return
                mp3_path = self._ensure_voice_preview_mp3(lang, voice_id, text)
                self._convert_to_wav(mp3_path, wav_path)
                self.root.after(0, self._play_wav, wav_path)
                self.root.after(0, self.log, f"  ▶ Đang phát giọng thử: \"{text}\"")
            except Exception as e:
                self.root.after(0, self.log, f"  [LỖI NGHE THỬ GIỌNG] {e}")
                self.root.after(0, messagebox.showerror, "Lỗi nghe thử giọng", str(e))
            finally:
                self.root.after(0, self._set_preview_buttons_state, "normal")

        threading.Thread(target=run, daemon=True).start()

    def preview_bgm_thread(self):
        lang = self.var_lang.get()
        bgm_path = get_bgm_path(lang=lang)
        if not bgm_path:
            messagebox.showwarning("Chưa có nhạc nền", f"Chưa tìm thấy resources/bgm_{lang}.mp3 hoặc bgm.mp3.\nBấm 'Đổi Nhạc...' để chọn file nhạc nền.")
            return

        self._set_preview_buttons_state("disabled")
        self.log(f"🎵 Đang phát thử nhạc nền (15s đầu): {os.path.basename(bgm_path)}")

        def run():
            try:
                cache_dir = os.path.join(BASE_DIR, "user_data", "preview_cache")
                os.makedirs(cache_dir, exist_ok=True)
                wav_path = os.path.join(cache_dir, f"bgm_preview_{lang}.wav")
                self._convert_to_wav(bgm_path, wav_path, max_sec=15)
                self.root.after(0, self._play_wav, wav_path)
            except Exception as e:
                self.root.after(0, self.log, f"  [LỖI NGHE NHẠC] {e}")
                self.root.after(0, messagebox.showerror, "Lỗi nghe nhạc nền", str(e))
            finally:
                self.root.after(0, self._set_preview_buttons_state, "normal")

        threading.Thread(target=run, daemon=True).start()

    def preview_mix_thread(self):
        lang, voice_id, voice_label = self._get_selected_voice()
        bgm_path = get_bgm_path(lang=lang)
        if not bgm_path:
            messagebox.showwarning("Chưa có nhạc nền", f"Chưa tìm thấy resources/bgm_{lang}.mp3 hoặc bgm.mp3.\nBấm 'Đổi Nhạc...' để chọn file nhạc nền.")
            return

        text = self._get_preview_sample_text(lang)
        self._set_preview_buttons_state("disabled")
        self.log(f"🎧 Đang trộn thử: {voice_label} + {os.path.basename(bgm_path)} (vol={DEFAULT_BGM_VOLUME})")

        def run():
            try:
                mp3_path = self._ensure_voice_preview_mp3(lang, voice_id, text)
                cache_dir = os.path.join(BASE_DIR, "user_data", "preview_cache")
                wav_path = os.path.join(cache_dir, f"mix_preview_{lang}.wav")
                self._mix_to_wav(mp3_path, bgm_path, wav_path)
                self.root.after(0, self._play_wav, wav_path)
                self.root.after(0, self.log, "  ▶ Đang phát bản trộn Giọng + Nhạc nền...")
            except Exception as e:
                self.root.after(0, self.log, f"  [LỖI TRỘN THỬ] {e}")
                self.root.after(0, messagebox.showerror, "Lỗi nghe thử trộn", str(e))
            finally:
                self.root.after(0, self._set_preview_buttons_state, "normal")

        threading.Thread(target=run, daemon=True).start()

    def change_bgm_file(self):
        path = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3;*.wav;*.m4a;*.aac;*.ogg")])
        if not path:
            return
        lang = self.var_lang.get()
        os.makedirs(RESOURCES_DIR, exist_ok=True)
        dest = os.path.join(RESOURCES_DIR, f"bgm_{lang}.mp3")
        try:
            if path.lower().endswith(".mp3"):
                shutil.copy2(path, dest)
            else:
                cmd = [FFMPEG_PATH, "-y", "-i", path, "-c:a", "libmp3lame", "-b:a", "192k", dest]
                res = subprocess.run(cmd, capture_output=True)
                if res.returncode != 0:
                    raise RuntimeError(res.stderr.decode("utf-8", errors="ignore")[-300:])
            self.update_bgm_info()
            self.log(f"[OK] Đã cập nhật nhạc nền [{lang.upper()}]: {dest}")
            messagebox.showinfo("Thành công", f"Đã lưu nhạc nền mới vào:\n{dest}")
        except Exception as e:
            self.log(f"[LỖI ĐỔI NHẠC] {e}")
            messagebox.showerror("Lỗi đổi nhạc nền", str(e))

    def set_render_progress(self, pct, status_text, fg="#38BDF8"):
        pct_clamped = max(0, min(100, int(pct)))
        self.render_progress["value"] = pct_clamped
        self.lbl_render_progress.config(text=f"Tiến độ: {status_text} ({pct_clamped}%)", foreground=fg)

    def update_render_progress_from_line(self, line):
        if not line:
            return

        if "[Buoc 1/4]" in line:
            self.set_render_progress(3, "Đang quét & chuẩn hóa media")
            return
        if "Tim thay" in line and "file media hop le" in line:
            self.set_render_progress(5, "Đã kiểm tra xong media")
            return
        if "[Buoc 2/4]" in line or "Generating voiceover" in line:
            self.set_render_progress(6, "Đang tạo giọng đọc AI (TTS)")
            return

        # Batch TTS request: [Batch 01..05/30]
        m_batch = re.search(r"\[Batch\s+(\d+)\.\.(\d+)/(\d+)\]", line)
        if m_batch:
            start_i, end_i, tot = int(m_batch.group(1)), int(m_batch.group(2)), max(1, int(m_batch.group(3)))
            pct = 6 + int(24 * ((start_i - 1) / tot))
            self.set_render_progress(pct, f"Đang gọi AI TTS câu {start_i:02d}..{end_i:02d}/{tot:02d}")
            return

        # Line TTS generated/cached: [05/30] Generated / Cached
        m_tts = re.search(r"\[(\d+)/(\d+)\]\s+(?:Generated|Cached)\s+", line)
        if m_tts:
            cur, tot = int(m_tts.group(1)), max(1, int(m_tts.group(2)))
            pct = 5 + int(25 * (cur / tot))
            self.set_render_progress(pct, f"Âm thanh TTS: {cur:02d}/{tot:02d} câu")
            return

        if "[Buoc 3/4]" in line:
            self.set_render_progress(32, "Đang đồng bộ phụ đề SRT")
            return
        if "[Buoc 4/4]" in line or "Auto-detected resolution" in line:
            self.set_render_progress(34, "Khởi tạo FFmpeg renderer")
            return
        if "Chuẩn hóa Intro video" in line:
            self.set_render_progress(35, "Đang chuẩn hóa video Intro")
            return

        # 2.5D Parallax pre-computation: [2.5D 05/22]
        m_25d = re.search(r"\[2\.5D\s+(\d+)/(\d+)\]", line)
        if m_25d:
            cur, tot = int(m_25d.group(1)), max(1, int(m_25d.group(2)))
            pct = 35 + int(20 * (cur / tot))
            self.set_render_progress(pct, f"Tách nền 2.5D: {cur:02d}/{tot:02d} ảnh")
            return

        if "Rendering " in line and " scenes using " in line:
            self.set_render_progress(55, "Đang dựng từng cảnh FFmpeg")
            return

        # Scene rendered: [05/30] Rendered
        m_scene = re.search(r"\[(\d+)/(\d+)\]\s+Rendered\s+", line)
        if m_scene:
            cur, tot = int(m_scene.group(1)), max(1, int(m_scene.group(2)))
            pct = 55 + int(33 * (cur / tot))
            self.set_render_progress(pct, f"Dựng cảnh FFmpeg: {cur:02d}/{tot:02d} cảnh")
            return

        if "Concatenating content scenes" in line:
            self.set_render_progress(90, "Đang ghép nối các cảnh")
            return
        if "Burning compact subtitles" in line:
            self.set_render_progress(93, "Đang đốt phụ đề SRT lên video")
            return
        if "Mixing background music" in line:
            self.set_render_progress(95, "Đang trộn nhạc nền BGM & đốt phụ đề")
            return
        if "Ghép Intro vào đầu video" in line:
            self.set_render_progress(98, "Đang ghép Intro vào đầu video")
            return
        if "[OK] Final video ready" in line or "[HOAN THANH]" in line:
            self.set_render_progress(100, "Hoàn tất", fg="#4ADE80")
            return

    def stop_render_process(self):
        if self.render_proc and self.render_proc.poll() is None:
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.render_proc.pid)], capture_output=True)
                self.log("[WARN] Đã hủy tiến trình render theo yêu cầu.")
                self.set_render_progress(self.render_progress["value"], "Đã hủy thủ công", fg="#FBBF24")
            except Exception as e:
                self.log(f"[LỖI HỦY RENDER] {e}")

    def start_render_thread(self):
        proj_name = self.cbo_project.get()
        if not proj_name:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dự án trước!")
            return

        lang = self.var_lang.get()
        voice_list = VOICES_VI if lang == "vi" else VOICES_EN
        sel_idx = self.cbo_voice.current()
        voice_id = voice_list[sel_idx][1] if 0 <= sel_idx < len(voice_list) else voice_list[0][1]
        force_flag = "--force" if self.chk_force.get() else ""
        use_25d_flag = "--25d" if self.chk_25d.get() else "--no-25d"

        self.btn_render.config(state="disabled")
        self.btn_stop_render.config(state="normal")
        self.set_render_progress(1, "Đang khởi động pipeline")
        self.log(f"--- BẮT ĐẦU RENDER [{lang.upper()}]: {proj_name} (Voice: {voice_id}) ---")

        def handle_output_line(text_line):
            self.log(text_line)
            self.update_render_progress_from_line(text_line)

        def run():
            cmd = [sys.executable, "-u", os.path.join(BASE_DIR, "make_video.py"), proj_name, "--lang", lang, "--voice", voice_id, use_25d_flag]
            if force_flag:
                cmd.append(force_flag)

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
            self.render_proc = proc
            for line in proc.stdout:
                clean = line.strip()
                if clean:
                    self.root.after(0, handle_output_line, clean)
            proc.wait()
            self.render_proc = None

            def finish():
                self.btn_render.config(state="normal")
                self.btn_stop_render.config(state="disabled")
                self.on_project_selected()
                if proc.returncode == 0:
                    self.set_render_progress(100, "Hoàn tất", fg="#4ADE80")
                    out_name = f"{proj_name}_{lang}.mp4"
                    messagebox.showinfo("Thành công", f"Đã dựng xong video [{lang.upper()}]:\n{out_name}")
                else:
                    if "Đã hủy" not in self.lbl_render_progress.cget("text"):
                        self.set_render_progress(self.render_progress["value"], "Lỗi / Dừng", fg="#F87171")
                    messagebox.showerror("Thất bại", "Quá trình render gặp lỗi hoặc đã bị hủy! Xem log bên dưới.")

            self.root.after(0, finish)

        threading.Thread(target=run, daemon=True).start()

    # Watermark Tool
    def browse_watermark_in_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.ent_in_dir.delete(0, "end")
            self.ent_in_dir.insert(0, d)

    def browse_watermark_file(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.webp")])
        if path:
            self.ent_img_in.delete(0, "end")
            self.ent_img_in.insert(0, path)

    def browse_watermark_out_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.ent_out_dir.delete(0, "end")
            self.ent_out_dir.insert(0, dir_path)

    def open_out_dir(self):
        out_dir = self.ent_out_dir.get().strip()
        if out_dir and os.path.exists(out_dir):
            os.startfile(out_dir)

    def start_clean_watermark_thread(self):
        out_dir = self.ent_out_dir.get().strip()
        if not out_dir or not os.path.exists(out_dir):
            messagebox.showerror("Lỗi", "Thư mục lưu ảnh không tồn tại!")
            return

        naming_mode = self.var_naming_mode.get()
        mode = self.var_wm_mode.get()

        if mode == "single":
            src_path = self.ent_img_in.get().strip()
            if not os.path.exists(src_path):
                messagebox.showerror("Lỗi", "Không tìm thấy file ảnh gốc!")
                return
            files_to_process = [src_path]
        else:
            in_dir = self.ent_in_dir.get().strip()
            if not os.path.exists(in_dir):
                messagebox.showerror("Lỗi", "Không tìm thấy thư mục ảnh gốc!")
                return
            valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
            files_to_process = [os.path.join(in_dir, f) for f in os.listdir(in_dir) if f.lower().endswith(valid_exts)]
            if not files_to_process:
                messagebox.showwarning("Thông báo", "Không tìm thấy file ảnh nào trong thư mục đã chọn!")
                return

        self.btn_clean_all.config(state="disabled")
        self.log(f"--- BẮT ĐẦU XÓA LOGO ({len(files_to_process)} ảnh) [Tên: {naming_mode.upper()}] ---")

        def run():
            success_count = 0
            for idx, img_path in enumerate(files_to_process, 1):
                try:
                    img = Image.open(img_path)
                    cleaned = remove_gemini_star_from_image(img)
                    base_name = os.path.basename(img_path)

                    if naming_mode == "keep":
                        final_name = base_name
                    else:
                        final_name = "clean_" + base_name if not base_name.startswith("clean_") else base_name

                    dest_path = os.path.join(out_dir, final_name)
                    cleaned.save(dest_path, quality=100)
                    success_count += 1
                    self.root.after(0, self.log, f"  [{idx}/{len(files_to_process)}] Đã lưu: {final_name}")
                except Exception as e:
                    self.root.after(0, self.log, f"  [LỖI] {os.path.basename(img_path)}: {e}")

            def finish():
                self.btn_clean_all.config(state="normal")
                self.log(f"[HOÀN THÀNH] Đã xóa logo xong {success_count}/{len(files_to_process)} ảnh tại: {out_dir}")
                messagebox.showinfo("Hoàn tất", f"Đã xóa logo xong {success_count}/{len(files_to_process)} ảnh!\nLưu tại: {out_dir}")

            self.root.after(0, finish)

        threading.Thread(target=run, daemon=True).start()

    # Bot Google Flow
    def browse_prompt_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.ent_prompt_file.delete(0, "end")
            self.ent_prompt_file.insert(0, path)

    def clear_bot_log(self):
        self.txt_bot_log.delete("1.0", "end")

    def append_bot_log(self, text):
        if not text:
            return
        if text.startswith("STATE:WAITING_READY"):
            self.btn_ready_bot.config(state="normal")
            self.lbl_bot_status.config(text="Trạng thái: Đang chờ bạn bấm Sẵn Sàng...", foreground="#FBBF24")
            return
        if text.startswith("PROGRESS:"):
            try:
                parts = text.replace("PROGRESS:", "").strip().split("/")
                cur, tot = int(parts[0]), int(parts[1])
                pct = int((cur / tot) * 100) if tot > 0 else 0
                self.bot_progress["value"] = pct
                self.lbl_bot_progress.config(text=f"Tiến độ: {cur}/{tot} prompt ({pct}%)")
            except Exception:
                pass
            return

        tag = "INFO"
        if any(w in text for w in ["[LỖI", "❌", "Traceback", "Error", "Exception"]):
            tag = "ERROR"
        elif any(w in text for w in ["[THÀNH CÔNG]", "✅", "🎉", "[HOÀN TẤT]"]):
            tag = "SUCCESS"
        elif any(w in text for w in ["[CẢNH BÁO]", "⚠️", "CHỜ", "ĐANG CHỜ", "TẠM DỪNG"]):
            tag = "WARN"
        elif any(w in text for w in ["[THAO TÁC]", "▶", "[BƯỚC", "🚀"]):
            tag = "ACTION"
        elif any(w in text for w in ["[HƯỚNG DẪN]", "💡"]):
            tag = "MUTED"

        self.txt_bot_log.insert("end", text + "\n", tag)
        self.txt_bot_log.see("end")
        self.log(text)

    def on_bot_ready(self):
        ready_flag = os.path.join(BASE_DIR, ".bot_ready")
        try:
            with open(ready_flag, "w", encoding="utf-8") as f:
                f.write("ready")
        except Exception as e:
            self.append_bot_log(f"[LỖI] Không thể ghi tín hiệu sẵn sàng: {e}")
            return
        self.btn_ready_bot.config(state="disabled")
        self.lbl_bot_status.config(text="Trạng thái: Đang nạp prompt...", foreground="#38BDF8")
        self.append_bot_log("🚀 [SẴN SÀNG] Đã xác nhận sẵn sàng! Bot bắt đầu quá trình nạp prompt vào Flow...")

    def run_bot_thread(self):
        prompt_file = self.ent_prompt_file.get().strip()
        if not os.path.exists(prompt_file):
            messagebox.showerror("Lỗi", "Không tìm thấy file prompt!")
            return

        if self.bot_proc and self.bot_proc.poll() is None:
            messagebox.showwarning("Cảnh báo", "Bot đang chạy! Bấm 'Dừng Bot' trước nếu muốn chạy lại.")
            return

        ready_flag = os.path.join(BASE_DIR, ".bot_ready")
        if os.path.exists(ready_flag):
            try:
                os.remove(ready_flag)
            except Exception:
                pass

        self.btn_run_bot.config(state="disabled")
        self.btn_ready_bot.config(state="disabled")
        self.btn_stop_bot.config(state="normal")
        self.lbl_bot_status.config(text="Trạng thái: Đang khởi động...", foreground="#38BDF8")
        self.bot_progress["value"] = 0
        self.lbl_bot_progress.config(text="Tiến độ: Đang khởi động...")

        self.append_bot_log("==================================================")
        self.append_bot_log(f"--- KHỞI ĐỘNG BOT GOOGLE FLOW: {os.path.basename(prompt_file)} ---")

        def run():
            cmd = [sys.executable, os.path.join(BASE_DIR, "auto_flow.py"), prompt_file]
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            try:
                self.bot_proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace", env=env
                )
                for line in self.bot_proc.stdout:
                    clean = line.strip()
                    if clean:
                        self.root.after(0, self.append_bot_log, clean)
                self.bot_proc.wait()
            except Exception as e:
                self.root.after(0, self.append_bot_log, f"[LỖI] Tiến trình bot gặp sự cố: {e}")

            def finish():
                self.btn_run_bot.config(state="normal")
                self.btn_ready_bot.config(state="disabled")
                self.btn_stop_bot.config(state="disabled")
                r_flag = os.path.join(BASE_DIR, ".bot_ready")
                if os.path.exists(r_flag):
                    try:
                        os.remove(r_flag)
                    except Exception:
                        pass
                if self.bot_proc and self.bot_proc.returncode == 0:
                    self.lbl_bot_status.config(text="Trạng thái: Đã hoàn tất", foreground="#4ADE80")
                else:
                    self.lbl_bot_status.config(text="Trạng thái: Đã dừng / Kết thúc", foreground="#FBBF24")

            self.root.after(0, finish)

        threading.Thread(target=run, daemon=True).start()

    def stop_bot(self):
        if self.bot_proc and self.bot_proc.poll() is None:
            self.append_bot_log("⚠️ [DỪNG KHẨN CẤP] Đang ngắt trình duyệt Chrome và hủy tiến trình Bot...")
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.bot_proc.pid)], capture_output=True)
            except Exception:
                try:
                    self.bot_proc.kill()
                except Exception:
                    pass
            self.append_bot_log("⏹ [ĐÃ DỪNG] Bot Google Flow đã ngừng hoạt động hoàn toàn.")

        self.btn_run_bot.config(state="normal")
        self.btn_ready_bot.config(state="disabled")
        self.btn_stop_bot.config(state="disabled")
        self.lbl_bot_status.config(text="Trạng thái: Đã dừng thủ công", foreground="#F87171")
        r_flag = os.path.join(BASE_DIR, ".bot_ready")
        if os.path.exists(r_flag):
            try:
                os.remove(r_flag)
            except Exception:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = SqueezingTechApp(root)
    root.mainloop()
