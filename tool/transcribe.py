"""Word timestamps for a song with faster-whisper (feeds lyric_words.py).

Usage: python tool/transcribe.py songs/work.mp3 songs/work_whisper_words.json [model]
Rap vocals trip the model up, so always align its output to the real lyrics with lyric_words.py.
"""
import json
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel

song, out = sys.argv[1], sys.argv[2]
model = WhisperModel(sys.argv[3] if len(sys.argv) > 3 else "small.en", device="cpu", compute_type="int8")
# decode with ffmpeg so any format works and PyAV version quirks don't matter
pcm = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", song, "-ar", "16000", "-ac", "1", "-f", "f32le", "-"],
                     capture_output=True).stdout
segments, _ = model.transcribe(np.frombuffer(pcm, np.float32), word_timestamps=True)
data = [{"start": s.start, "end": s.end, "text": s.text,
         "words": [{"w": w.word, "s": w.start, "e": w.end} for w in s.words]} for s in segments]
json.dump(data, open(out, "w"))
print(f"wrote {out}: {sum(len(s['words']) for s in data)} words")
