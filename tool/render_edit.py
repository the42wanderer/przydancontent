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


def find_font(*candidates):
    for c in candidates:
        if os.path.exists(c):
            # ffmpeg filter options use ":" as a separator, so a Windows drive letter needs escaping
            return c.replace("\\", "/").replace(":", r"\:")
    sys.exit(f"none of these fonts exist: {candidates}")


FONT = find_font("C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf")
# "text_style": "brat" - Charli XCX brat look: Arial-metric font squeezed narrow, lowercase, slight blur.
# "text_bg" / "text_fg" set the block and letter colours (brat cover is 0x8ACE00 on black).
BRAT_FONT = find_font("C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                      "/System/Library/Fonts/Supplemental/Arial.ttf")
BRAT_SQUEEZE = 0.8
GRADE = "eq=contrast=1.1:brightness=0.03:saturation=1.15:gamma=1.2,colorbalance=rs=0.04:bs=0.05:rh=0.05:bh=-0.03"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit(p.stderr[-2000:])


def frame_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    w, h = out.strip().split(",")[:2]
    return int(w), int(h)


def pixel_box(box, src):
    """Boxes are [x0, y0, x1, y1] as fractions of the frame (or pixels); a missing box means the whole frame."""
    w, h = frame_size(src)
    if not box:
        return [0, 0, w, h]
    if max(box) <= 1:
        box = [box[0] * w, box[1] * h, box[2] * w, box[3] * h]
    x0, y0, x1, y1 = (int(v) // 2 * 2 for v in box)
    return [x0, y0, x1, y1]


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
             "-vf", segment_filter(pixel_box(boxes.get(s["clip"]), src), s.get("fx", []), dur), "-frames:v", str(frames),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", part])
        parts.append(part)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p.replace(os.sep, '/')}'\n" for p in parts))
    joined = os.path.join(tmp, "joined.mp4")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])

    t0 = tl["start"]
    post = []
    for t in tl.get("flashes", []):
        a = t - t0
        post.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:t=fill:enable='between(t,{a:.3f},{a + 0.067:.3f})'")
        post.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.35:t=fill:enable='between(t,{a + 0.067:.3f},{a + 0.13:.3f})'")
    dur = tl["end"] - t0
    brat = tl.get("text_style") == "brat"
    bg, fg = tl.get("text_bg"), tl.get("text_fg", "white")
    texts = []
    for tx in tl.get("texts", []):
        a, b = tx["from"] - t0, tx["to"] - t0
        on = f"enable='between(t,{a:.3f},{b:.3f})'"
        # a straight quote cannot be escaped inside ffmpeg's quoted option, so use a typographic one
        txt = tx["text"].replace(":", r"\:").replace("'", "’")
        y = tx.get("y", "(h-text_h)/2")
        if not brat:
            post.append(f"drawtext=fontfile={FONT}:text='{txt}':fontsize={tx.get('size', 150)}:fontcolor=white"
                        f":borderw=6:bordercolor=black@0.6:x=(w-text_w)/2:y={y}:{on}")
        elif tx.get("card") and bg:
            # brat cover: full-screen colour block, lowercase text in the middle
            texts.append(f"drawbox=x=0:y=0:w=iw:h=ih:color={bg}:t=fill:replace=1:{on}")
            texts.append(f"drawtext=fontfile={BRAT_FONT}:text='{txt.lower()}':fontsize={tx.get('size', 150) * 1.3:.0f}"
                         f":fontcolor={fg}:x=(w-text_w)/2:y=(h-text_h)/2:{on}")
        else:
            # no text_bg: bare letters with a soft shadow so they stay readable on bright footage
            look = f"box=1:boxcolor={bg}:boxborderw=22" if bg else "shadowcolor=black@0.55:shadowx=0:shadowy=5"
            texts.append(f"drawtext=fontfile={BRAT_FONT}:text='{txt.lower()}':fontsize={tx.get('size', 150)}"
                         f":fontcolor={fg}:{look}:x=(w-text_w)/2:y={y}:{on}")
    graph = f"[0:v]{','.join(post) or 'null'}[base]"
    if texts:
        # draw on a wider transparent layer, squeeze it to width (narrow brat letterforms), soften slightly
        graph += (f";color=c=black@0.0:s={int(W / BRAT_SQUEEZE)}x{H}:r={FPS}:d={dur:.3f},format=rgba,"
                  f"{','.join(texts)},gblur=sigma=1.4,scale={W}:{H}[txt];[base][txt]overlay=0:0[v]")
    else:
        graph += ";[base]null[v]"
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", joined, "-ss", str(t0), "-t", f"{dur:.3f}", "-i", rel(tl["audio"]),
         "-filter_complex", graph, "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path])
    print("wrote", out_path)


if __name__ == "__main__":
    main(*sys.argv[1:3])
