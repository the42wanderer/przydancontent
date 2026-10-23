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

## Run log

- 2026-10-22, on the artist's Mac: all 12 YouTube scenepacks downloaded fine from home (36 of 37 sources; TikTok 7411719521494404398 fails but is excluded anyway). Index rebuilt: 2,524 shots. Auto Batman edits re-rendered into `out/`; v2 was the cleanest. `RajlSpO16a0` (Evolution of the Bat-signal) is excluded because it mixes 4:3 and widescreen and its 1940s title card leaks text into the crop.
- Mac setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt imageio-ffmpeg`. Homebrew's ffmpeg has no `drawtext` (no libfreetype), so link imageio-ffmpeg's binary as `.venv/bin/ffmpeg` and run with `PATH=$PWD/.venv/bin:$PATH`.

## Edit 2: Work x John Stewart (Lanterns), "the ring says you are"

Decided 2026-10-22. HBO's *Lanterns* is airing and Aaron Pierre's John Stewart is getting buzz. The artist asked for a dialogue scene that turns into an edit.

- **Concept:** about 8 s of the show where Hal tells John "you're just a substitute teacher, Junior. You're not ready to get up in front of the class until the ring says you are." It plays over Work's filtered intro and ends on John's silent stare. The drop (0:34.27) is the payoff: every John Stewart with the ring (*Lanterns* plus the *Justice League* / *Justice League Unlimited* and other animated versions), cut on every beat, with **green** flashes. Lyrics stay white brat. The scene is song 26.1–34.27, the montage runs to 48.5 (ends after "too cocky"), about 22 s total.
- Config `edits/work_ring_johnstewart.auto.json`, sources `edits/sources_lanterns.json`. The scene comes from DC's official "Best of Lanterns" compilation (`-jC32AIIn14`, 194.45–202.6 s). Its audio is in `data/dialogue/` (yt-dlp audio-only), with whisper transcripts of the trailers alongside.
- New pipeline features: `dialogue` in auto configs and timelines (scene audio mixed in, song turned down to 0.3 until the drop, +5 dB dialogue gain, limiter), per-shot crop `box` (follows the speaker, since Hal is left of frame and John right), hand-written `subs` (whisper misheard the payoff line), `flash_color`.
- Lessons: montage sources must be **character-only** compilations. Trailers and two-hander scenepacks brought in Hal, Guy Gardner and other cast, because CLIP can't tell live-action John from Hal. `max_per_clip` 6 is fine for long compilations. v3 was the best render (ends on Pierre raising the ring).
- **Revised (artist feedback):** use the **second chorus**, not the intro. Over the quiet intro the song seemed to switch on out of nowhere. The scene now plays over the end of the verse and the breakdown (song 108.4–116.55), the drop is 1:56.55, same "move your body" chorus, ending at 130.55 after "too cocky". General rule: put a dialogue intro over a part of the song that's already playing, not over silence.
- **Bird construct (artist idea):** John's green bird from *Lanterns* episode 2 (made without his ring; clip `9a1NskAZS0w`) is pinned to the lyrics. The bird flying across the sky on "bird" (held 3 beats), then John grinning with the bird on his shoulder on "cocky" as the last shot. Anchors can now name an exact shot (`{"clip", "from", "beats"}`), and `end_at` / `lyrics_from` set where the edit ends and where lyrics start.
- **Ending (artist feedback):** stopping right after the bird felt abrupt. Now John's grin holds for about 1.1 s, then a 1.6 s **glitch "coming soon" card** (black screen, "przydan - work" under it, green/magenta colour split, sideways jitter, flicker, moving green bars, grain) while the song fades out (`end_card`, `fade_out`). Use this ending on every snippet of an unreleased song.
- Unavailable: "Best of Green Lantern (John Stewart)" by DC (`59b3m1u1zds`) and the Justice League S2 compilation didn't download; teaser 2 audio gave a 403.

## Edit 3: Work x "we are being watched" (creators on surveillance)

Decided 2026-10-22. The artist wanted a completely different direction. The "surveillance state" verse is about Flock cameras and Palantir, so the edit opens with popular creators saying it, then the verse answers.

- **Trend check:** TikTok now hides hashtag feeds and song charts from logged-out visitors (`tool/scrape_tags.mjs` gets empty replies, and so does a real browser). The public Creative Center showed Halloween horror on top (#tiktokscaryhorrorcontest, 312M views in a week). An analog-horror "CAM 04" idea using the artist's own night footage is in the marketing guide, waiting on footage.
- **The edit** (`edits/work_surveillance_watched.auto.json`, sources `edits/sources_surveillance.json`): Christophe ("all the cameras"), Anthony Sistilli ("tracking everyone"), Alex Karp ("every single thing we do is monitored") and penguinz0 ("you will own nothing and be happy"), 10.45 s back to back over a 15% song. The verse lands at 1:15.45 and runs to 1:29, then a red glitch end card. The montage uses the same creators' videos (Flock cameras, tracking maps, police at the door on "pop up", smashed cameras on "burn"). v3 is the best.
- **Pipeline:** `dialogue` can be a list of parts (each with its own audio, crops, subs, `gain` and a `label` name tag); `duck` sets the song level under them; lyrics stop at the end card.
- **Lessons:** exclude reposted-TikTok compilations and news clips with banners (their captions leak in), raise `caption_cut_percent` to about 45 for commentary footage, level each voice on its own (YouTube voices ranged -17 to -23 dB), and skip shots with real campaign signs. Use whole-file audio downloads; `--download-sections` streams at real time.

## Edit 4: Work x Sri Lanka's 430 chase ("has it gone?")

Decided 2026-10-23, the day after the match. Sri Lanka chased England's 429/4 in Rawalpindi (Brook 202), their highest ODI chase and the second-highest ever, won by Liyanage's six off the second-last ball. The artist is Sri Lankan (Colombo/Melbourne), so this also aims at a home audience.

- **Research:** Cricinfo ball-by-ball and report (its JSON API is blocked; the report has the narrative). Reddit was blocked for both browser and fetch, so it isn't used. Viral sports edits on YouTube Shorts (Kohli 5.6M, Ja Morant 2.4M, Stokes 1.4M) cut only 0.2-0.7 times a second, follow one hero and tell a story in on-screen text ("until this man came").
- **The edit** (`edits/work_holygrail_slchase.auto.json`, source: PCB full highlights `DUb_zUiEiF4`): story parts with the real commentary (Brook's 200; "that's two in two, is this the twist?"; the dressing room in suspense; "hit hard, hit high, has it gone?"), then the holy grail drop on "It has". After it, shots held for 2 beats, from the celebration (`celebrate.mp4`) and Rathnayake's hundred (`ton.mp4`) only, plus the replay of the six on "bird" and an England player on "cocky". Gold flashes, gold/maroon end card. v1 is the best.
- **Pipeline:** `beats_per_cut` (montage pace after the drop), `avoid` queries (drop shots like the other team or umpires), shot `offset` for cutaways inside a dialogue part, and the end card's `color2`. For sport, index only the shots you want (the chase, the celebration) rather than the whole match.

## Next steps

1. On the PC: fetch the YouTube scenepacks, rebuild the index (`index_shots.py`, `clip_embed.py`), re-run the auto-assembler for 4K-sourced Batman edits.
2. More snippets of Work: Intro drop and Move your body (Batman), Serf shit (Berserk), Surveillance state (Dark Knight).
3. Weekly automation: scrape trends, pick the rising character, fetch its scenepacks, index, assemble and render a batch into `out/` (Windows Task Scheduler or a Claude Code scheduled task).
4. Marketing guide (strategy, fan-page setup, snippet release plan, metrics) lives in a claude.ai doc: https://claude.ai/artifact/75jK6WH91d9HvZTHKZnHsi. Summary: 3 niche edit pages plus the artist page, every edit uses the song's own sound, about 6 edits a day, judge edits by "what song is this" comments and sound uses, pages say who runs them.
