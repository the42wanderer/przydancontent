"""Render a beat-synced vertical edit from a timeline JSON.

Usage: python tool/render_edit.py edits/work_holygrail.json out/work_holygrail.mp4

Timeline format (times in song seconds):
{
  "audio": "path/to/song.mp3",
  "start": 110.62, "end": 130.334,
  "sources": "dir with source clips", "boxes": "content boxes json",
  "slots": [{"at": 110.62, "clip": "<video id>", "from": 4.5, "fx": ["punch"]}, ...],
  "flashes": [116.611, ...],
  "texts": [{"text": "PRZYDAN", "from": 113.3, "to": 116.5}]
}
Each slot runs until the next slot's "at" (the last one until "end").
fx: "punch" = zoom-in that settles over 0.3 s, "shake" = 0.4 s camera shake.
"""
import json
import os
import subprocess
import sys
import tempfile

W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
GRADE = "eq=contrast=1.1:brightness=0.03:saturation=1.15:gamma=1.2,colorbalance=rs=0.04:bs=0.05:rh=0.05:bh=-0.03"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(p.stderr[-2000:])


def segment_filter(box, fx, dur):
    x0, y0, x1, y1 = box
    f = [f"crop={x1 - x0}:{y1 - y0}:{x0}:{y0}",
         f"scale={W}:{H}:force_original_aspect_ratio=increase", f"crop={W}:{H}", f"fps={FPS}"]
    if fx:
        # zoompan counts output frames in "on": punch settles over 9 frames, shake over 12
        z = "1" + ("+0.18*max(0,1-on/9)" if "punch" in fx else "") + ("+0.08" if "shake" in fx else "")
        sx = "+28*sin(on*3.2)*max(0,1-on/12)" if "shake" in fx else ""
        sy = "+22*cos(on*2.7)*max(0,1-on/12)" if "shake" in fx else ""
        f.append(f"zoompan=z='{z}':x='iw/2-iw/zoom/2{sx}':y='ih/2-ih/zoom/2{sy}':d=1:s={W}x{H}:fps={FPS}")
    f += [GRADE, "setsar=1", "format=yuv420p"]
    return ",".join(f)


def main(timeline_path, out_path):
    tl = json.load(open(timeline_path))
    base = os.path.dirname(os.path.abspath(timeline_path))
    rel = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    boxes = json.load(open(rel(tl["boxes"])))
    slots = tl["slots"]
    tmp = tempfile.mkdtemp()
    parts = []
    for i, s in enumerate(slots):
        end = slots[i + 1]["at"] if i + 1 < len(slots) else tl["end"]
        dur = end - s["at"]
        frames = max(1, round(end * FPS) - round(s["at"] * FPS))
        part = os.path.join(tmp, f"{i:03d}.mp4")
        src = os.path.join(rel(tl["sources"]), s["clip"] + ".mp4")
        run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(s["from"]), "-i", src, "-t", f"{dur + 0.2:.3f}",
             "-vf", segment_filter(boxes[s["clip"]], s.get("fx", []), dur), "-frames:v", str(frames),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", part])
        parts.append(part)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    joined = os.path.join(tmp, "joined.mp4")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])

    t0 = tl["start"]
    post = []
    for t in tl.get("flashes", []):
        a = t - t0
        post.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:t=fill:enable='between(t,{a:.3f},{a + 0.067:.3f})'")
        post.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.35:t=fill:enable='between(t,{a + 0.067:.3f},{a + 0.13:.3f})'")
    for tx in tl.get("texts", []):
        a, b = tx["from"] - t0, tx["to"] - t0
        # a straight quote cannot be escaped inside ffmpeg's quoted option, so use a typographic one
        txt = tx["text"].replace(":", r"\:").replace("'", "’")
        post.append(f"drawtext=fontfile={FONT}:text='{txt}':fontsize={tx.get('size', 150)}:fontcolor=white"
                    f":borderw=6:bordercolor=black@0.6:x=(w-text_w)/2:y={tx.get('y', '(h-text_h)/2')}"
                    f":enable='between(t,{a:.3f},{b:.3f})'")
    vf = ",".join(post) or "null"
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", joined, "-ss", str(t0), "-t", f"{tl['end'] - t0:.3f}", "-i", rel(tl["audio"]),
         "-vf", vf, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path])
    print("wrote", out_path)


if __name__ == "__main__":
    main(*sys.argv[1:3])
