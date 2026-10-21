"""Write (and optionally render) beat-synced edit timelines automatically.

Usage: python tool/auto_assemble.py edits/work_batman.auto.json [--render]

Reads a config (see edits/work_batman.auto.json), finds the beat grid and the drop in the
song window, lays out slots (one per bar before the drop, one per beat after it, 2-beat holds on
anchor words), and fills each slot with a shot from the CLIP index that matches the slot's query.
Writes one timeline per variation to edits/auto/<name>_vN.json; --render also renders them to out/.

Shot rules: no shot (or another piece of the same shot) used twice, at most max_per_clip uses of one source clip, never the same clip
twice in a row, dark shots skipped, high-motion shots preferred after the drop.
"""
import json
import os
import random
import sys

import librosa
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from lyric_words import lyric_words  # noqa: E402
import render_edit  # noqa: E402


def beat_grid(song):
    y, sr = librosa.load(song, sr=22050)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    _, beats = librosa.beat.beat_track(y=y, sr=sr, units="time", start_bpm=float(np.atleast_1d(tempo)[0]),
                                       tightness=400)
    return y, sr, np.asarray(beats)


def find_drop(y, sr, start, end):
    """The drop = the biggest jump in bass energy inside the window (0.5 s before vs after)."""
    hop = 256
    spec = np.abs(librosa.stft(y, hop_length=hop))
    low = 20 * np.log10(spec[librosa.fft_frequencies(sr=sr) < 120].mean(0) + 1e-9)
    t = librosa.times_like(low, sr=sr, hop_length=hop)
    k = int(0.5 * sr / hop)
    idx = [i for i in range(k, len(low) - k) if start + 1 <= t[i] <= end - 1]
    i = max(idx, key=lambda i: low[i:i + k].mean() - low[i - k:i].mean())
    return float(t[i])


def text_chunks(words, end, big):
    """1-2 word pops, a new pop for every key word; each lasts until the next (max 0.9 s)."""
    chunks = []
    for w in words:
        key = w["word"].lower() in big
        if (chunks and len(chunks[-1]["words"]) < 2 and w["at"] - chunks[-1]["at"] < 0.22 and not key
                and chunks[-1]["words"][-1].lower() not in big):
            chunks[-1]["words"].append(w["word"])
        else:
            chunks.append({"at": w["at"], "words": [w["word"]]})
    return [{"text": " ".join(c["words"]).lower(), "from": c["at"],
             "to": round(min(chunks[i + 1]["at"] if i + 1 < len(chunks) else end, c["at"] + 0.9), 3),
             "size": 125, "y": "h*0.64"} for i, c in enumerate(chunks)]


class Picker:
    def __init__(self, cfg, rel, rng):
        import open_clip
        import torch
        idx = rel(cfg["index"])
        self.shots = json.load(open(os.path.join(idx, "shots.json")))
        self.emb = np.load(os.path.join(idx, "emb.npy"))
        self.model, _, _ = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
        self.tok = open_clip.get_tokenizer("ViT-B-32")
        self.torch = torch
        self.motion = np.array([s["motion"] for s in self.shots])
        self.ok = np.array([s["vid"] not in set(cfg.get("exclude_clips", [])) and s["dur"] >= 0.3
                            and cfg.get("min_brightness", 28) <= s["bright"] <= cfg.get("max_brightness", 140)
                            for s in self.shots])
        self.max_per_clip = cfg.get("max_per_clip", 4)
        self.rng, self.used, self.per_clip, self.last = rng, set(), {}, None
        self.cache = {}
        if cfg.get("character"):
            # drop the shots that look least like the character (other heroes, title cards, filler)
            c = self.sims(cfg["character"])
            self.ok &= c >= np.percentile(c, cfg.get("character_cut_percentile", 35))

    def sims(self, query):
        if query not in self.cache:
            with self.torch.no_grad():
                t = self.model.encode_text(self.tok([query]))
            t = (t / t.norm(dim=-1, keepdim=True)).numpy()[0]
            self.cache[query] = self.emb @ t
        return self.cache[query]

    def pick(self, query, after_drop):
        score = self.sims(query).copy()
        if after_drop:
            score += 0.002 * np.minimum(self.motion, 30)
        for i, s in enumerate(self.shots):
            if (not self.ok[i] or (s["vid"], s.get("shot")) in self.used or s["vid"] == self.last
                    or self.per_clip.get(s["vid"], 0) >= self.max_per_clip):
                score[i] = -9
        top = np.argsort(-score)[:4]
        i = int(self.rng.choices(list(top), weights=[4, 3, 2, 1][:len(top)])[0])
        s = self.shots[i]
        # pieces of one long shot look alike, so the whole original shot counts as used
        self.used.add((s["vid"], s.get("shot")))
        self.per_clip[s["vid"]] = self.per_clip.get(s["vid"], 0) + 1
        self.last = s["vid"]
        return s


def assemble(cfg, rel, beats, drop, words, variation):
    rng = random.Random(variation)
    start, end = cfg["window"]
    grid = [float(b) for b in beats if start - 0.05 <= b <= end + 0.05]
    di = int(np.argmin([abs(b - drop) for b in grid]))
    anchors = cfg.get("anchors", {})
    # anchor words snap to the nearest beat and hold for 2 beats
    hits = {}
    for w in words:
        q = anchors.get(w["word"].lower())
        if q:
            # nearest free beat; the drop beat belongs to the drop shot
            for j in sorted(range(len(grid) - 1), key=lambda j: abs(grid[j] - w["at"]))[:3]:
                if j != di and j not in hits and j - 1 not in hits:
                    hits[j] = q
                    break
    starts, i = [], 0
    while i < len(grid) - 1:
        starts.append(i)
        if i in hits:
            i = i + 2 if not i < di < i + 2 else di
        elif i < di:
            i = min(i + 4, di) if not any(i < h < min(i + 4, di) for h in hits) else min(h for h in hits if h > i)
        else:
            i += 1
    picker = Picker(cfg, rel, rng)
    montage = cfg["montage_queries"]
    slots = []
    for j in starts:
        if j == di:
            q, fx = cfg["drop_query"], ["punch", "shake"]
        elif j in hits:
            q, fx = hits[j], ["punch"] if j > di else []
        elif j < di:
            q, fx = rng.choice(cfg.get("breakdown_queries", montage)), []
        else:
            q, fx = rng.choice(montage), []
        s = picker.pick(q, j >= di)
        slots.append({"at": round(grid[j], 3), "clip": s["vid"], "from": round(s["start"], 2), "fx": fx, "note": q})
    flashes = sorted({round(grid[j], 3) for j in range(di, len(grid) - 1)
                      if j - di < 4 or (j - di) % 4 == 0 or j in hits})
    return {
        "audio": cfg["song"], "start": round(grid[0], 3), "end": round(grid[-1], 3),
        "sources": cfg["sources"], "boxes": cfg["boxes"],
        "slots": slots, "flashes": flashes,
        "text_style": cfg.get("text_style", "brat"), "text_fg": cfg.get("text_fg", "white"),
        "texts": text_chunks(words, grid[-1], set(cfg.get("big_words", []))),
    }


def main(cfg_path, render=False):
    cfg = json.load(open(cfg_path))
    base = os.path.dirname(os.path.abspath(cfg_path))
    rel = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    y, sr, beats = beat_grid(rel(cfg["song"]))
    start, end = cfg["window"]
    drop = cfg.get("drop") or find_drop(y, sr, start, end)
    print(f"tempo {60 / np.median(np.diff(beats)):.1f} BPM, drop at {drop:.2f}s")
    words = lyric_words(json.load(open(rel(cfg["whisper"]))), open(rel(cfg["lyrics"])).read(), start, end)
    name = os.path.basename(cfg_path).replace(".auto.json", "")
    out_dir = os.path.join(base, "auto")
    os.makedirs(out_dir, exist_ok=True)
    for v in range(1, cfg.get("variations", 3) + 1):
        tl = assemble(cfg, rel, beats, drop, words, v)
        # timelines in edits/auto/ resolve paths one level deeper than the config
        for k in ("audio", "sources", "boxes"):
            tl[k] = os.path.relpath(rel(tl[k]), out_dir)
        path = os.path.join(out_dir, f"{name}_v{v}.json")
        json.dump(tl, open(path, "w"), indent=1)
        print("wrote", path, f"({len(tl['slots'])} shots)")
        if render:
            out = os.path.join(base, "..", "out", f"{name}_v{v}.mp4")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            render_edit.main(path, out)


if __name__ == "__main__":
    main(sys.argv[1], "--render" in sys.argv)
