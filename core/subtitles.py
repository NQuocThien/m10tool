import os
import subprocess
from .config import FFMPEG_PATH

def get_audio_duration(audio_path):
    """Probes exact audio duration in seconds using ffmpeg."""
    cmd = [FFMPEG_PATH, "-i", audio_path]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            t_str = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t_str.split(":")
            return float(h)*3600 + float(m)*60 + float(s)
    return 5.0

def fmt_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def generate_subtitles(audio_items, srt_path):
    """
    Takes audio items [{'index': 1, 'text': '...', 'audio_path': '...'}]
    Computes exact timestamps and writes out a synchronized SRT file.
    Returns list of items enriched with 'start', 'end', and 'duration'.
    """
    enriched = []
    current_time = 0.0
    
    with open(srt_path, "w", encoding="utf-8") as f:
        for item in audio_items:
            dur = get_audio_duration(item["audio_path"])
            start_t = current_time
            end_t = current_time + dur
            
            f.write(f"{item['index']}\n")
            f.write(f"{fmt_srt_time(start_t)} --> {fmt_srt_time(end_t)}\n")
            f.write(f"{item['text']}\n\n")
            
            enriched.append({
                **item,
                "duration": dur,
                "start": start_t,
                "end": end_t
            })
            current_time = end_t
            
    print(f"📝 Synced subtitles saved: {srt_path} (Total: {current_time:.2f}s)")
    return enriched
