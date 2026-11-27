import os
import re
import subprocess
from .config import FFMPEG_PATH, HIGHLIGHT_UNITS, SHORT_WORDS_PER_CAPTION


def get_audio_duration(audio_path):
    """Probes exact audio duration in seconds using ffmpeg."""
    cmd = [FFMPEG_PATH, "-i", audio_path]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            t_str = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t_str.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 5.0


def fmt_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        ms = 999
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_subtitle_chunks(text, max_words=9):
    """
    Splits a long sentence into natural 5-9 word reading chunks for dynamic SRT pacing.
    """
    text = text.strip()
    if not text:
        return []

    words = text.split()
    if len(words) <= max_words:
        return [text]

    # 1. Split by natural clause punctuation first (keep punctuation attached)
    raw_clauses = re.split(r'(?<=[,;:\.\?\!—])\s+', text)
    merged_clauses = []
    for cl in raw_clauses:
        cl = cl.strip()
        if not cl:
            continue
        if merged_clauses and len(merged_clauses[-1].split()) < 3:
            merged_clauses[-1] = f"{merged_clauses[-1]} {cl}"
        elif len(cl.split()) < 3 and merged_clauses:
            merged_clauses[-1] = f"{merged_clauses[-1]} {cl}"
        else:
            merged_clauses.append(cl)

    # 2. Further split any clause still exceeding max_words into balanced halves
    final_chunks = []
    for cl in merged_clauses:
        cl_words = cl.split()
        if len(cl_words) <= max_words:
            final_chunks.append(cl)
        else:
            num_parts = (len(cl_words) + max_words - 1) // max_words
            step = (len(cl_words) + num_parts - 1) // num_parts
            for i in range(0, len(cl_words), step):
                part = " ".join(cl_words[i:i + step]).strip()
                if part:
                    final_chunks.append(part)

    return final_chunks if final_chunks else [text]


def _group_atomic_tokens(words):
    """Glue [number + unit] pairs into atomic tokens so '3 triệu' or '65 W' never splits mid-phrase."""
    atoms = []
    i = 0
    while i < len(words):
        w = words[i]
        clean_w = w.strip(".,!?:;\"'()[]{}—–-")
        has_digit = any(ch.isdigit() for ch in clean_w)
        if has_digit and (i + 1) < len(words):
            next_clean = words[i + 1].strip(".,!?:;\"'()[]{}—–-").lower()
            if next_clean in HIGHLIGHT_UNITS:
                atoms.append(f"{w} {words[i + 1]}")
                i += 2
                continue
        atoms.append(w)
        i += 1
    return atoms


def split_short_caption_chunks(text, max_words=SHORT_WORDS_PER_CAPTION):
    """
    Splits a spoken sentence into punchy 3-5 word dynamic caption beats for 9:16 Shorts.
    Preserves clause pauses and keeps [number + unit] pairs together.
    """
    text = text.strip()
    if not text:
        return []

    raw_clauses = [c.strip() for c in re.split(r'(?<=[,;:\.\?\!—])\s+', text) if c.strip()]
    if not raw_clauses:
        raw_clauses = [text]

    chunks = []
    for clause in raw_clauses:
        # Remove standalone em-dash tokens so captions look clean on mobile
        clause_clean = re.sub(r'\s+—\s+', ' ', clause).strip(" —–")
        if not clause_clean:
            continue
        atoms = _group_atomic_tokens(clause_clean.split())
        total_w = sum(len(a.split()) for a in atoms)
        if total_w <= max_words + 1:
            chunks.append(" ".join(atoms))
            continue

        cur_atoms = []
        cur_w = 0
        for atom in atoms:
            aw = len(atom.split())
            if cur_atoms and (cur_w + aw) > max_words:
                chunks.append(" ".join(cur_atoms))
                cur_atoms = [atom]
                cur_w = aw
            else:
                cur_atoms.append(atom)
                cur_w += aw

        if cur_atoms:
            # Merge single-word trailing orphan into previous chunk of same clause
            if cur_w == 1 and chunks:
                chunks[-1] = f"{chunks[-1]} {' '.join(cur_atoms)}"
            else:
                chunks.append(" ".join(cur_atoms))

    return chunks if chunks else [text]


def compute_caption_cue_timings(text, duration, max_words=SHORT_WORDS_PER_CAPTION):
    """
    Maps dynamic 3-5 word caption chunks onto [0.0 .. duration] with natural speech & punctuation weights.
    Returns: [{'start': float, 'end': float, 'text': str}, ...]
    """
    dur = max(0.2, float(duration))
    chunks = split_short_caption_chunks(text, max_words=max_words)
    if not chunks:
        return [{"start": 0.0, "end": dur, "text": ""}]
    if len(chunks) == 1:
        return [{"start": 0.0, "end": dur, "text": chunks[0]}]

    weights = []
    for ch in chunks:
        char_len = max(2, len(re.sub(r'\s+', '', ch)))
        pause_bonus = 3.5 if ch[-1] in ",;:.?!—" else 0.0
        weights.append(char_len + pause_bonus)

    total_w = max(1.0, sum(weights))
    cues = []
    cum_w = 0.0
    prev_end = 0.0
    for idx, (ch, w) in enumerate(zip(chunks, weights)):
        cum_w += w
        end_t = dur if idx == len(chunks) - 1 else (dur * (cum_w / total_w))
        cues.append({
            "start": round(prev_end, 3),
            "end": round(max(prev_end, end_t), 3),
            "text": ch,
        })
        prev_end = cues[-1]["end"]
    cues[-1]["end"] = round(dur, 3)
    return cues


def generate_subtitles(audio_items, srt_path):
    """
    Takes audio items [{'index': 1, 'text': '...', 'audio_path': '...'}]
    Computes exact scene timestamps AND writes dynamic multi-chunk SRT entries.
    Returns list of items enriched with scene 'start', 'end', and 'duration'.
    """
    enriched = []
    current_time = 0.0
    srt_counter = 1

    with open(srt_path, "w", encoding="utf-8") as f:
        for item in audio_items:
            dur = get_audio_duration(item["audio_path"])
            start_t = current_time
            end_t = current_time + dur

            chunks = split_subtitle_chunks(item["text"])
            total_chars = max(1, sum(len(c) for c in chunks))
            chunk_cursor = start_t

            for i, chunk in enumerate(chunks):
                if i == len(chunks) - 1:
                    chunk_end = end_t
                else:
                    ratio = len(chunk) / total_chars
                    chunk_end = min(end_t, chunk_cursor + dur * ratio)

                f.write(f"{srt_counter}\n")
                f.write(f"{fmt_srt_time(chunk_cursor)} --> {fmt_srt_time(chunk_end)}\n")
                f.write(f"{chunk}\n\n")
                srt_counter += 1
                chunk_cursor = chunk_end

            enriched.append({
                **item,
                "duration": dur,
                "start": start_t,
                "end": end_t,
            })
            current_time = end_t

    print(f"📝 Synced subtitles saved: {srt_path} ({srt_counter - 1} cues, Total: {current_time:.2f}s)")
    return enriched
