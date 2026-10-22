"""Render a beat-synced vertical edit from a timeline JSON.

Usage: python tool/render_edit.py edits/work_holygrail.json out/work_holygrail.mp4

Timeline format (times in song seconds):
{
  "audio": "path/to/song.mp3",
  "start": 110.62, "end": 130.334,
  "sources": "dir with source clips", "boxes": "content boxes json",
  "slots": [{"at": 110.62, "clip": "<video id>", "from": 4.5, "fx": ["punch"]}, ...],
  "flashes": [116.611, ...],
  "texts": [{"text": "PRZYDAN", "from": 113.3, "to": 116.5}],
  "flash_color": "white",
  "dialogue": {"audio": "path/to/scene.m4a", "from": 41.2, "at": 22.5, "to": 34.27, "duck": 0.3, "gain": 1.8},
  "fade_out": 1.0,
  "end_card": {"from": 131.0, "text": "coming soon", "sub": "przydan - work", "color": "0x39ff5a"}
}
"dialogue" (optional, one or a list) plays a film scene's own audio from "from" (seconds in that file) over song time
"at".."to", with the song turned down to "duck" until "to" (usually the drop).
"fade_out" (optional) fades picture and sound out over the last N seconds instead of a hard stop.
"end_card" (optional) cuts to black at "from" and shows glitching text (flicker, jitter, RGB split, noise
bars) until the end; with it, "fade_out" only fades the sound.
Each slot runs until the next slot's "at" (the last one until "end").
A slot's own "box" overrides the clip's box (e.g. to follow a speaker in a dialogue scene).
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
             "-vf", segment_filter(pixel_box(s.get("box") or boxes.get(s["clip"]), src), s.get("fx", []), dur), "-frames:v", str(frames),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", part])
        parts.append(part)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p.replace(os.sep, '/')}'\n" for p in parts))
    joined = os.path.join(tmp, "joined.mp4")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])

    t0 = tl["start"]
    post = []
    fc = tl.get("flash_color", "white")
    for t in tl.get("flashes", []):
        a = t - t0
        post.append(f"drawbox=x=0:y=0:w=iw:h=ih:color={fc}@0.85:t=fill:enable='between(t,{a:.3f},{a + 0.067:.3f})'")
        post.append(f"drawbox=x=0:y=0:w=iw:h=ih:color={fc}@0.35:t=fill:enable='between(t,{a + 0.067:.3f},{a + 0.13:.3f})'")
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
    card = tl.get("end_card")
    if card:
        a = card["from"] - t0
        on = f"enable='between(t,{a:.3f},{dur:.3f})'"
        c = card.get("color", "0x39ff5a")
        post.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:{on}")
        post.append(f"noise=alls=22:allf=t+u:{on}")
        # glitch bars: rows of block characters (drawbox only places itself once, drawtext moves every frame)
        for k in range(3):
            texts.append(f"drawtext=fontfile={BRAT_FONT}:text='{'█' * 60}':fontsize={18 + 22 * k}:fontcolor={c}"
                         f":alpha='if(lt(random(0),0.45),0,0.4)':x='-random(1)*200':y='h*random(2)':{on}")
        flick = "alpha='if(lt(random(0),0.2),0.1,1)'"
        jit = "if(lt(random(1),0.4),(random(2)-0.5)*180,0)"
        jy = "(random(3)-0.5)*6"
        big = card.get("size", 175)
        txt = card["text"].lower().replace("'", "’")
        # RGB split: green and magenta copies jitter on their own around the white text
        for col, off in ((c, -20), ("0xff3df0", 20), (fg, 0)):
            texts.append(f"drawtext=fontfile={BRAT_FONT}:text='{txt}':fontsize={big}:fontcolor={col}:{flick}"
                         f":x='(w-text_w)/2+{off}+{jit}':y='(h-text_h)/2+{jy}':{on}")
        if card.get("sub"):
            texts.append(f"drawtext=fontfile={BRAT_FONT}:text='{card['sub'].lower()}':fontsize={big * 0.42:.0f}"
                         f":fontcolor={fg}:{flick}:x='(w-text_w)/2+{jit}/3':y=(h+text_h)/2+{big * 0.6:.0f}:{on}")
    graph = f"[0:v]{','.join(post) or 'null'}[base]"
    if texts:
        # draw on a wider transparent layer, squeeze it to width (narrow brat letterforms), soften slightly
        graph += (f";color=c=black@0.0:s={int(W / BRAT_SQUEEZE)}x{H}:r={FPS}:d={dur:.3f},format=rgba,"
                  f"{','.join(texts)},gblur=sigma=1.4,scale={W}:{H}[txt];[base][txt]overlay=0:0[v]")
    else:
        graph += ";[base]null[v]"
    inputs = ["-i", joined, "-ss", str(t0), "-t", f"{dur:.3f}", "-i", rel(tl["audio"])]
    dls = tl.get("dialogue") or []
    dls = [dls] if isinstance(dls, dict) else dls
    if dls:
        # the song stays turned down until the last scene ends
        last = max(d["to"] for d in dls) - t0
        graph += f";[1:a]volume='if(lt(t,{last:.3f}),{dls[0].get('duck', 0.3)},1)':eval=frame[song]"
        for k, dl in enumerate(dls):
            a, b = dl["at"] - t0, dl["to"] - t0
            inputs += ["-ss", str(dl["from"]), "-t", f"{b - a:.3f}", "-i", rel(dl["audio"])]
            graph += (f";[{k + 2}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={dl.get('gain', 1.0)},"
                      f"afade=t=in:d=0.03,afade=t=out:st={b - a - 0.08:.3f}:d=0.08,adelay={a * 1000:.0f}:all=1[dia{k}]")
        graph += (f";[song]{''.join(f'[dia{k}]' for k in range(len(dls)))}amix=inputs={len(dls) + 1}:normalize=0"
                  f":duration=first,alimiter=limit=0.95:level=0[a]")
    else:
        graph += ";[1:a]anull[a]"
    vout, aout = "[v]", "[a]"
    if tl.get("fade_out"):
        f = tl["fade_out"]
        graph += f";[a]afade=t=out:st={dur - f:.3f}:d={f}[af]"
        aout = "[af]"
        if not card:
            graph += f";[v]fade=t=out:st={dur - f:.3f}:d={f}[vf]"
            vout = "[vf]"
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", *inputs,
         "-filter_complex", graph, "-map", vout, "-map", aout, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path])
    print("wrote", out_path)


if __name__ == "__main__":
    main(*sys.argv[1:3])
