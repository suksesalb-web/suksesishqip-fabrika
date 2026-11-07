# @suksesishqip — content guide

This file is the brief every daily run follows. Change it to change what the page posts.

## The page
- Albanian-language Instagram page about discipline, mindset, lessons from great thinkers and successful people, and honest side-hustle ideas.
- Voice: direct, warm, grounded. Like a smart older friend, not a guru. Short sentences.
- Standard Albanian (gjuha standarde) with correct ë and ç everywhere. No English words where an Albanian one exists.

## Daily mix (3 posts)
| Slot (Tirana time) | Style | What |
|---|---|---|
| ~10:40 | `statement` or `tweet` | One sharp idea on discipline or mindset |
| ~15:20 | `story` (carousel, 4–6 slides) | A success story or a practical lesson (side hustle, money habit, book idea) |
| ~20:10 | `quote` or `tweet` | A verified quote, or a reflective thought |

Rotate topics across the week: discipline, habits, money mindset, side hustles that work from Albania, stories of people who built something, Stoic ideas, book lessons. Check `data/topics_log.txt` and don't repeat a topic or quote used in the last 60 days.

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

## Quality gate (every run)
1. `python fabrika/spellcheck.py queue/<date>.json` must pass. Add real proper names to `fabrika/dict/allowlist.txt`, never a misspelling.
2. After the Render action, open every image in `out/<date>/`: text readable, nothing cut off, photo fits the message, no awkward or inappropriate photo.
3. Approve only posts that pass: write `approved/<date>.json` with `{"date": "...", "approve": ["p1", ...]}`. A failed post can be fixed (edit the queue, re-render) or dropped.
