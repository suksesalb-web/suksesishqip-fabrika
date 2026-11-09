# @suksesishqip — content guide

This file is the brief every daily run follows. Change it to change what the page posts.

## The page
- Albanian-language Instagram page about discipline, mindset, lessons from great thinkers and successful people, and honest side-hustle ideas.
- Voice: direct, warm, grounded. Like a smart older friend, not a guru. Short sentences.
- Standard Albanian (gjuha standarde) with correct ë and ç everywhere. No English words where an Albanian one exists.

## Daily mix (5 posts)
| Slot (Tirana time) | Style | What |
|---|---|---|
| 09:00 | `statement` or `tweet` | One sharp morning idea on discipline or mindset |
| 12:00 | `reel` (12–30 s) | **AI or side hustle:** one concrete thing a person can do with AI tools or a skill, from Albania. 2–3 times a week as an animated Reel (see Animated Reels) |
| 15:00 | `quote` or `story` | Books & thinkers: a verified quote with the source named, or (2–3 times a week) a "mësime nga libri" carousel (see Book posts) |
| 18:00 | `reel` (12–25 s) | **Business or money:** a sharp money/business truth, or how a real person built something (mini-story). 2–3 times a week as a Stickman Reel (see Stickman Reels) |
| 22:00 | `tweet` | A reflective, personal-sounding thought people send to a friend. Family and home themes (parents, Sunday at home, family far away) work well here, a few times a week |

## Main focus
The page's core is **interesting side hustles, making money with AI, and how to start a business**. Discipline and mindset support it. Never post religious, gaming, K-pop, sport-gossip or political content.

## Tone: a bit clickbaity, never fake
- Hooks can tease and surprise: "Ky biznes s'kërkon asnjë lek kapital", "AI-ja që po zëvendëson një punë 800€ në muaj", "Pse askush s'ta thotë këtë për…".
- But every post must **deliver** on its hook with real, specific steps or facts. If the slides can't back up the cover, rewrite the cover.
- No promised earnings ("fito 1000€ në javë"), no "pa punë", no "pasivisht", no app/crypto schemes. Say what the work is, what tools it needs, and how someone gets their first client.
- AI side hustles must name real tools (ChatGPT, Claude, Canva, CapCut, ElevenLabs etc.) and be realistic for a beginner in Albania.

## Writing for reach (views, saves, sends)
- **Carousels are the engine.** They get saved and re-shown in feed. Each slide must make the reader want the next one: open a loop on the cover, pay it off at the end.
- **Cover hook = the whole game.** Specific beats vague: "Në 1914, Ford dyfishoi pagat" beats "Një histori frymëzuese". Use numbers, names, contrast, a surprising claim that's true.
- **Write to be sent.** The strongest signal for reaching non-followers is people sending a post in DMs. Ask: would someone send this to a friend with "kjo je ti" or "lexoje këtë"?
- **One idea per post.** If it needs two ideas, it's two posts.
- **The photo must say the same thing as the text.** A post about a factory shows a factory; a post about loneliness shows someone alone. If the photo could belong to any post, it's the wrong photo.
- **Albanian context wins.** Albanian names, places, prices in lek, realities of working from Albania. Global stories are fine, local relevance is the edge.

Rotate topics across the week: discipline, habits, money mindset, side hustles that work from Albania, stories of people who built something, Stoic ideas, book lessons. Check `data/topics_log.txt` and don't repeat a topic or quote used in the last 60 days.

## Trend input (read every run)
`data/trends/<today>.json` is written at 05:30–06:30 Tirana time by the Trend report action: the fastest-growing English short videos of the last 48 hours, ranked by views per hour. `by_search` holds the top 6 per search (read the AI, side-hustle and business searches first); `top` is the overall top 30.
- Use it to pick **themes and angles** that are hot right now: at least 2 of the 5 posts should build on a theme from the report when one fits the page.
- Look for the idea behind a hit ("looking rich makes you look poor", "discipline vs motivation"), then write our own post about it, in Albanian, with Albanian context.
- **Never copy** titles, scripts or wording, and never present someone else's video as ours.
- Ignore entries that are off-niche, clickbait without substance, religious or political, or unsuitable for the page.
- `data/instagram/<today>.json` (same action) shows what is working on Instagram itself: `outliers` = posts from watched niche pages (data/instagram_watchlist.txt) in the last 7 days that did far better than that page's usual; `formats` = how Reels, carousels and images perform; `hashtags_on_outliers`; and `own_posts` = reach, saves, shares and views of our own recent posts. Use the outliers for themes and hooks, and our own numbers to do more of what works for us (and less of what doesn't).
- **Albanian pages in the watchlist** (e.g. millionaire_albania) show what works with our own audience. When one of their posts is an outlier, weigh it above the foreign pages. Take the theme or the emotion, never their format, look or wording.
- We stay ourselves: practical business, AI and side hustles from Albania, honest and specific. No "millionaire lifestyle" tone, no reposted viral videos, no political figures.
- If today's file is missing, use the most recent one, or carry on without it.

## Quote bank
`data/quote_bank.json` holds quotes believed to be genuinely in the named book, with their Goodreads likes (popularity), topic tags, and a `banned` list of famous fake quotes. For quote posts:
- Prefer a quote from the bank whose tags match today's trend themes; among those, prefer higher `likes` and quotes not used in the last 60 days. After posting, set its `"used": "DATE"`.
- `"paraphrase": true` quotes are popular wordings of a translation: present them as "sipas Mark Aurelit" with the book name, not as an exact quotation.
- A new quote can be added to the bank only if you can name the book (and ideally the chapter/letter) it comes from; never use anything on the banned list.
- Instagram signal so far: short, sharp business lines (≤ 15 words) beat long quotes. Prefer short quotes, or cut to the strongest sentence.

## Book posts ("mësime nga libri")
- Format: `story` carousel. Cover: kicker "Mësime nga librat", title "N mësime nga \"<Book>\" …", subtitle with author and year. Then 4–6 lessons, one per slide, then the automatic save/follow slide.
- Books that fit the page: Rich Dad Poor Dad, The 48 Laws of Power (also as a weekly series "Ligji 1, 2, 3…"), Atomic Habits, The Psychology of Money, Think and Grow Rich, The Richest Man in Babylon, Can't Hurt Me, Meditations, The Almanack of Naval Ravikant, Deep Work.
- **Only ideas that are really in the book.** Write lessons in our own words, with Albanian examples (këste, qira, paga, dyqan). At most one short direct quote per post, clearly attributed. Never reproduce passages, chapter text or lists word for word.
- If you're not sure an idea or quote is in the book, leave it out. Many popular "book quotes" online are fake.
- Caption ends with the source line: 📖 "<Book>", <Author> (<year>). Mësimet janë përmbledhje me fjalët tona.
- Track book posts in topics_log ("book: <title>") and don't repeat a book within 30 days (a numbered series counts as one book continuing).

## Hard rules
- **No get-rich-quick claims.** No income promises, no "make €X from home", no specific investment advice, no crypto tips.
- **Quotes must be real and attributed correctly.** Only use a quote when you can name the work it comes from. Misattributed internet quotes are banned.
- **Facts must be true.** Dates, numbers and stories about real people get checked. When unsure, leave it out.
- **No real people's photos.** Photos come from Pixabay by search query only: places, objects, silhouettes, statues, nature.
- **Original wording.** Never copy captions or posts from other pages.

## Writing each post
- Hook in the first line. The first line is what stops the scroll.
- Captions: 2–5 short lines, a question or a call to action ("Ruaje", "Dërgoja dikujt që…"), then 3–5 hashtags, always including #suksesishqip.
- Story slides: cover = `kicker` + `title` + `subtitle`; each next slide = `title` (1–3 words) + `body` (max ~35 words). A final "Ruaje këtë postim" slide is added automatically.
- `photo_query` in English, concrete and moody: "man walking alone city night", "ancient statue dark", "desk laptop night lamp". Avoid faces in close-up.

## Queue file format (`queue/YYYY-MM-DD.json`)
```json
{
  "date": "2026-11-08",
  "posts": [
    {"id": "p1", "style": "statement", "time": "10:40", "photo_query": "...",
     "slides": [{"text": "...", "highlight": "..."}], "caption": "..."},
    {"id": "p2", "style": "story", "time": "15:20", "photo_query": "...",
     "slides": [{"kicker": "...", "title": "...", "subtitle": "..."}, {"title": "...", "body": "..."}],
     "caption": "..."},
    {"id": "p3", "style": "quote", "time": "20:10", "photo_query": "...",
     "slides": [{"quote": "...", "author": "...", "source": "..."}], "caption": "..."}
  ]
}
```
`tweet` posts use `"slides": [{"text": "..."}]`.

## Reels (`"style": "reel"`)
Three looks, all approved by the owner: **footage Reels** (real clips, a cut on every beat, zoom, whoosh), **animated Reels** (`"engine": "motion"`, see below) and **Stickman Reels** (`"engine": "stickman"`, see below). The slot table gives defaults, but you have freedom: pick whichever look serves the idea best (footage for stories, mindset and money truths; animation for tools, steps, numbers and comparisons), and vary within it (music mood, beat types, pacing) so the feed doesn't feel repetitive.
```json
{"id": "p2", "style": "reel", "time": "12:00",
 "video_query": "man driving car at night city lights",
 "voice": "gemini:Riko", "music": "mood:cinematic",
 "beats": [{"text": "HOOK", "video_query": "..."}, {"text": "...", "video_query": "..."},
           {"text": "...", "highlight": "PAYOFF", "video_query": "..."}],
 "caption": "..."}
```
- **Every beat gets its own footage** (`video_query` per beat, English, literal: what that sentence shows). The Reel cuts on every beat, beats longer than ~4 s get a second shot from the same search, every shot opens with a quick zoom punch and then slowly pushes in or pulls out, text slides in, and a whoosh marks each cut (a low hit when the gold payoff lands). The post-level `video_query` is the fallback for beats without one.
- Review **every** `frame-NN.jpg` (one per shot; `manifest.json` → `reel.shots` says which beat each belongs to). When re-rendering, lock the shots that passed with `"video_ids": [...]` (one id per shot, in order, from `reel.video_ids`; use `""` for a shot to re-pick) and change only the failing beat's `video_query`.
- **3–5 beats.** Beat 1 is the hook: max ~12 words, a surprising, specific claim that makes someone think of a person they know. Other beats: max ~18 words. The last beat lands the payoff in `highlight` (gold), max ~6 words.
- The voice is **Riko** (Gemini TTS, the owner's choice; Anila is only an automatic fallback). Riko reads every beat while it's on screen. For a more human delivery, a beat's `say` may include one light expression tag where it fits naturally, e.g. `<breath>` before a hook or `<laugh>` after an ironic line (max 1–2 per Reel, never in serious or sad posts). Tags are only spoken, never shown; the Reel's length follows the voice (aim 12–25 s). Write beats to be **heard** as well as read: natural spoken Albanian, no lists of symbols, numbers written so they read well aloud.
- `video_query`: concrete, literal, moving footage (a person doing the thing, the place). No visible brand names or logos, no close-up faces. If no footage fits after 3 searches, `"video_query": "none"` on the post gives a dark moving background: never drop a Reel over footage.
- `music`: `mood:cinematic`, `mood:piano` (emotional), `mood:dark` (stoic, serious), `mood:lofi` (tips, business how-to), `mood:uplifting` (success stories). Tracks live in `fabrika/music/` (see tracks.json).
- Each shot's frame: text readable and not cut off, footage fits the sentence, no logos, no black frames. The video itself is `reel.mp4`.
- Caption: same rules as posts, and always a send/comment prompt.

## Animated Reels (`"engine": "motion"`)
For AI tools, side hustles and how-tos (things stock footage can't show: tools, steps, prices, before/after), the 12:00 Reel can be an animated Reel instead of footage, **2–3 times a week**. Same voice, music (use `mood:lofi` or `mood:uplifting`), sound effects and review. Give the post a `video_query` and each beat its own `video_query` (literal, what the sentence is about): that footage plays blurred and darkened behind the animation and changes on every beat. Without footage the background is animated gold light and particles.
```json
{"id": "p2", "style": "reel", "engine": "motion", "time": "12:00", "voice": "gemini:Riko", "music": "mood:lofi",
 "video_query": "cafe interior coffee",
 "beats": [
  {"type": "hook", "text": "HOOK (max ~12 words)", "video_query": "barista making coffee cafe"},
  {"type": "list", "title": "Të duhen vetëm:", "items": ["...", "...", "..."], "say": "what the voice says"},
  {"type": "steps", "title": "Si fillon:", "items": ["...", "...", "..."], "say": "..."},
  {"type": "number", "value": 15, "from_value": 0, "prefix": "", "suffix": " min", "label": "...", "say": "..."},
  {"type": "compare", "left": {"label": "...", "items": ["...", "..."]}, "right": {"label": "...", "items": ["...", "..."]}, "say": "..."},
  {"type": "text", "text": "...", "highlight": "PAYOFF"}
 ],
 "caption": "..."}
```
- 4–5 beats, pick the types that fit the idea (not all of them). Items: 2–3 per list/steps, max ~4 words each. Compare: 2 items per side.
- `say` is what the voice reads for list/steps/number/compare beats. Say each item using its first word, so it appears on screen exactly when spoken. Keep the whole Reel to **~50 spoken words (25–30 s)**.
- Numbers must be true and realistic (time, cost of a tool, number of steps), **never income promises**.
- Review: one frame per beat (`frame-NN.jpg`), check text fits and nothing overlaps.

## Stickman Reels (`"engine": "stickman"`)
A third look, approved by the owner: a minimalist white line-art stickman on a dark grey background acts out each sentence, captions appear word by word in the middle with the key words in **red**. Calm, a little melancholic, very relatable. Best for "your life right now vs what it could be" stories: the 9–5 loop, scrolling instead of building, procrastination, habits, saving, starting something on the side. Not for tools or step lists (use the animated Reel) or real people's stories (use footage).
- Use it **2–3 times a week**, usually in the 18:00 slot (it may replace the 12:00 animated Reel when the idea fits better). Never two stickman Reels on the same day, and not on two days in a row. Alternate with footage and animated Reels so the feed stays varied; once `own_posts` has numbers, use more of whichever look performs.
```json
{"id": "p4", "style": "reel", "engine": "stickman", "time": "18:00", "voice": "gemini:Riko", "music": "mood:piano",
 "beats": [
  {"scene": "wake", "clock": "06:30", "text": "Zgjohesh në 06:30.", "red": "06:30", "say": "Zgjohesh në gjashtë e tridhjetë."},
  {"scene": "desk", "text": "Tetë orë për ëndrrën e dikujt tjetër.", "red": "dikujt tjetër"},
  {"scene": "phone", "text": "Në mbrëmje, dy orë në telefon.", "red": "dy orë"},
  {"scene": "laptop", "text": "Ato dy orë mund të ishin biznesi yt.", "red": "biznesi yt"},
  {"scene": "face", "text": "Fillo sonte. Edhe pak.", "red": "sonte"}],
 "caption": "..."}
```
- **5–8 beats**, one short sentence each (max ~10 words), written as a story in the second person ("ti"). The whole Reel: ~45–60 spoken words (20–30 s). The last beat is the turn: what the viewer can do differently, usually with `scene: "face"` (the stickman turns to the camera).
- `red`: 1–3 words that appear exactly in that beat's `text` (the emotional or key word). Every beat has one.
- `scene` per beat, pick what the sentence shows: `wake` (bed, sits up; add `"clock": "HH:MM"` for a big red time), `commute` (walks to work with a briefcase), `desk` (office desk, clock spinning), `home` (comes home to an empty room), `stress` (hand on head, clock spinning), `phone` (on the couch scrolling at night), `laptop` (working on a laptop at night: the side hustle), `walk` (walking down a street), `run` (running: speed, competition), `stairs` (climbing steps to a red flag: progress), `money` (coins stacking up: saving), `think` (hand on chin, red "?"), `face` (turns to the camera with a red glow: the payoff). Don't use the same scene twice in a row.
- Voice: Riko, same as other Reels. Use `say` when the text has numbers or times that should be read out in words. Music: `mood:piano` (default) or `mood:dark`. No whooshes (set automatically).
- Review: one `frame-NN.jpg` per beat. Check the caption fits (max 3 lines), the red word is the right one, and the scene matches the sentence.

## Buffer free plan
Max 10 scheduled posts per channel at a time. Schedule only the current day (5 posts), never days ahead.

## Quality gate (every run)
1. `python fabrika/spellcheck.py queue/<date>.json` must pass. Add real proper names to `fabrika/dict/allowlist.txt`, never a misspelling.
2. After the Render action, open every image in `out/<date>/`: text readable, nothing cut off, photo fits the message, no awkward or inappropriate photo.
3. **Never drop a post because of its photo.** Try up to 3 photo searches (each one concrete and literal: a person doing the thing, the place, the object). If none fits, set `"photo_query": "none"` and the post renders on a plain dark background, which always works. A post is dropped only if its text or facts are wrong and can't be fixed.
4. When re-rendering, **lock every photo that passed** by adding `"photo_id": "<pixabay_id from manifest>"` to that post, and only change `photo_query` on the posts that failed. Otherwise every photo gets re-picked.
5. Approve only posts that pass: write `approved/<date>.json` with `{"date": "...", "approve": ["p1", ...]}`. A failed post can be fixed (edit the queue, re-render) or dropped.
