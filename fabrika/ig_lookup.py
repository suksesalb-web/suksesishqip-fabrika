"""One-off research: public numbers of Instagram professional accounts (Business Discovery).

Usage: python fabrika/ig_lookup.py name1,name2,...   -> data/instagram/lookup-<date>.json
Per account: followers, posts, median likes/comments over the last 30 posts, engagement rate,
format mix, posts per week, and the 5 best posts (caption start, format, likes, comments, views).
Accounts that don't exist or aren't professional accounts are listed with the error.
"""
import json, statistics, sys
from datetime import datetime, timezone
from pathlib import Path
from trends_instagram import api, our_account, discover, fmt, ROOT

names = [n.strip().lstrip("@") for n in sys.argv[1].split(",") if n.strip()]
me = our_account()
out = []
for u in names:
    try:
        acc = discover(me["id"], u)
    except RuntimeError as e:
        out.append({"username": u, "error": str(e)[:160]})
        print(u, "ERROR", str(e)[:100])
        continue
    media = acc.get("media", {}).get("data", [])
    likes = [m.get("like_count") or 0 for m in media]
    comm = [m.get("comments_count") or 0 for m in media]
    fol = acc.get("followers_count") or 0
    ts = [datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00")) for m in media]
    span = max(1.0, (max(ts) - min(ts)).total_seconds() / 86400) if len(ts) > 1 else 1.0
    fmts = {}
    for m in media:
        fmts[fmt(m)] = fmts.get(fmt(m), 0) + 1
    by_fmt = {k: statistics.median([(m.get("like_count") or 0) for m in media if fmt(m) == k]) for k in fmts}
    best = sorted(media, key=lambda m: (m.get("like_count") or 0) + 3 * (m.get("comments_count") or 0), reverse=True)[:5]
    row = {"username": u, "followers": fol, "posts_checked": len(media),
           "median_likes": statistics.median(likes) if likes else 0, "median_comments": statistics.median(comm) if comm else 0,
           "engagement_pct": round(100 * (statistics.median(likes) + statistics.median(comm)) / fol, 2) if fol and likes else None,
           "posts_per_week": round(7 * len(media) / span, 1), "formats": fmts, "median_likes_by_format": by_fmt,
           "latest_post": max(ts).date().isoformat() if ts else None,
           "best": [{"format": fmt(m), "likes": m.get("like_count"), "comments": m.get("comments_count"), "views": m.get("view_count"),
                     "date": m["timestamp"][:10], "caption_start": (m.get("caption") or "").split("\n")[0][:160], "url": m.get("permalink")}
                    for m in best]}
    out.append(row)
    print(u, fol, row["median_likes"], row["engagement_pct"], row["posts_per_week"], fmts)
path = ROOT / "data" / "instagram" / f"lookup-{datetime.now(timezone.utc).date().isoformat()}.json"
path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
