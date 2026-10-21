"""Word-level lyric timings for a window of a song.

Usage: python tool/lyric_words.py whisper_words.json lyrics.txt START END > words.json
whisper_words.json: output of transcribe.py; lyrics.txt: the real lyrics.
Unmatched words are placed by interpolating between matched neighbours.
"""
import difflib
import json
import re
import sys


def norm(x):
    return re.sub(r"[^a-z]", "", x.lower())


def lyric_words(segs, lyrics_text, start, end):
    hw = [w for s in segs for w in s["words"]]
    lw = [w for line in lyrics_text.splitlines() for w in line.split() if norm(w)]
    t = [None] * len(lw)
    sm = difflib.SequenceMatcher(None, [norm(w) for w in lw], [norm(w["w"]) for w in hw], autojunk=False)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            t[a + k] = hw[b + k]["s"]
    known = [i for i, v in enumerate(t) if v is not None]
    for i in range(len(t)):
        if t[i] is None:
            lo = max([k for k in known if k < i], default=None)
            hi = min([k for k in known if k > i], default=None)
            if lo is not None and hi is not None:
                t[i] = t[lo] + (t[hi] - t[lo]) * (i - lo) / (hi - lo)
    return [{"word": re.sub(r'[",.()]', "", w), "at": round(v, 3)} for w, v in zip(lw, t)
            if v is not None and start <= v < end]


if __name__ == "__main__":
    out = lyric_words(json.load(open(sys.argv[1])), open(sys.argv[2]).read(), float(sys.argv[3]), float(sys.argv[4]))
    json.dump(out, sys.stdout, indent=0)
