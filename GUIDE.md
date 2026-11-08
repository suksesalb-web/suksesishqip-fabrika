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
| 12:00 | `reel` (12–25 s) | **AI or side hustle:** one concrete thing a person can do with AI tools or a skill, from Albania |
| 15:00 | `quote` or `story` | Books & thinkers: a verified quote with the source named, or (2–3 times a week) a "mësime nga libri" carousel (see Book posts) |
| 18:00 | `reel` (12–25 s) | **Business or money:** a sharp money/business truth, or how a real person built something (mini-story) |
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
```json
{"id": "p2", "style": "reel", "time": "12:00",
 "video_query": "man driving car at night city lights",
 "voice": "sq-AL-AnilaNeural", "music": "mood:cinematic",
 "beats": [{"text": "HOOK"}, {"text": "..."}, {"text": "...", "highlight": "PAYOFF"}],
 "caption": "..."}
```
- **3–5 beats.** Beat 1 is the hook: max ~12 words, a surprising, specific claim that makes someone think of a person they know. Other beats: max ~18 words. The last beat lands the payoff in `highlight` (gold), max ~6 words.
- The voice (Anila) reads every beat while it's on screen; the Reel's length follows the voice (aim 12–25 s). Write beats to be **heard** as well as read: natural spoken Albanian, no lists of symbols, numbers written so they read well aloud.
- `video_query`: concrete, literal, moving footage (a person doing the thing, the place). No visible brand names or logos, no close-up faces. If no footage fits after 3 searches, `"video_query": "none"` gives a dark moving background: never drop a Reel over footage. Lock footage that passed with `"video_id"`.
- `music`: `mood:cinematic`, `mood:piano` (emotional), `mood:dark` (stoic, serious), `mood:lofi` (tips, business how-to), `mood:uplifting` (success stories). Tracks live in `fabrika/music/` (see tracks.json).
- Review a Reel by opening its `frame-01.jpg … frame-NN.jpg` (one per beat): text readable and not cut off, footage fits, no logos. The video itself is `reel.mp4`.
- Caption: same rules as posts, and always a send/comment prompt.

## Buffer free plan
Max 10 scheduled posts per channel at a time. Schedule only the current day (5 posts), never days ahead.

## Quality gate (every run)
1. `python fabrika/spellcheck.py queue/<date>.json` must pass. Add real proper names to `fabrika/dict/allowlist.txt`, never a misspelling.
2. After the Render action, open every image in `out/<date>/`: text readable, nothing cut off, photo fits the message, no awkward or inappropriate photo.
3. **Never drop a post because of its photo.** Try up to 3 photo searches (each one concrete and literal: a person doing the thing, the place, the object). If none fits, set `"photo_query": "none"` and the post renders on a plain dark background, which always works. A post is dropped only if its text or facts are wrong and can't be fixed.
4. When re-rendering, **lock every photo that passed** by adding `"photo_id": "<pixabay_id from manifest>"` to that post, and only change `photo_query` on the posts that failed. Otherwise every photo gets re-picked.
5. Approve only posts that pass: write `approved/<date>.json` with `{"date": "...", "approve": ["p1", ...]}`. A failed post can be fixed (edit the queue, re-render) or dropped.
