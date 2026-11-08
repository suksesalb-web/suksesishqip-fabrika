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
| 12:00 | `story` (carousel, 5–7 slides) | **AI or side hustle:** something a person can actually do with AI tools or a skill, from Albania, step by step |
| 15:00 | `quote` | A verified quote from a thinker, with the source named |
| 18:00 | `story` (carousel, 5–7 slides) | **Business:** how to start or grow a small business, or how a real person built one (mini-story) |
| 22:00 | `tweet` | A reflective, personal-sounding thought people send to a friend |

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
- If today's file is missing, use the most recent one, or carry on without it.

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

## Buffer free plan
Max 10 scheduled posts per channel at a time. Schedule only the current day (5 posts), never days ahead.

## Quality gate (every run)
1. `python fabrika/spellcheck.py queue/<date>.json` must pass. Add real proper names to `fabrika/dict/allowlist.txt`, never a misspelling.
2. After the Render action, open every image in `out/<date>/`: text readable, nothing cut off, photo fits the message, no awkward or inappropriate photo.
3. When re-rendering, **lock every photo that passed** by adding `"photo_id": "<pixabay_id from manifest>"` to that post, and only change `photo_query` on the posts that failed. Otherwise every photo gets re-picked.
4. Approve only posts that pass: write `approved/<date>.json` with `{"date": "...", "approve": ["p1", ...]}`. A failed post can be fixed (edit the queue, re-render) or dropped.
