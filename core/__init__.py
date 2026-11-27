# Video Generator Core Package (Vắt Chanh Công Nghệ - Vietnamese-only channel)
import sys


def _ensure_utf8_console():
    """Windows consoles default to cp1252: force UTF-8 so Vietnamese log lines never crash a render."""
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure") and (stream.encoding or "").lower() != "utf-8":
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


_ensure_utf8_console()
