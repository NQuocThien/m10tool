"""
Vietnamese text helpers for the single-language channel:
- group_caption_atoms(): glue [number + unit] and compound words so captions never split "nhu / cầu".
- normalize_for_tts(): rewrite tech terms/units into how they should be spoken (subtitles keep the original).

Both read editable data files in resources/ so wording can be tuned without touching code.
"""
import json
import os
import re
from functools import lru_cache

from .config import HIGHLIGHT_UNITS, RESOURCES_DIR

COMPOUND_WORDS_PATH = os.path.join(RESOURCES_DIR, "vi_compound_words.txt")
PRONUNCIATION_PATH = os.path.join(RESOURCES_DIR, "pronunciation_vi.json")

_PUNCT = ".,!?:;\"'()[]{}—–-…"
_MAX_COMPOUND_LEN = 4


def _clean(word):
    return word.strip(_PUNCT).lower()


@lru_cache(maxsize=1)
def load_compound_words(path=COMPOUND_WORDS_PATH):
    """Returns a frozenset of lowercase multi-syllable phrases (single syllables are ignored)."""
    phrases = set()
    if not os.path.isfile(path):
        return frozenset()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip().lower()
            if line and not line.startswith("#") and len(line.split()) >= 2:
                phrases.add(" ".join(line.split()))
    return frozenset(phrases)


def _ends_clause(word):
    """A word carrying , . ! ? etc. closes a clause: never glue across it."""
    return word[-1:] in ",;:.?!—…" if word else False


def group_caption_atoms(words, compounds=None):
    """
    Groups words into unbreakable atoms:
    - [number + unit] pairs ('3 triệu', '65 W')
    - known compound words, longest match first ('xe máy điện', 'nhu cầu')
    """
    if compounds is None:
        compounds = load_compound_words()
    atoms = []
    i = 0
    n = len(words)
    while i < n:
        w = words[i]
        clean_w = _clean(w)

        if any(ch.isdigit() for ch in clean_w) and i + 1 < n and not _ends_clause(w):
            if _clean(words[i + 1]) in HIGHLIGHT_UNITS:
                atoms.append(f"{w} {words[i + 1]}")
                i += 2
                continue

        matched = 1
        for size in range(min(_MAX_COMPOUND_LEN, n - i), 1, -1):
            span = words[i:i + size]
            if any(_ends_clause(x) for x in span[:-1]):
                continue
            if " ".join(_clean(x) for x in span) in compounds:
                matched = size
                break
        atoms.append(" ".join(words[i:i + matched]))
        i += matched
    return atoms


# Function words that usually START a new phrase: a good place to break a caption line.
_PHRASE_START_WORDS = frozenset({
    "là", "của", "và", "với", "để", "cho", "trong", "ngoài", "trên", "dưới", "khi", "nhưng",
    "mà", "thì", "nên", "vì", "do", "nếu", "hay", "hoặc", "rồi", "sau", "trước", "giữa",
    "bằng", "như", "từ", "tới", "đến", "vẫn", "đã", "đang", "sẽ", "chỉ", "cũng", "được", "bị",
})


def is_phrase_start(atom):
    """True when a caption atom opens a new phrase (function word or a punctuation-led token)."""
    first = atom.split()[0] if atom else ""
    return _clean(first) in _PHRASE_START_WORDS


@lru_cache(maxsize=1)
def _load_pronunciation_rules(path=PRONUNCIATION_PATH):
    """Compiles the pronunciation dictionary into ordered (regex, replacement) rules."""
    if not os.path.isfile(path):
        return ()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        print(f"  [WARN] Không đọc được {os.path.basename(path)} ({e}) -> bỏ qua chuẩn hóa phát âm.", flush=True)
        return ()

    rules = []
    terms = data.get("terms", {}) or {}
    for term in sorted(terms, key=len, reverse=True):
        pattern = re.compile(rf"(?<![\w-]){re.escape(term)}(?![\w-])")
        rules.append((pattern, terms[term]))

    units = data.get("units", {}) or {}
    for unit in sorted(units, key=len, reverse=True):
        # number (optionally decimal) + optional space + unit, not followed by more letters/digits
        pattern = re.compile(rf"(\d+(?:[.,]\d+)?)\s?{re.escape(unit)}(?![\wÀ-ỹ])")
        spoken = units[unit]
        rules.append((pattern, lambda m, s=spoken: f"{m.group(1)} {s}"))
    return tuple(rules)


def normalize_for_tts(text):
    """Returns the text the narrator should actually speak (terms/units expanded)."""
    spoken = text
    for pattern, repl in _load_pronunciation_rules():
        spoken = pattern.sub(repl, spoken)
    return spoken
