import os
import re

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

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
