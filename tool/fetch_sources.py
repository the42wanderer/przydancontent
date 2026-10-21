"""Download every clip in a sources manifest (YouTube, TikTok, anything yt-dlp supports).

Usage: python tool/fetch_sources.py edits/sources_batman.json [data/clips]

Manifest: [{"id": "...", "url": "...", "note": "..."}]. Files are saved as <id>.mp4, video only,
at most 1080p; clips already on disk are skipped. Run it from a home connection: YouTube blocks
cloud servers.
"""
import json
import os
import sys

from yt_dlp import YoutubeDL

sys.path.insert(0, os.path.dirname(__file__))
from tiktok_download import download as tiktok_download  # noqa: E402

manifest, out_dir = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "data/clips"
os.makedirs(out_dir, exist_ok=True)
failed = []
for item in json.load(open(manifest)):
    target = os.path.join(out_dir, item["id"] + ".mp4")
    if os.path.exists(target):
        continue
    opts = {
        "format": "bv*[height<=1080][vcodec^=avc1]/bv*[height<=1080]/b[height<=1080]/b",
        "outtmpl": os.path.join(out_dir, item["id"] + ".%(ext)s"),
        "postprocessors": [{"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"}],
        "quiet": True,
        "no_warnings": True,
        "sleep_interval": 3,
        "socket_timeout": 60,
    }
    try:
        if "tiktok.com" in item["url"]:
            # the page-data route works where yt-dlp's TikTok extractor gets blocked
            try:
                tiktok_download(item["url"], target)
            except Exception:
                with YoutubeDL(opts) as ydl:
                    ydl.download([item["url"]])
        else:
            with YoutubeDL(opts) as ydl:
                ydl.download([item["url"]])
        print("ok  ", item["id"], item.get("note", ""))
    except Exception as e:
        failed.append(item["id"])
        print("FAIL", item["id"], str(e).splitlines()[0][:160])
print(f"done, {len(failed)} failed" + (f": {failed}" if failed else ""))
