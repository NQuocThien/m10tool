import os
import re

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}
VALID_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

def is_video_file(path):
    return os.path.splitext(path)[1].lower() in VIDEO_EXTENSIONS

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def get_sorted_images(imgs_dir, auto_prefix=True):
    """
    Returns a sorted list of image file paths in imgs_dir.
    If images are not yet numbered with 01_, 02_, ... and auto_prefix is True,
    it renames them with zero-padded prefixes to ensure strict ordering.
    """
    if not os.path.exists(imgs_dir):
        raise FileNotFoundError(f"Image directory not found: {imgs_dir}")

    files = [f for f in os.listdir(imgs_dir) if os.path.splitext(f)[1].lower() in VALID_EXTENSIONS]
    if not files:
        raise ValueError(f"No image files found in {imgs_dir}")

    # Check if already prefixed with numbers like '01_' or '1_'
    already_prefixed = all(re.match(r'^\d+[-_]', f) for f in files)

    if already_prefixed:
        files.sort(key=natural_sort_key)
    else:
        # Sort naturally and optionally add numeric prefix
        files.sort(key=natural_sort_key)
        if auto_prefix:
            renamed = []
            for idx, old_name in enumerate(files, 1):
                new_name = f"{idx:02d}_{old_name}"
                old_path = os.path.join(imgs_dir, old_name)
                new_path = os.path.join(imgs_dir, new_name)
                os.rename(old_path, new_path)
                renamed.append(new_name)
            files = renamed

    return [os.path.join(imgs_dir, f) for f in files]


def parse_prompt_scene_numbers(prompt_file):
    """
    Parse scene numbers from '# Cảnh XX ...' or '# Scene XX ...' comments
    preceding each non-empty prompt line.
    """
    if not prompt_file or not os.path.exists(prompt_file):
        return []

    scene_numbers = []
    last_scene_num = None
    scene_re = re.compile(r'(?:Cảnh|Scene)\s*(\d+)', re.IGNORECASE)

    with open(prompt_file, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                m = scene_re.search(line)
                if m:
                    last_scene_num = int(m.group(1))
                continue
            if last_scene_num is not None:
                scene_numbers.append(last_scene_num)
                last_scene_num = None

    return scene_numbers


def _strip_numeric_prefix(filename):
    return re.sub(r'^\d+[-_]+', '', filename)


def sort_media_by_prompts(media_dir, video_prompt_file=None, img_prompt_file=None, sort_by="mtime"):
    """
    Sort and rename downloaded videos and images in media_dir to match scene numbers
    in video_prompt_file and img_prompt_file.
    Existing files with numeric prefixes NOT in the target prompt list (e.g. [REUSE] mascot)
    are preserved untouched.
    """
    if not os.path.exists(media_dir):
        raise FileNotFoundError(f"Thư mục media không tồn tại: {media_dir}")

    video_scenes = parse_prompt_scene_numbers(video_prompt_file)
    img_scenes = parse_prompt_scene_numbers(img_prompt_file)

    all_files = [f for f in os.listdir(media_dir) if os.path.isfile(os.path.join(media_dir, f))]
    video_files = [f for f in all_files if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS]
    img_files = [f for f in all_files if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS]

    result = {"renamed": [], "skipped": [], "errors": []}

    def _process_group(files, scenes, label):
        if not scenes:
            return

        scene_set = set(scenes)
        candidates = []
        for f in files:
            m = re.match(r'^(\d+)[-_]', f)
            if m and int(m.group(1)) not in scene_set:
                result["skipped"].append(f"[{label}] Giữ nguyên file reuse/khác: {f}")
                continue
            candidates.append(f)

        if len(candidates) != len(scenes):
            result["errors"].append(
                f"[{label}] Số lượng không khớp: có {len(candidates)} file nhưng prompt cần {len(scenes)} cảnh {scenes}"
            )
            return

        if sort_by == "name":
            candidates.sort(key=natural_sort_key)
        else:
            candidates.sort(key=lambda fn: (os.path.getmtime(os.path.join(media_dir, fn)), natural_sort_key(fn)))

        temp_items = []
        for idx, (old_name, scene_num) in enumerate(zip(candidates, scenes)):
            old_path = os.path.join(media_dir, old_name)
            tmp_name = f"__sort_tmp_{label}_{idx:03d}_{old_name}"
            tmp_path = os.path.join(media_dir, tmp_name)
            os.rename(old_path, tmp_path)
            temp_items.append((tmp_path, old_name, scene_num))

        for tmp_path, old_name, scene_num in temp_items:
            clean_base = _strip_numeric_prefix(old_name)
            new_name = f"{scene_num:02d}_{clean_base}"
            new_path = os.path.join(media_dir, new_name)
            os.rename(tmp_path, new_path)
            result["renamed"].append((label, old_name, new_name))

    _process_group(video_files, video_scenes, "VIDEO")
    _process_group(img_files, img_scenes, "IMG")
    return result
