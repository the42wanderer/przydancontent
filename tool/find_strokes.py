"""Find bat-on-ball moments for boundaries in a cricket highlights video.

Usage: python tool/find_strokes.py AUDIO WHISPER.json START END [OUT.json] [INDEX OFFSET]

With INDEX (a shot index of the same footage, OFFSET = where that clip starts in the audio), only
shots that look like the camera behind the bowler count, and each gives at most its loudest crack.

A boundary leaves two traces: the crack of the bat (a sharp high-frequency transient) and the
commentator saying "four" or "six" within a few seconds. Prints/writes the contact times
(seconds in the source) of cracks followed by such a call; check them on a contact sheet.
"""
import json
import os
import re
import subprocess
import sys

import numpy as np
import librosa

audio, whisper, start, end = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
SR = 22050
pcm = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(start), "-t", str(end - start), "-i", audio,
                      "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
y = np.frombuffer(pcm, np.float32)
# the crack lives above the commentary voice: onset strength on the 2-8 kHz band only
spec = np.abs(librosa.stft(y, n_fft=1024, hop_length=256))
f = librosa.fft_frequencies(sr=SR, n_fft=1024)
band = spec[(f > 2000) & (f < 8000)]
env = np.maximum(0, np.diff(np.log1p(band), axis=1)).sum(0)
t = start + (np.arange(len(env)) + 1) * 256 / SR
peaks = librosa.util.peak_pick(env, pre_max=20, post_max=20, pre_avg=40, post_avg=40,
                               delta=np.percentile(env, 99) * 0.25, wait=40)

calls = [(w["s"], w["w"].lower()) for s in json.load(open(whisper)) for w in s["words"]
         if start <= w["s"] <= end + 6 and re.search(r"\b(four|six|boundary|maximum)\b", w["w"], re.I)]
def called(ct):
    return any(0.3 < s - ct < 4.5 for s, _ in calls)


hits = []
if len(sys.argv) > 7:
    import open_clip
    import torch
    idx, off = sys.argv[6], float(sys.argv[7])
    shots = json.load(open(idx + "/shots.json"))
    emb = np.load(idx + "/emb.npy")
    model, _, _ = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
    with torch.no_grad():
        q = model.encode_text(open_clip.get_tokenizer("ViT-B-32")(
            ["a cricket batsman at the crease seen from behind the bowler, the pitch in the middle"]))
    q = (q / q.norm(dim=-1, keepdim=True)).numpy()[0]
    sim = emb @ q
    for i in np.argsort(-sim)[:int(len(shots) * 0.35)]:
        a, b = shots[i]["start"] + off, shots[i]["end"] + off
        m = (t >= a + 0.3) & (t <= b)
        if not m.any():
            continue
        k = int(np.argmax(np.where(m, env, 0)))
        # ANY=1: keep every sharp crack, not only those the commentator calls
        if called(float(t[k])) or (os.environ.get("ANY") and env[k] > np.percentile(env, 99.5)):
            hits.append({"t": round(float(t[k]), 2), "strength": round(float(env[k]), 1), "shot": shots[i]["id"]})
    hits.sort(key=lambda h: h["t"])
else:
    for p in peaks:
        ct = float(t[p])
        if called(ct) and (not hits or ct - hits[-1]["t"] > 4):
            hits.append({"t": round(ct, 2), "strength": round(float(env[p]), 1)})
print(f"{len(hits)} boundary contacts between {start} and {end}")
for h in hits:
    print(h["t"], h["strength"])
if len(sys.argv) > 5:
    json.dump(hits, open(sys.argv[5], "w"), indent=1)
