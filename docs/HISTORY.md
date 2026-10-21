# Project history and decisions

Everything found, decided and built so far (as of 2026-10-21), so a new session can pick up without the artist re-explaining. Newest decisions win where they conflict with older ones.

## The goal

Promote **PRZYDAN** (Instagram @przydantherapper) through the TikTok "fan page" strategy: themed edit pages that post fast, beat-synced "hard edits" of his songs over footage people already love (films, characters, memes), so the song spreads before people know the artist. The artist wants this **automated**: a tool that finds what is trending, gets footage, and cuts edits by itself.

## The artist

- Spotify: [PRZYDAN](https://open.spotify.com/artist/1IqPko6VZxrgLCW4avKX5o), 8 monthly listeners on 2026-10-21. Instagram @przydantherapper (needs a login to read). No other web presence found.
- Released catalog: album *Inauguration* (2025-09-09; Alchemist-type beats, J. Cole influence, some trap) plus singles "still tapped in" (2025-07-24) and "Hey Alright" (2025-03-24). Self-produced ("PRZYDAN produced it").
- **Current direction: lead with the unreleased music.** New songs are rage / underground (UG): Ken Carson, Yeat, Slayr, Prettifun lane, little or no sampling. Inauguration gets promoted later, for a different audience. Hype unreleased songs with snippets before release.

## Decisions and preferences (from the artist)

| Topic | Decision |
| --- | --- |
| Build vs buy | Build our own tool. Will not pay Virlo ($49/month) or similar; do the research ourselves. |
| Edit style | **Fast hard edits** that fit rage/UG songs: a cut on every beat after the drop. The slow "calm footage vs hard beat" idea was rejected for Work. |
| Hardest part | Finding footage, not editing. Use movies, current characters, memes. First pick: **Batman**. |
| Lyrics on screen | Yes, word by word. **Brat style** (Charli XCX brat typography: narrow, lowercase, slightly blurred), **white, no green, no blocks/boxes**. |
| Public repo | Fine with the repo being public, including the unreleased song and lyrics. |
| Where it runs | YouTube blocks cloud servers, so the pipeline runs on the artist's Windows PC with Claude Code. Fine with files living locally. |
| Explaining | Doesn't want to re-explain anything: keep this file current. |

## Research findings

**Reference edits the artist sent** (stats 2026-10-21; cuts per second measured from the downloaded videos):

| Video | Followers | Plays | Footage | Text | Cuts/s |
| --- | --- | --- | --- | --- | --- |
| [907_fitzy "prod by me"](https://www.tiktok.com/@907_fitzy/video/7541870136555277582) | 1.9K | 2.5M | LEGO Batman (2008 game) cutscenes | none | 0.25 |
| [bnyxlounge](https://www.tiktok.com/@bnyxlounge/video/7610496821173013773) | 11.1K | 581K | 90s VHS nature documentary | "how it feels to hear that BNYX tag" | 0.59 |
| [yeatupdates](https://www.tiktok.com/@yeatupdates/video/7661404896436014350) | 53.3K | 417K | Yeat live: fire, lasers, crowd | "back" | 2.44 |
| [andyindiemusic](https://www.tiktok.com/@andyindiemusic/video/7646915441637526806) | 421 | 255K | ad for LyricTune (lyric-video tool) | tutorial | 0.17 |
| [druxy59 Donnie Darko](https://www.tiktok.com/@druxy59/video/7676201389130829086) | 2.0K | 155K | Donnie Darko scenes, lyrics matched to scenes | small white subtitles | 0.24 |
| [907_fitzy GTA IV](https://www.tiktok.com/@907_fitzy/video/7541198991808122125) | 1.9K | 21K | GTA IV under an FL Studio screen | none | 0.09 |
| [have_been_gavin Soulja Boy](https://www.tiktok.com/@have_been_gavin/video/7508936983226387755) | 14.7K | 960 | old Soulja Boy clips | none | 0.65 |
| [907_fitzy Y2K](https://www.tiktok.com/@907_fitzy/video/7626529602990509325) | 1.9K | 867 | 2000s Skechers ad | none | 0.35 |
| [have_been_gavin "Recess"](https://www.tiktok.com/@have_been_gavin/video/7632429617546120461) | 14.7K | 583 | Subway Surfers | none | 0.40 |

Lessons: follower count barely matters; each hit has one recognizable subject and one clear idea; footage is nostalgic or iconic and matched to the song; the flops used generic filler with no angle.

**Batman edits on TikTok** (772 videos from #batmanedit, #thebatman, #darkknight, #legobatman, #batmanarkham, #rageedit; top ~150 per tag):

| Source | Edits | Last 90 days | Median plays |
| --- | --- | --- | --- |
| Animated series (BTAS, Beyond) | 17 | 12 | 425K |
| The Batman (2022, Pattinson) | 121 | 58 | 209K |
| Dark Knight trilogy | 168 | 120 | 97K |
| Arkham games | 134 | 115 | 20K |
| LEGO Batman | 124 | 93 | 4K |

The fast hits (e.g. [Batman x RIOT](https://www.tiktok.com/@greenlightediting/video/7665768083927207198), 2.7M; [czeditzxv](https://www.tiktok.com/@czeditzxv/video/7686969531440418062), 4.9M) are **"every Batman" montages**: about 60 shots in 20 s, a different Batman version almost every beat, white flash frames between hits. #rageedit itself is mostly anime anger edits (Gon, Guts/Berserk, Hulk, Naoya).

**Footage supply:** editors share "scenepacks" (pre-cut 4K/60fps clips per character, often with slow-motion and colour-corrected versions) on YouTube and MEGA, and "clips for edits" posts on TikTok.

**Tools looked at:** content.ready (lyric-video SaaS, $10 to $100/month), LyricTune (similar), Virlo (trend research, rejected on price), Jev by TypeSafe (cheap typed-judgment model via OpenRouter: `POST https://openrouter.ai/api/alpha/decisions`, model `~typesafe/jev-latest`, `questions` of type choice/score; see github.com/socai-io/jev-social `src/decision-provider.js`), jev-social (browser research tool; not used).

## Download constraints (learned the hard way)

- YouTube blocks cloud servers ("Sign in to confirm you're not a bot", 403) for every yt-dlp client. Cookies are unreliable there and PO-token/proxy tricks are off the table. **From a home connection yt-dlp works**, hence the local setup.
- TikTok works from anywhere through the public page data (`tool/tiktok_download.py`); yt-dlp's TikTok extractor failed from the cloud.
- Dailymotion only gave 288p. cobalt.tools dropped YouTube and requires a human check. Paid Apify YouTube actors exist (a few dollars for 45 min of video) but were not chosen.

## Song: Work (unreleased)

Files: `songs/work.mp3`, `songs/work_lyrics.txt` (typed by the artist), `songs/work_whisper_words.json`, `songs/work_timed_lines.json`.

- 2:39, about 143.6 BPM (beat 0.418 s, bar 1.67 s). Filtered intro with no bass until the **drop at 0:34.27**; breakdown from **1:51**, back in at **1:56.55** right after "PRZYDAN made it, it's my holy grail"; beat cuts out at 2:24.0.
- Snippets:

| Snippet | Time | Idea |
| --- | --- | --- |
| Holy grail drop (main) | 1:50.6 to 2:10.3 | Name said in the breakdown, then the drop. Done with Batman. |
| Intro drop | 0:26 to 0:42 | Build cut per bar, speeding up, then the drop at 0:34.3 |
| Move your body | 0:34.3 to 0:51.3 | Starts on the drop: wall-to-wall montage |
| Serf shit | 1:04.9 to 1:15.5 | "serf shit / feudal shit / not a slave": Berserk (Guts) or medieval battles |
| Surveillance state | 1:15.5 to 1:29 | "taxes going inside of a war", "surveillance state": The Dark Knight sonar machine, Bane |

## What's built

See README.md for commands. Key pieces:

- `tool/render_edit.py`: renders a timeline JSON (cuts, punch/shake, flashes, brat lyrics, audio). Fonts auto-detected (Arial on Windows).
- `tool/auto_assemble.py`: writes timelines automatically from `edits/*.auto.json` (beat grid, drop detection, lyric anchors, CLIP shot picking, character filter, brightness limits, no repeated shots) and renders N variations with `--render`.
- `tool/fetch_sources.py` + `edits/sources_batman.json`: downloads all 37 Batman sources (25 TikTok clips, 12 YouTube scenepacks; the YouTube ones only from home).
- `tool/index_shots.py`, `tool/clip_embed.py`, `tool/clip_search.py`: shot index and search by words. Indexing 25 clips takes about 5 minutes on CPU.
- `edits/work_holygrail.json`: the hand-made Work x Batman edit the artist approved (brat white lyrics). `edits/work_holygrail_batman.auto.json`: the auto version's config.

Known issues: the assembler drops captioned frames (CLIP "text on screen" filter) and off-character shots, but some sources contain glitch-effect frames the filters can't detect, so skim renders before posting; CLIP handles concrete queries ("batmobile through fire") much better than abstract ones ("chaos").

## Next steps

1. On the PC: fetch the YouTube scenepacks, rebuild the index (`index_shots.py`, `clip_embed.py`), re-run the auto-assembler for 4K-sourced Batman edits.
2. More snippets of Work: Intro drop and Move your body (Batman), Serf shit (Berserk), Surveillance state (Dark Knight).
3. Weekly automation: scrape trends, pick the rising character, fetch its scenepacks, index, assemble and render a batch into `out/` (Windows Task Scheduler or a Claude Code scheduled task).
4. Marketing guide (strategy, fan-page setup, snippet release plan, metrics) lives in a claude.ai doc: https://claude.ai/artifact/75jK6WH91d9HvZTHKZnHsi. Summary: 3 niche edit pages plus the artist page, every edit uses the song's own sound, about 6 edits a day, judge edits by "what song is this" comments and sound uses, pages say who runs them.
