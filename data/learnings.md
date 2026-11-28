# What works for @suksesishqip (learnings)

Written by the 3-day review (and by hand when Mario decides something). The daily run reads this file
before writing posts and follows it, inside the rules of GUIDE.md. Newest entries on top. Each entry:
what the numbers showed, why we think so, and the concrete change for the next posts.

## 2026-11-28 (3-day review; newest complete Buffer data is of 26 Nov ~05:30; judged: posts up to 24 Nov, 25 Nov early)
**Data problems first.**
- **Nothing was published on 26 and 27 Nov.** The Render action failed both days before it started: `apt-get install ffmpeg…` got 404s (stale package index on the runner; it needs `apt-get update` first). Mario has been told; the review may not edit workflows. So there are no numbers for 26–27 Nov, and **the 26–27 Nov posts are unused** (not in topics_log): they are ready, checked work posts and may be used as replacements (see Changes 4).
- **Buffer metrics are rate-limited:** 27 Nov 21 of 80 posts came back "Too many requests", 28 Nov 80 of 80 (a re-run at 06:48 got 3). So **today's `data/metrics/latest.md` is all zeros: ignore it, use the numbers below.** The script asks Buffer once per post per platform (~150 calls each morning); batching them or only asking for the last ~10 days would fix it (code change for Mario/a later run; publishing also uses the Buffer API).
**Numbers. TikTok** (usual level of 13–24 Nov now 1 158 views; 19–24 Nov tweets median 2 079, Reels 756).
- Best: 23 Nov 18:00 payslip Reel **60 203 views, 453 shares, 14,1 s**; 23 Nov 15:00 festa tweet 30 615 / 331 shares; **24 Nov 18:00 overtime Reel "Rroga 60.000 lekë dhe rri pas orarit pa pagesë, kur ligji thotë +25%!" 3 558 → 29 535 in one day, 288 shares**; 21 Nov italisht tweet 17 689 / 124 shares / 41 comments; 22 Nov pushimet tweet 10 478; **25 Nov 18:00 sick-pay Reel "Rroga 70.000 lekë dhe sëmuresh tri ditë…" 8 716 / 40 shares in under 12 h**; 24 Nov gjobat tweet 7 825; 22 Nov raise-prompt Reel 7 570; **25 Nov 15:00 "Të dërgojnë 500 euro nga jashtë çdo muaj?" 5 597 in ~14 h** (only 2 shares); 23 Nov interview Reel 5 527.
- Weakest: 21 Nov 0% këste 428; 22 Nov fatura 530; 25 Nov 12:00 UGC/phone-camera tweet 630 (17 h, 6,2 s); 21 Nov qira 643; 24 Nov dhuratat 678; 25 Nov phone-plan Reel 750 (only 8 h); 23 Nov gjermanisht tweet 1 000 (5,0 s); 24 Nov Excel tweet 1 199.
**Instagram** (own_posts fine, token OK, 22 followers): best 25 Nov 18:00 sick-pay Reel 184 reach, 3 saves, 2 shares (our best IG reach so far); 20 Nov dy punë 150; weakest 23 Nov 21:00 interview 24 and 24 Nov 18:00 overtime 25 (a TikTok winner: IG reach is still noise). TikTok decides.
**Why.**
- **Salary + the law = our biggest Reels.** The 3 biggest Reels the page has ever had (60 203, 29 535, 8 716 in < 12 h) all have the same shape: the viewer's rroga as the number on the cover, then a line of the Kodi i Punës (or the payslip) that shows the employer owes them something (the firm's real cost, +25% for overtime, 80% for sick days), then the exact step. It is relatable (everyone has a boss), it feels like a secret, and it has an obvious person to send it to (every coworker): 40–453 shares. The overtime Reel shows TikTok can take a day to push a winner: judge at 36–48 h, not at 20 h.
- **Spending is now 0 for 10.** The phone-plan Reel was the week's test of "a bill everyone has" and sits at 750 (early); best spending post ever is bankomati 1 304. All 10 spending/bills/banks/shopping Reels since 19 Nov: 341–1 304, 0–2 shares. Evidence, not a hint.
- **Side hustle tweets: only a language that very many Albanians speak works.** English 67 387 and Italian 17 689 vs German 1 000, Excel 1 199, phone camera/UGC 630 (also "150–200 $ për video" for brands sounds far from the viewer). 12:00 tweets 21–25 Nov median 1 100 → above the 600 undo line, the 5 tweet days stay.
- **The diaspora money tweet** (500 € sent from abroad lost ~3 800 lekë with the euro) reached 5 597 fast: money the family already has, a number they feel. One post: a hint.
**Changes (GUIDE.md updated).**
1. **18:00 Reel: salary + a right is the first choice** ("Rroga X lekë" as `big` + the article that says what the employer owes + the step), at least 4 of 7 days. Evidence: 60 203 / 29 535 / 8 716 vs salary-only Reels without a right (kafe 1 624, 100.000 → 79.700 1 178) and spending 341–1 304.
2. **Spending / bills / banks / shopping: at most 1 post a week** (was 2), with the salary as `big`. Evidence: 0 of 10 above 1 304 TikTok views, 0–2 shares, including this week's fairest test (phone plan 750).
3. **Side hustle tweet: at least 2 of the 5 a week on a language very many Albanians speak** (English, Italian; Greek is untested and worth one try) or on writing Albanian; the phone camera / UGC idea is dropped for now. Evidence: English 67 387, Italian 17 689 vs German 1 000, Excel 1 199, UGC 630.
4. **Unpublished posts are reusable.** If a day's posts never went out (render/publish failure), they stay unused, are not logged in topics_log, and the daily run may use one as the day's replacement in the next 7 days (re-check every number and any job listing first). Evidence: 26–27 Nov, eight finished posts lost to the render failure.
5. **Undo window for the 21:00 work rule moved:** 26 Nov–2 Dec had no published work Reels yet, so the check is now the first 7 published 21:00 work Reels from 28 Nov (median ≥ 1 500, else back to the 22 Nov wording). Interview 5 527 and raise prompt 7 570 already support it.
**For the daily runs (one replacement a day):** 28 Nov p4 (bank account fees, big "3.600 lekë" = spending) → the 26 Nov p4 work Reel "Mbyll në mesnatë dhe hyn prapë në 07:00, kur ligji të jep 11 orë pushim!" (neni 78; re-check; put a salary in the hook or kicker if it reads naturally). 28 Nov p3: the `big` is "31 ditë": make it **"60.000 lekë"** (the salary is in the hook already; the rule is salary as `big`). 29 Nov p4 (forgotten subscriptions, big "42%" = spending) → the 27 Nov p4 notice Reel ("Gjete punë më të mirë dhe do ikësh nesër…", njoftimi 2 javë / 1 muaj / 3 muaj). 29 Nov p2 (kafe vs qira tweet) is the week's one spending post: keep it. Later tweet days: the unpublished 26 Nov p1 (shkruan shqip, Albanian Language Specialist: re-check that the listing is still open), 26 Nov p2 (shefi në 22:00) and 27 Nov p2 (neni 81, puna e natës +50%) are ready replacements.
**Watch next.** Does the render work again on 28 Nov (if not, nothing gets published and Mario must fix render.yml)? Do Buffer metrics come back (if not, the next review has only Instagram)? Final numbers of the 25 Nov sick-pay Reel, the diaspora tweet and the phone-plan Reel. The 4th and 5th Kodi i Punës tweets (pay date 28 Nov, then neni 81 or other): do they keep 5 000+? 29 Nov 18:00 "Rroga 900 euro në Itali…" as a second diaspora test.

## 2026-11-25 (3-day review, Buffer data of 25 Nov ~05:30; judged: posts 21–23 Nov; 24 Nov under 20 h, noted as early)
**Numbers. TikTok** (usual level now 623 views; tweets median 1 470, hype Reels 730). The cool-down of 18–20 Nov is over: 23 Nov was the best day since 17 Nov.
- Best: 23 Nov 18:00 payslip Reel "Rroga 50.000 bruto: firma paguan 58.350, ti merr 44.400!" (big "50.000 lekë") **45 409 views, 336 shares, 14,2 s** (best watch time ever); 23 Nov 15:00 tweet "Punon sot, edhe pse është festë? Kodi i Punës (neni 87)…" **29 092, 319 shares**; 21 Nov 12:00 italisht/Fiverr tweet 16 763, 119 shares, 41 comments; 22 Nov 15:00 pushimet tweet 10 079, 18 shares; 22 Nov 12:00 raise-prompt Reel 5 885 (best 12:00 Reel ever); 23 Nov 21:00 interview Reel 4 292.
- Early (< 20 h) but already up: 24 Nov 15:00 gjobat tweet 6 423, 24 Nov 18:00 overtime Reel 3 558 / 25 shares.
- Weakest: 21 Nov 21:00 0% këste 381 (6,8 s); 22 Nov 18:00 fatura +700 lekë 451 (8,0 s); 21 Nov 18:00 qira 57% 598; 23 Nov 12:00 gjermanisht tweet 901 (5,0 s); 22 Nov 21:00 bankomati 999; 24 Nov 21:00 dhuratat 251 (early). All 0 shares.
**Instagram** (own_posts fine, token OK, 19 followers): Reels 13–147 reach. Best: 20 Nov 21:00 dy punë 147, 23 Nov 18:00 payslip 121, 22 Nov 12:00 raise 118. Weakest: 23 Nov 21:00 interview 22, 24 Nov 18:00 overtime 13 (early). Still too small to steer by; TikTok decides.
**Why.**
- **Employer beats spending, 9 to 0.** Every post 21–24 Nov about the viewer as an employee (a right, the payslip, the boss, the interview, the raise) went above the usual level: 10 079, 29 092, 6 423*, 45 409, 5 885, 4 292, 3 558*, plus 20 Nov dy punë 2 748. Every post about spending, bills, banks or shopping stayed at 251–999 with 0 shares (këste, fatura, qira, bankomati, dhuratat; before them TV 305, kredi 676). Watch time was not the problem (6,8–12,3 s): nobody sent them. A bill or a bank fee is a private fix; "the boss owes you +25%" or "the firm pays 58.350 for your 44.400" is something you send to every coworker, and it feels like a secret being told. That is the share engine.
- The payslip Reel won on the cover rule from 22 Nov (salary as `big`) plus a new surprise (what the firm pays, not only what you lose): a follow-up with its own shock, as the rule asks. The two 18:00 Reels with the salary only in the kicker and a percentage as `big` (57%, and 40% at 21:00) failed.
- Side hustle tweets: italisht 16 763 vs gjermanisht 901 and Excel 1 055. Same shape, so the difference is how many people have the skill (very many Albanians understand Italian; few German; "Excel better than your colleagues" is a narrow claim) and the price: "5 dollarë" per job is concrete, "0,05–0,20 dollarë për fjalë" sounds like nothing (5,0 s watch time). 12:00 tweets 21–24 Nov: median 1 055 → above the 600 undo line, the 5 tweet days stay.
- The raise-prompt Reel (22 Nov, Sunday 12:00) is the first 12:00 Reel above 940 in 14 tries: work again, not a side hustle. One post: a hint.
- Posting times and trend use: no new evidence (all slots had winners and losers); no change.
**Changes (GUIDE.md updated).**
1. **21:00 `p4` = a work situation** (interview, raise, overtime, sick days, notice, payslip line, late message) with the exact sentence or step. Evidence: work posts 9 of 9 above usual vs spending posts 0 of 8 (251–999, 0 shares). Undo if the 21:00 work Reels of 26 Nov–2 Dec have a median under 1 500.
2. **Spending / bills / banks / shopping: at most 2 posts a week**, each hooked to the salary on the cover. New paragraph in GUIDE ("Spending is not the viewer's pain, the employer is"). Same evidence.
3. **15:00 tweet: a worker's right 3–4 days a week** in the festa shape: "Punon sot, edhe pse është festë?" / "Kodi i Punës (neni 87): …" / "Shëno: …". Other strong first lines: "Të mbajtën 2.000 lekë nga rroga se u vonove 10 minuta?", "Rroga 80.000 lekë dhe s'i ke marrë ende pushimet e këtij viti?". New ones to try (check the article first): "Të mbajnë 3 muaj 'në provë' pa kontratë?", "Të thanë që s'ke të drejtë për pushime se je i ri në punë?", "Shefi të thotë që orët shtesë 'i ka rroga'?". Evidence: 3 of 3 Kodi i Punës tweets 6 423–29 092 vs other 15:00 tweets 557–2 033. Never the same article twice in 30 days.
4. **18:00: the salary as `big`**, not only in the kicker; payslip / pay-rights angles count as salary Reels. Evidence: big "50.000 lekë" 45 409 (and the 5 earlier winners) vs big "57%" 598 and "40%" 251.
5. **Side hustle tweet: a skill most Albanians have** (English, Italian, writing Albanian, phone camera, Canva) and the price of one job, never cents per word. Evidence: italisht 16 763 vs gjermanisht 901 / Excel 1 055. A hint-to-moderate signal, so it is a wording rule, not a mix change. On Reel days at 12:00 a ready AI prompt for the viewer's own job is allowed (raise prompt 5 885; 1 post = hint).
6. **Weekly research (Sunday 29 Nov): at least 10 employee items** in the bank (unused Kodi i Punës rights, payslip, contracts, probation, notice, interviews), spending/bank items at most 4. The 23 Nov bank has only 2 unused labour items left (severance, annual leave).
**For the daily runs this week (one replacement a day, allowed as follow-ups of the 23–24 Nov winners):** 26 Nov p4 (Black Friday "3 pyetje"; both Black Friday Reels sat at 305 and 381) → a work Reel from items 2 + 6 of the research bank, e.g. "Rroga 60.000 lekë: cilat zbritje te fletëpagesa janë të ligjshme, dhe cila jo" (contributions 11,2% yes, fines no, art. 122(3)); 28 Nov p4 (bank account fees) and 29 Nov p4 (forgotten subscriptions) → a work situation if a checked item is ready, otherwise keep and put the salary as `big`. 25 Nov p4 (phone plan) stays as the week's test of a bill everyone has.
**Watch next.** 21:00 work Reels 26 Nov–2 Dec (median ≥ 1 500?). Do Kodi i Punës tweets keep 5 000+ or fade with repetition (watch the 4th and 5th)? 25 Nov phone-plan Reel and 26 Nov AI-jobs side hustle tweet (writing Albanian: a wide skill). Final numbers of 24 Nov overtime Reel and gjobat tweet. Instagram: any Reel past 200 reach.

## 2026-11-22 (3-day review, Buffer data of 22 Nov ~05:30; judged: posts up to 20 Nov; 21 Nov still at 0 = Buffer lag)
**Numbers. TikTok** (usual level 470 views; tweets median 1 212, hype Reels 584):
- The page cooled down after 16–17 Nov: median per post 16–17 Nov ~6 100 views, 18–20 Nov **~580**. Shares: winners 16–667 each; 18–20 Nov every post 0–1 except the 18:00 kafe Reel (9).
- Best of the period: 18 Nov 15:00 mama tweet 3 476 (family, now stopped); 18 Nov 18:00 "kafe + ujë = 48 minuta punë" 1 624, 9 shares; 20 Nov 21:00 "dy punë me nga 50.000: 6.500 lekë tatim" 946. Older winners kept growing: Fiverr tweet 67 387 / 667 shares, 50/30/20 49 428, tax trap 25 140.
- Weakest: 19 Nov 21:00 Black Friday TV "-40%?" 214; 20 Nov 18:00 kredi 500.000 → 667.000 358 (11,3 s watched!); 20 Nov 15:00 babai tweet 411; 19 Nov 12:00 karroca 411; 18 Nov 21:00 punë private 3.000 lekë 535; 19 Nov 18:00 "100.000 → 79.700" 874 (12,9 s watched); 19 Nov 15:00 inflacioni/paga mesatare tweet 648.
- 12:00 side hustle Reels: 577 (xhama), 411 (karroca), 590 (albume, with "mbrëmjet i ke të lira"). Now 0 for 13, best 940.
- Too new: 21 Nov all four (italisht Fiverr tweet, qira tweet, qira 57% Reel, 0% këste Reel).
**Instagram** (own_posts fine, token OK, 19 followers, Reels only since 20 Nov): reach is either ~110–145 or ~10–35. Best: 20 Nov 21:00 dy punë 143 reach (1 save), 17 Nov 21:00 borxh 128, 17 Nov 18:00 tax 125, 18 Nov 18:00 kafe 112. Weakest: 18 Nov 21:00 punë private 9, 21 Nov 18:00 qira 26 (new). Too small to steer by; TikTok decides.
**Why.**
- Losers did not lose on watch time (kredi 11,3 s, 100.000 12,9 s, dy punë 9,2 s ≈ the winners' 9–13 s): people who saw them watched. They lost on **shares**, so TikTok never pushed them past the first pool. Each was for a narrow group: someone taking a loan, someone with two jobs, someone buying a TV, a freelancer pricing a job, someone earning 100.000. The winners are for everyone with a salary and have an obvious person to send them to (the friend whose rroga runs out, the coworker on the minimum wage, the cousin who knows English).
- **Cover pattern:** all 5 Reels above 5 000 views had the viewer's monthly rroga of 50.000–80.000 lekë on the first frame and were about the salary itself (how it's split, taxed, declared, lent). Reels with the salary only in small text or a purchase/loan on the cover stayed at 214–1 624. 5 of 5 vs 0 of 10: evidence.
- Follow-ups without a new surprise fade: the tax-trap idea (25 140) repeated as "100.000 → 79.700" (874) and "dy punë" (946). Same lesson, smaller audience.
- Side hustle Reel: the "mbrëmjet i ke të lira" hook did not save it either (590). It is the format (20 s of steps for someone else's kind of job), not the hook. The tweet version of a side hustle is our biggest post.
- The overall cool-down after a viral week is partly normal TikTok behaviour (the account got extra tests on 16–17 Nov); we can't separate that from content with this sample, but the share pattern above holds inside both periods.
**Changes (GUIDE.md updated).**
1. **Daily mix:** `p1` 12:00 side hustle **tweet on Mon, Tue, Wed, Thu and Sat** (was Mon/Wed/Sat); Reel only on Fri and Sun, and only in the Fiverr shape (skill the viewer has + real platform + real prices + one smart move). Evidence: side hustle Reels 0/13 above 940; tweets median 1 212 vs Reels 584; side hustle/work tweets 5 327 and 67 387. Undo if the 12:00 tweets of 21–27 Nov have a median under 600.
2. **18:00 = the viewer's salary itself** (40.000–80.000 lekë in hand, or 500–900 €), with the salary on the cover. Evidence: cover pattern above (5 of 5 vs 0 of 10). Strong first lines to model: "Nëse rroga prej 60.000 lekësh të mbaron më 20…", "Rroga bruto 50.000 lekë: një rritje 1.000 lekësh ta ul rrogën në dorë!", "Merr 80.000 lekë në dorë, dhe në fund të muajit prapë s'ke kursime?". New angles to try: "Rroga 60.000 lekë: sa të mbetet pas 1 dhjetorit (qira, fatura, dhurata)?", "Rroga 50.000 lekë hyn më 1: 3 lëvizjet e para para se ta prekësh", "Paga minimale 50.000 lekë: çfarë të mbahet nga fletëpagesa, rresht për rresht" (numbers checked on the day).
3. **21:00 = a situation almost everyone with a salary meets** (payday, the payslip, the boss, a friend asking money, December spending). No niche cases: loans, second jobs, freelance pricing, store sales (214–946, 0 shares).
4. **New "Sendability test" in GUIDE** (after the hook test): name who the viewer sends it to; if it's a narrow group, change the idea or hook it to the salary behind it. A follow-up needs its own new surprise.
5. **Side hustle tweets, 5 a week:** rotate skill and platform (at most 2 of 5 on Fiverr; Upwork, Preply-type tutoring, Canva, Excel, CVs, voice-over, local Facebook groups), numbers checked on the platform that day.
6. For the daily run today (22 Nov draft): p2 (sigurimi i makinës) and p4 (komisioni i bankomatit) are for narrow groups; if one post is replaced today, replace p2 with a salary-centred money tweet. p3 ("1 kWh më shumë → fatura +700 lekë") has the tax-trap shape (a small step that costs a lot): keep it, and if true, put the viewer's salary in the kicker or sub.
**Watch next.** 12:00 tweets of 21–27 Nov (median ≥ 600? any above 3 000?). Do salary-cover Reels at 18:00 get back above 3 000 and 10+ shares? 21 Nov qira Reel ("Qira 400 euro me rrogë 700 euro", salary in euro on the cover) and 0% këste Reel once counted. If the whole page stays near ~500 even with salary covers, the cool-down is account-level and the next review should look at posting times and trends instead.

## 2026-11-20 (Mario's decision, by hand)
**What.** Mario: tweets must not go to Instagram any more ("na hapën barkun"), and no more family tweets. On Instagram tweets reached only 4–17 accounts each and sat on the profile between the Reels; family tweets were also the weakest tweets on TikTok (594–2 971 vs 5 289–60 271 for money/work).
**Change.** `publish.py` sends image posts to TikTok only; Instagram gets only Reels. Family / personal tweets stopped: the 15:00 tweet is money / work every day, once a week a new kind (a work situation with the exact sentence to say). Today's family tweet (20 Nov 15:00) had already gone out on both platforms before the decision.
**Watch next.** Does the Instagram profile (Reels only) get more reach per Reel and new followers? Does the work-situation tweet beat the old family level (~1 500) on TikTok?

## 2026-11-19 (3-day review, Buffer data of 19 Nov ~05:30, judged: posts up to 17 Nov; 18 Nov still counting)
**Numbers. TikTok** (usual level now 436 views per post, hype Reels 801, tweets 1 447):
- Best: 17 Nov 15:00 tweet "Di anglisht dhe mbrëmjet i ke të lira? Në Fiverr…" **59 511 views, 611 shares, 13 comments, 10 s** (biggest post ever, 2 days after posting). Then 50/30/20 Reel (14 Nov) grew to 48 250 / 400 shares; 17 Nov 18:00 "Rroga bruto 50.000 lekë: një rritje 1.000 lekësh ta ul rrogën në dorë!" 19 260 / 71 shares / 12,9 s (best watch time); 16 Nov 18:00 "Merr 80.000 lekë në dorë…" 10 742; 16 Nov 15:00 tweet 90.119 lekë 5 796; 16 Nov 21:00 "70.000 në dorë, 50.000 në letra" 5 225; 17 Nov 21:00 "shoku kërkon 50.000 borxh" 4 723.
- Weakest: every 12:00 side hustle Reel: 16 Nov furniture 801, 17 Nov ChatGPT bank statement (60.000 again) 900, 18 Nov windows 486 (~20 h). Before that 193–466. Foreign stories: Blakely 458, Dyson 322, Nokia 225. Family tweet "babai, makina" 594.
- Too new: 18 Nov mama tweet 2 971 in ~20 h (best family tweet so far), "kafe = 48 minuta punë" 1 231, 21:00 "punë private 3.000 lekë" 281.
- By slot (16–17 Nov, the first full days of the new mix): 12:00 Reel 801/900 · 15:00 tweet 5 796/59 511 · 18:00 Reel 10 742/19 260 · 21:00 Reel 5 225/4 723. The 21:00 money Reel works (~5 000) when it is money, not a story.
**Instagram** (own_posts fine, token OK; ~17 followers): Reels 57–127 reach, tweets 4–17. Best of the period: 17 Nov 21:00 borxh Reel 127 reach, 2 shares; 17 Nov 18:00 tax Reel 122. Weakest: 18 Nov 21:00 Reel 4 reach. Nothing has broken out; too small to steer by, TikTok decides.
**Why.**
- Fiverr tweet won because line 1 picks out a real person ("di anglisht" + free evenings: almost every young Albanian, or their cousin), line 2 is a real platform with checked numbers, line 3 is a smart move (pick the category with fewer sellers). It is readable in 3 s and has an obvious person to send it to: 611 shares. The same side hustle idea as a Reel needs 20 s and a gear list before the payoff.
- Side hustle Reels with the viewer-money hook did lift from ~250 to ~800–900, but the hook ("rroga mbaron më 20") is the money Reels' hook while the content is someone else's job (furniture, windows, a van): the promise and the payoff don't match, people leave at ~7 s. 3 viewer-hook tries + 7 earlier, none above 900: evidence, not a hint.
- Paycheck mechanics win at 18:00 (gross vs net, the tax trap, 50/30/20 for a specific salary): it's a number the viewer has and a fact they did not know about it. Salary rotation works: 50.000 and 80.000 hooks won; the one with 60.000 (17 Nov p1) was the weakest that day.
- Foreign stories: 3 of 3 at the bottom. Family tweets: 5 of 5 at 594–2 971 vs 4 of 4 money/work tweets at 5 289–59 511.
**Changes (GUIDE.md updated).**
1. Daily mix: on **Mon, Wed, Sat** `p1` at 12:00 is a **side hustle tweet** in the Fiverr shape (skill the viewer has + platform + real prices + one smart move); Reel on the other 4 days. Evidence: 10 side hustle Reels ≤ 900 vs side hustle/work tweets 5 289 (logo) and 59 511 (Fiverr). Sized as a test: 3 days, not all 7.
2. Side hustle Reels on the other days: prefer online work with a skill the viewer has over equipment jobs (furniture 801, windows 486; Fiverr 59 511, logo 5 289). Moderate evidence.
3. Foreign success/failure stories and two-part stories paused (3 of 3 at 225–458).
4. 15:00 tweet: family 1 day a week instead of 2, from 23 Nov (5 family tweets vs 4 money tweets, see above). The mama tweet (2 971 in 20 h) is the best family one: if family ever wins, it is that kind (a habit of a parent you understand late).
5. Series on the Fiverr winner (GUIDE rule): **Sat 21 Nov `p1` becomes the first side hustle tweet** (the daily run's one allowed replacement; the mobile detailing Reel in the draft is an equipment job with a dollar figure and 60.000): another language Albanians know (italisht / gjermanisht / greqisht) on Fiverr or a similar platform, numbers checked that day, link in sources. Never the same "anglisht + Fiverr" again.
6. (Condensed 2026-11-28: one-off draft fixes for 19–22 Nov, done.)
**Watch next.** Side hustle tweet at 12:00 (21 Nov) vs the 12:00 Reel (~800): if two 12:00 tweets reach 3 000+, make it 5 days; if they stay under 1 000, the problem is the slot, not the format, and side hustle moves to 15:00 twice a week. 19 Nov 18:00 "100.000 → 79.700 në dorë" (follow-up of the tax trap): above 5 000? Mama tweet's final number. Does the 21:00 money Reel stay ~5 000?

## 2026-11-16 (3-day review, Buffer data of 16 Nov 05:48)
**Numbers.** Almost nothing new to judge since the 15 Nov analysis: Buffer did not refresh TikTok overnight (the 16 Nov file has the same numbers as the 15 Nov 18:09 one).
TikTok, judgeable posts of 13–15 Nov: best still reel/hype 50/30/20 "rroga 60.000 lekë" 30 975 views, 224 shares, 11,7 s; then tweets "telefoni 1.200€" 10 743 and "logo falas" 4 625.
Weakest: reel/hype Dyson 205 views, 3,5 s (lowest watch time of all Reels); side hustle "12,5 milionë të huaj… menu" 245 views, 4,5 s, 0 shares (15 Nov, first ~15 h).
Too new / not counted: 15 Nov 15:00 family tweet "babai, makina 20 vjet" 211 (~15 h), 15 Nov 18:00 inflation Reel and 21:00 Sara Blakely Reel 0 views (Buffer lag, see below).
Instagram (17 followers): best 50/30/20 Reel 113 reach, 6 shares, 1 save; menu Reel 78; every tweet 8–13 reach, including the TikTok winners (10 743 on TikTok = 8 reach on IG). own_posts works (token fine).
**Why.**
- The menu Reel is the 7th side hustle Reel at ~200–380 views and fails hook test points 1–2 exactly as predicted: tourists and cafe owners, a statistic (12,5 milionë), not the viewer. It was written before the hook test existed, so it does not count toward the "5 tries with a viewer-money hook" (those start 16 Nov).
- Dyson confirms foreign stories: a stranger's number, people leave at 3,5 s.
- Buffer lag: posts showed 0 at ~10 h and filled in the next day before (13 Nov 22:00 tweet 0 → 1 373, Nokia 0 → 225). So a 0 under ~36 h is not a flop.
**Checked the week's drafts (16–22 Nov) against the hook test.** 27 of 28 open from the viewer's money: good. Two weak spots:
(1) side hustle hooks are half viewer, half a foreign stranger in dollars ("komodinë 30 dollarëshe u shit 150" 16 Nov, "pajisje 200 dollarë" 18 Nov, "Josh e nisi me një punë 30 dollarëshe" 21 Nov), the kind of number that has never left ~250;
(2) the same number again and again: "rroga 60.000" in 6 hooks (17 Nov p1 + p4, 20 Nov p1, 21 Nov p1 + p4, 22 Nov p1) and "90.119 lekë" in two tweets (16 and 19 Nov). GUIDE's own series rule says other salaries; one figure is "my number" for only part of the audience and makes the feed look repetitive. Evidence for (2) is a reasoned risk, not yet our data: small change, watch it.
**Changes.**
- GUIDE hook test: the whole hook stays in the viewer's world and in lekë; the foreign person's dollar result comes after the hook as proof (evidence: every foreign-figure hook 200–250 views; every winner a lekë/euro number of the viewer).
- GUIDE: rotate the viewer's number: same rroga in at most 2 hooks a week, same figure in at most 1 post (evidence above, point 2).
- GUIDE: a 0 in latest.md for a post under ~36 h is Buffer lag, not a flop (evidence: the jumps listed above).
- (Condensed 2026-11-28: the wording fixes for the 16–22 Nov drafts were done that week.)
- No change to the daily mix or slots: the 15 Nov mix has had no judgeable day yet.
**Watch next.** The first viewer-money side hustle Reels (16–22 Nov p1): do any leave ~250? (5 tries, then 3 days a week.) 15 Nov inflation Reel and Sara Blakely Reel once Buffer counts them. 50/30/20 follow-ups (17 Nov p1) above 2 000? Money Reel at 21:00 vs 18:00. Family tweet "babai, makina" final number (was it the slot change to 15:00 or just slow counting?). Instagram: any Reel past 300 reach.

## 2026-11-15 (full analysis of 40 posts on TikTok + Instagram, asked by Mario)
**Numbers (Buffer, 8–15 Nov).** TikTok usual level: ~270 views per post. Above it, only these:
reel/hype "rroga 60.000 lekë, rregulli 50/30/20" 30 975 views, 224 shares, 12 comments, 11,7 s watched ·
tweet "telefoni 1.200€, paga 800€, 24 këste" 10 743 views, 31 shares · reel "300 lekë në ditë" 5 700, 35 shares, 9,4 s ·
tweet "logo falas si provë" 4 625 · family tweets 937–1 413.
Everything else sat at 190–420: all 6 side hustle / AI Reels (193–383 views, 1 share in total), both foreign story Reels
(Nokia 225, Dyson 205, watched 3,5–4,3 s), statements, quotes, book carousels.
Instagram: 17 followers, median reach ~13 for images and ~100 for Reels; nothing has broken out. The best-watched Reel there
is the same 50/30/20 one (8,1 s, 6 shares).
**Why.** The four winners share one thing: the first line is the viewer's own money as a number they already know
(rroga, kësti, 300 lekë në ditë), with a pain in it, and the post ends in a rule they can use. People watch 2–3 times longer
(9–12 s vs 3,5–5 s) and send it (31–224 shares vs 0). The look is not the cause: the same Hype look got 30 975 and 205.
The slot is not the cause either: 18:00 has both the best and ordinary posts. Side hustle Reels open with someone else's
problem (a cafe, a shop, tourists) and stories open with a stranger, so the viewer does not see themselves in second 1.
**Changes.**
- Daily mix: two money Reels a day (18:00 calculation + rule, 21:00 mistake or situation + fix); foreign company stories at most once a week.
- The 12:00 side hustle Reel stays (it is the page's core) but must open from the viewer's money, not the client's problem.
- Tweet: money / work with a number 5 days a week, family 2 days.
- "The hook test" in GUIDE.md: about the viewer, a number they already have, a pain in it.
- Series on winners (e.g. 50/30/20 for other salaries, the next step after saving).
- `fabrika/post_metrics.py` now writes `data/metrics/latest.md` every morning, so the daily run sees TikTok numbers (before, it only saw Instagram's).
**Watch next.** Does the side hustle Reel leave the ~250 level with a viewer-money hook? If not after 5 tries, move it to 3 days a week.
Do the 50/30/20 follow-ups hold above 2 000? Does a money Reel at 21:00 do as well as at 18:00? Instagram: is any Reel passing 300 reach?

## TikTok snapshot 2026-11-13 19:10 (screenshot from Mario)
Views: reel/footage "300 lekë në ditë" (11 Nov) 5 060 · tweet babai (11 Nov) 1 391 · tweet "Telefoni 1.200€, paga 800€" (13 Nov 15:00, only 4 h old) 1 179 · tweet ankthi "deri në 30" (12 Nov) 623 · statement talenti (12 Nov) 382 · reel/footage ChatGPT idea test (12 Nov) 302 · quote Kiyosaki 278 · statement tulla (13 Nov) 210 · carousel Babylon 203 · reel/stickman "Thua" 196 · reel/motion CV (13 Nov) 146 · reel/hype Nokia (13 Nov 18:00, only ~1 h old) 74.
**Pattern.** The two biggest TikTok posts and the fastest riser are personal money math in lekë/euro from Albanian life (300 lekë/day → 109 500/year; phone 1 200€ vs salary 800€ in 24 instalments): 1 179 views in 4 h for a plain tweet. Family tweets stay second. Foreign company stories and generic advice sit at 150–400.
**Use it.** Hooks with the viewer's own money (rroga, këste, kafe, qira, telefon) in lekë/euro beat everything else so far; prefer the "numbers" kind for Reels and tweets until a story Reel proves otherwise. Re-check the Nokia hype Reel after 24 h before judging the new look.

## 2026-11-13 (competitor analysis, decided with Mario)
**Evidence.** In the 6 daily Instagram reports, carousels were ~50% of the watched pages' outlier posts and have the highest median score; Entrepreneur's founder-story carousels (a name + an age or number on the cover) repeatedly beat their usual reach. Our own carousels were book lessons and flopped.
**Change.** Story carousels twice a week at 15:00 (see GUIDE "Story carousels"), with a true clickbait-style cover and a cliffhanger on every slide; no "swipe" label on covers. Everything needs a hook.
**Watch next.** Story carousels vs tweets at 15:00 (reach, saves, shares on Instagram; views on TikTok photo carousels).

## 2026-11-13 (first review, data 8–12 Nov, by hand with Mario)
**Numbers.** Instagram (reach, median): Reels ~115, tweets ~45 (one reached 423), quotes ~16,
carousels ~15, statements ~10. TikTok (views, from Mario's screenshot): the money Reel "300 lekë në ditë"
5 007, family tweets 1 386 and 924, statements ~400, quote 277, motion Reel 204, book carousel 170,
stickman Reels 14 and 178.
**Why.** Posts that win make the viewer think of their own life in one second: a number from
Albanian daily life (lekë, rroga, këste) or a warm family moment (mum, dad, home). Generic poster
lines, long quotes and book lessons don't stop the scroll. Stickman was too calm for TikTok.
**Changes (Mario's decisions).**
- All Reels in the Hype look, with a hook built on a shocking true number or contrast.
- All three image slots are tweets: concrete, with a number or a scene, 22:00 personal/family.
- Book carousels and quotes at most once a week.
**Watch next.** Hype Reels vs the old Reels (reach, views, shares); which Reel kind wins
(story, numbers, situation); which tweet slot wins (09:00 / 15:00 / 22:00); do numbers in the
hook beat no-number hooks?
