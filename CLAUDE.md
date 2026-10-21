# przydancontent

Edit pipeline for PRZYDAN (rage/underground rapper, Ken Carson / Yeat lane). Goal: automatically turn a song snippet plus a trending character or film into fast, beat-synced vertical "hard edits" for TikTok fan pages.

- **Read docs/HISTORY.md first**: the artist, every decision and preference so far, research findings, the song analysis, and next steps. Keep it updated when something new is decided.
- Read README.md for setup and the pipeline table. Scripts live in `tool/`, edit definitions in `edits/`.
- `songs/` holds the audio, typed lyrics, whisper word timings and timed lyric lines (committed on purpose; the artist is fine with them being public). `data/` (clips, index) and `out/` (renders) are git-ignored.
- Edits are timeline JSON files rendered by `tool/render_edit.py`. Crop boxes are fractions of the frame, so they survive re-downloads at a different resolution.
- House style: cut on every beat after a drop (about 0.42 s at 144 BPM), white flashes on downbeats, punch/shake on the drop and lyric hits, lyrics as brat-style text (`"text_style": "brat"`, white, no blocks).
- Footage rules: one recognizable character per edit, many versions of it in fast edits; skip shots with burned-in captions, watermarks or near-black frames. Check rendered frames before calling an edit done.
- Never commit cookies or API tokens.

To make a new edit: write an `edits/<song>_<snippet>_<character>.auto.json` config (copy `edits/work_holygrail_batman.auto.json`), make sure the sources are fetched and indexed, then `py tool/auto_assemble.py CONFIG --render`. Skim the renders before calling them done.

Next to build: the weekly scheduled run (see docs/HISTORY.md, Next steps).
