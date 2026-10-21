# przydancontent

Edit pipeline for PRZYDAN (rage/underground rapper, Ken Carson / Yeat lane). Goal: automatically turn a song snippet plus a trending character or film into fast, beat-synced vertical "hard edits" for TikTok fan pages.

- Read README.md for setup and the pipeline table. Scripts live in `tool/`, edit definitions in `edits/`.
- `songs/` (audio, lyrics, whisper word timings), `data/` (clips, index) and `out/` (renders) are git-ignored. The GitHub repo is public: keep unreleased audio and lyrics out of it.
- Edits are timeline JSON files rendered by `tool/render_edit.py`. Crop boxes are fractions of the frame, so they survive re-downloads at a different resolution.
- House style: cut on every beat after a drop (about 0.42 s at 144 BPM), white flashes on downbeats, punch/shake on the drop and lyric hits, lyrics as brat-style text (`"text_style": "brat"`, white, no blocks).
- Footage rules: one recognizable character per edit, many versions of it in fast edits; skip shots with burned-in captions, watermarks or near-black frames. Check rendered frames before calling an edit done.
- Never commit unreleased audio, cookies or API tokens.

Next to build: an auto-assembler that writes the timeline itself (lyric-matched shots on key words, high-motion shots on the drop, no repeats), renders 3 to 5 variations, and a scheduled weekly run.
