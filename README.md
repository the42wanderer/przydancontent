# przydancontent

Tools for making beat-synced "hard edits" for PRZYDAN's songs: find what's trending, pull footage, index it, cut it on the beat, render 1080x1920 MP4s.

Run it on your own computer: YouTube blocks cloud servers, so YouTube scenepacks only download from a home connection.

## Setup (Windows, once)

```powershell
winget install Python.Python.3.12 Gyan.FFmpeg OpenJS.NodeJS.LTS Git.Git
# open a new terminal so the new tools are on PATH
git clone https://github.com/the42wanderer/przydancontent
cd przydancontent
git checkout claude/beautiful-hamilton-i7xc4q
py -m pip install -r requirements.txt
npm install
npx playwright install chromium
```

Songs live in `songs/`: `work.mp3`, `work_lyrics.txt` (typed lyrics), `work_whisper_words.json` (word timings), `work_timed_lines.json` (line start times). Downloaded clips (`data/`) and renders (`out/`) are git-ignored.

## Work x Batman

```powershell
py tool/fetch_sources.py edits/sources_batman.json data/clips      # clips (YouTube ones need a home connection)
py tool/render_edit.py edits/work_holygrail.json out/work_holygrail.mp4   # the hand-cut edit
py tool/index_shots.py data/clips data/index                       # shot index (a few minutes)
py tool/clip_embed.py data/index
py tool/auto_assemble.py edits/work_holygrail_batman.auto.json --render   # 3 automatic variations
```

Background, decisions and next steps: `docs/HISTORY.md`.

## Pipeline

| Step | Script | What it does |
| --- | --- | --- |
| Trends | `node tool/scrape_tags.mjs out.json batmanedit thebatman` | Top TikTok posts per hashtag: plays, saves, sounds, captions |
| Footage | `tool/fetch_sources.py MANIFEST data/clips` | Downloads every clip in a manifest (YouTube, TikTok) as `<id>.mp4` |
| Crop | `tool/content_boxes.py data/clips edits/boxes_X.json` | Finds each clip's footage area, dropping burned-in captions and borders |
| Index | `tool/index_shots.py data/clips data/index` | Splits clips into shots; motion, brightness, thumbnails |
| Search | `tool/clip_embed.py data/index`, then `tool/clip_search.py data/index queries.json` | CLIP index; find shots by words, e.g. "batmobile through fire" |
| Song | `tool/song_energy.py song.mp3` | Tempo, energy per second, drops, best 10/15/20 s windows |
| Lyrics | `tool/lyric_words.py whisper.json lyrics.txt START END` | Word timings from the real lyrics aligned to whisper output |
| Transcribe | `tool/transcribe.py songs/x.mp3 songs/x_whisper_words.json` | Word timestamps for a new song (align with `lyric_words.py`) |
| Render | `tool/render_edit.py TIMELINE.json OUT.mp4` | Cuts, punch/shake, flashes, brat-style lyrics, audio |
| Auto edit | `tool/auto_assemble.py edits/X.auto.json --render` | Beat grid + drop, lyric anchors, picks shots from the index, writes and renders N variations |

Timeline format is documented at the top of `tool/render_edit.py`; `edits/work_holygrail.json` is a full example.
