import os
import threading
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from scipy.ndimage import distance_transform_edt

_SESSION_LOCK = threading.Lock()
_REMBG_SESSION = None


def _get_rembg_session():
    """Lazily initializes and caches the shared rembg ONNX session."""
    global _REMBG_SESSION
    with _SESSION_LOCK:
        if _REMBG_SESSION is None:
            import onnxruntime as ort
            from rembg import new_session
            sess_opts = ort.SessionOptions()
            sess_opts.intra_op_num_threads = min(4, os.cpu_count() or 2)
            sess_opts.inter_op_num_threads = 1
            try:
                _REMBG_SESSION = new_session("u2net", sess_opts=sess_opts)
            except TypeError:
                _REMBG_SESSION = new_session("u2net")
        return _REMBG_SESSION


def _fill_background_hole(rgb_arr: np.ndarray, alpha_arr: np.ndarray) -> Image.Image:
    """
    Fills the foreground region in the background image using fast 1/4-scale
    nearest-neighbor interpolation + localized Gaussian blur so parallax movement
    never reveals a silhouette edge behind the foreground.
    """
    h, w = alpha_arr.shape[:2]
    scale = 4
    sw, sh = max(64, w // scale), max(64, h // scale)

    small_alpha = alpha_arr[::scale, ::scale]
    fg_mask_small = Image.fromarray((small_alpha > 15).astype(np.uint8) * 255, mode="L")
    dilated_small = fg_mask_small.filter(ImageFilter.MaxFilter(7))
    hole_mask_small = np.array(dilated_small) > 0

    orig_img = Image.fromarray(rgb_arr, mode="RGB")
    if not np.any(hole_mask_small) or np.all(hole_mask_small):
        return orig_img.filter(ImageFilter.GaussianBlur(radius=1.5))

    small_rgb = rgb_arr[::scale, ::scale]
    indices = distance_transform_edt(hole_mask_small, return_distances=False, return_indices=True)
    filled_small = small_rgb[indices[0], indices[1]]

    soft_filled_small = Image.fromarray(filled_small, mode="RGB").filter(ImageFilter.GaussianBlur(radius=4.5))
    soft_filled = soft_filled_small.resize((w, h), Image.Resampling.BILINEAR)

    feather_small = dilated_small.filter(ImageFilter.GaussianBlur(radius=2.0))
    feather_mask = feather_small.resize((w, h), Image.Resampling.BILINEAR)

    return Image.composite(soft_filled, orig_img, feather_mask)


def prepare_25d_layers(image_path: str, target_w: int, target_h: int, cache_dir: str):
    """
    Splits a static image into (fg_path, bg_path) at (target_w, target_h) for 2.5D parallax.
    Returns (None, None) if the image is mostly background or mostly foreground (e.g. full Bento Card),
    so the renderer can fall back to standard Ken Burns motion.
    """
    os.makedirs(cache_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(image_path))[0]
    mtime = int(os.path.getmtime(image_path))
    prefix = f"{stem}_{target_w}x{target_h}_{mtime}"

    fg_path = os.path.join(cache_dir, f"{prefix}.fg.png")
    bg_path = os.path.join(cache_dir, f"{prefix}.bg.jpg")
    legacy_bg_png = os.path.join(cache_dir, f"{prefix}.bg.png")
    skip_marker = os.path.join(cache_dir, f"{prefix}.skip")

    if os.path.exists(skip_marker):
        return None, None
    if os.path.exists(fg_path):
        if os.path.exists(bg_path):
            return fg_path, bg_path
        if os.path.exists(legacy_bg_png):
            return fg_path, legacy_bg_png

    with Image.open(image_path) as src:
        fitted = ImageOps.fit(src.convert("RGB"), (target_w, target_h), method=Image.Resampling.BILINEAR)

    from rembg import remove
    session = _get_rembg_session()
    fg_rgba = remove(fitted, session=session).convert("RGBA")

    rgba_arr = np.array(fg_rgba)
    alpha_arr = rgba_arr[:, :, 3]
    fg_ratio = float(np.mean(alpha_arr > 20))

    # Skip 2.5D for full-screen cards/diagrams or empty detections
    if fg_ratio < 0.03 or fg_ratio > 0.88:
        with open(skip_marker, "w", encoding="utf-8") as f:
            f.write(f"fg_ratio={fg_ratio:.3f}\n")
        return None, None

    rgb_arr = np.array(fitted)
    bg_img = _fill_background_hole(rgb_arr, alpha_arr)

    fg_rgba.save(fg_path, "PNG", compress_level=1)
    bg_img.save(bg_path, "JPEG", quality=92)
    return fg_path, bg_path
