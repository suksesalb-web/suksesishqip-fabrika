# Where our content comes from (source list)

Mario's decision (2026-11-15): the look and the voice are good, the content was thin. Every post now starts
from a real source item, found in an extensive weekly research run. He chose these source groups.
Take the idea, the case or the method; write it in our own words, with Albanian numbers. Never copy wording,
never present someone's video or post as ours. If a site is blocked or fails to load, skip it: never go around a block.

## A. Real cases with numbers (side hustle, business)
- Indie Hackers stories: https://www.indiehackers.com/stories (loads; what it cost to start, the first client, what failed)
- Side Hustle Nation: https://www.sidehustlenation.com/blog/ (loads; one concrete case per article)
- The Hustle: https://thehustle.co/ (loads; business stories with numbers)
- Fiverr category pages (load): real prices for one job, e.g. https://www.fiverr.com/categories/writing-translation
- Starter Story and Upwork did not load on 2026-11-15: reach their content through web search results instead.
- Reddit (r/sidehustle, r/freelance, r/smallbusiness, r/personalfinance, r/albania) is blocked for us: do not fetch it
  and do not use mirrors. When a web search result summarises a Reddit discussion, that summary may be used as a lead.

## B. Strong money ideas and formats (the idea is theirs, the numbers become Albanian)
- Money Saving Expert: https://www.moneysavingexpert.com/ (loads; practical consumer tricks)
- Collab Fund blog (Morgan Housel): https://collabfund.com/blog/ (loads; behaviour with money)
- Ramit Sethi, Caleb Hammer (Financial Audit: one real budget taken apart), Humphrey Yang (money made visible),
  Vivian Tu, Nischa, The Financial Diet, Personal Finance Club: followed through the YouTube and Instagram watchlists below.
- AI, practical: Anthropic and OpenAI prompt libraries, Ethan Mollick (One Useful Thing; the site needs a browser,
  so find the posts through web search). Every prompt is tried in Albanian before it is posted.

## C. Our own intelligence (collected every morning by the Trend report action)
- `data/trends/<date>.json`: `by_search` and `top` = the fastest-growing short videos of the last 48 h;
  `channels` = the best videos of the last 30 days from data/youtube_watchlist.txt with descriptions and top comments.
- `data/instagram/<date>.json`: `outliers` from data/instagram_watchlist.txt, and our own posts.
- `data/metrics/latest.md`: what won and lost for us on TikTok and Instagram.

## D. Our own viewers
- `data/audience/questions.md`: comments and questions Mario collects. A viewer's question beats every other source.

## Checking (fixed rule from GUIDE "Added value")
Albanian prices, wages, rates and taxes used in a post are checked on the day with a web search
(INSTAT, Banka e Shqipërisë, tatime.gov.al, bank price lists, Monitor) and the link goes in the post's "sources".
