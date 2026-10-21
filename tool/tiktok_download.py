"""Download TikTok videos straight from the public video page (no login).

Usage: python tool/tiktok_download.py OUT_DIR author/video/ID [...]
Saves OUT_DIR/<ID>.mp4. fetch_sources.py uses download() for TikTok URLs.
"""
import http.cookiejar
import json
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"


def download(url, path):
    """url: full TikTok video URL. The video link only works with the cookies the page set."""
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    html = op.open(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read().decode()
    data = json.loads(re.search(r'id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', html, re.S).group(1))
    video = data["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["video"]
    body = op.open(urllib.request.Request(video["playAddr"], headers={"User-Agent": UA,
                                                                      "Referer": "https://www.tiktok.com/"}), timeout=60).read()
    open(path, "wb").write(body)
    return len(body)


if __name__ == "__main__":
    for u in sys.argv[2:]:
        vid = u.split("/")[-1]
        try:
            print(vid, download("https://www.tiktok.com/@" + u, f"{sys.argv[1]}/{vid}.mp4"))
        except Exception as e:
            print(vid, "FAIL", e)
