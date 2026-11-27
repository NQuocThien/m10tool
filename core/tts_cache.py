"""
Content-aware cache for per-line TTS audio.

Audio files keep their legacy names (`NN_voice.mp3`) so renderers stay unchanged,
but each line's validity is tracked in `tts_manifest.json` by a hash of
(voice, style, text). Editing or inserting a script line therefore re-synthesizes
only the lines whose content actually changed.
"""
import hashlib
import json
import os

MANIFEST_NAME = "tts_manifest.json"
MANIFEST_VERSION = 1


def line_cache_key(text, voice, style):
    """Stable short hash identifying one synthesized line."""
    raw = f"{voice}\x1f{style or ''}\x1f{text}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def manifest_path(audio_dir):
    return os.path.join(audio_dir, MANIFEST_NAME)


def load_manifest(audio_dir):
    """Returns the manifest dict, or None when absent (legacy folder) or unreadable."""
    path = manifest_path(audio_dir)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("lines"), dict):
            return data
        print(f"  [WARN] {MANIFEST_NAME} sai định dạng, sẽ tạo lại audio cần thiết.", flush=True)
    except (OSError, ValueError) as e:
        print(f"  [WARN] Không đọc được {MANIFEST_NAME} ({e}), sẽ tạo lại audio cần thiết.", flush=True)
    return {"version": MANIFEST_VERSION, "lines": {}}


def save_manifest(audio_dir, manifest):
    """Writes the manifest atomically so an interrupted run never leaves a half-written file."""
    path = manifest_path(audio_dir)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def read_cached_voice(audio_dir):
    """Voice id used for the cached audio in this folder, if recorded."""
    manifest = load_manifest(audio_dir)
    return (manifest or {}).get("voice")


def has_audio(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0


def plan_line(idx, key, out_mp3, manifest, force):
    """
    Decides whether one line must be synthesized.
    Returns (needs_generation, reason).
    """
    if force:
        return True, "force"
    if not has_audio(out_mp3):
        return True, "missing"
    if manifest is None:
        # Legacy folder created before the manifest existed: adopt existing audio once.
        return False, "legacy"
    entry = manifest["lines"].get(f"{idx:02d}")
    if not entry:
        return True, "untracked"
    if entry.get("key") != key:
        return True, "changed"
    return False, "cached"


def record_lines(manifest, voice, entries):
    """
    Returns an updated manifest with `entries` = [(idx, key, text), ...] recorded,
    dropping entries beyond the current script length.
    """
    lines = {}
    for idx, key, text in entries:
        lines[f"{idx:02d}"] = {"key": key, "text": text}
    return {"version": MANIFEST_VERSION, "voice": voice, "lines": lines}
