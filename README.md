# przydancontent

Tools for making beat-synced "hard edits" for PRZYDAN's songs. See the marketing guide for the strategy.

Pipeline (prototype):

1. `tool/scrape_tags.mjs` – pull top TikTok posts for hashtags (views, saves, sounds) to see what footage is trending.
2. `tool/tiktok_download.py` – download source clips (scenepacks / clips-for-edits posts).
3. `tool/content_boxes.py` – find each clip's footage area (drops static captions and borders).
4. `tool/index_shots.py` – split clips into shots, score motion and brightness, save thumbnails.
5. `tool/clip_embed.py` + `tool/clip_search.py` – CLIP index; search shots by words ("batmobile through fire").
6. `tool/song_energy.py`, `tool/align_lyrics.py` – drops, beat grid, lyric timings for a song.
7. `tool/render_edit.py` – render a 1080x1920 edit from a timeline JSON (cuts, punch/shake, flashes, text, audio).

Example timeline: `edits/work_holygrail.json` (Work x Batman). Its source and audio paths point at the session scratch space; point them at your own copies to re-render.
