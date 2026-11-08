"""Daily Instagram report: what's working for other pages in the niche, and for us.

Uses Meta's Business Discovery (public data of other professional accounts)
and our own media insights. Needs secret META_PAGE_TOKEN (a never-expiring
Page token for the Facebook Page linked to @suksesishqip).

Writes data/instagram/<date>.json:
  outliers    posts from the last 7 days that did far better than their
              account's usual (engagement / account median)
  formats     how Reels, carousels and single images perform vs. usual
  hashtags    hashtags used most on outlier posts
  own_posts   our recent posts with reach, saves, shares, views
  watchlist   accounts checked, with follower counts or the error
"""
import json, os, re, statistics, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import requests

ROOT = Path(__file__).resolve().parent.parent
GRAPH = "https://graph.facebook.com/v23.0"
TOKEN = os.environ["META_PAGE_TOKEN"]
WATCHLIST = ROOT / "data" / "instagram_watchlist.txt"
HASHTAG = re.compile(r"#([\wëçËÇ]+)", re.UNICODE)


def api(path, **params):
    r = requests.get(f"{GRAPH}/{path}", params={**params, "access_token": TOKEN}, timeout=60)
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("message", "unknown error"))
    return data


def our_account():
    d = api("me", fields="instagram_business_account{id,username,followers_count}")
    ig = d.get("instagram_business_account")
    if not ig:
        raise RuntimeError("the Page has no linked Instagram professional account")
    return ig


MEDIA_FIELDS = "id,caption,like_count,comments_count,view_count,media_type,media_product_type,timestamp,permalink"


def discover(ig_id, username):
    for fields in (MEDIA_FIELDS, MEDIA_FIELDS.replace("view_count,", "")):
        try:
            q = f"business_discovery.username({username}){{username,followers_count,media.limit(30){{{fields}}}}}"
            return api(ig_id, fields=q)["business_discovery"]
        except RuntimeError as e:
            last = e
    raise last


def fmt(m):
    if m.get("media_product_type") == "REELS":
        return "reel"
    return {"CAROUSEL_ALBUM": "carousel", "IMAGE": "image", "VIDEO": "video"}.get(m.get("media_type"), "other")


def score_posts(acc, now):
    media = acc.get("media", {}).get("data", [])
    eng = lambda m: (m.get("like_count") or 0) + 3 * (m.get("comments_count") or 0)
    vals = [eng(m) for m in media]
    if len(vals) < 5:
        return []
    med = max(1, statistics.median(vals))
    out = []
    for m in media:
        ts = datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00"))
        out.append({
            "account": acc["username"], "followers": acc.get("followers_count"),
            "format": fmt(m), "age_days": round((now - ts).total_seconds() / 86400, 1),
            "likes": m.get("like_count"), "comments": m.get("comments_count"), "views": m.get("view_count"),
            "score": round(eng(m) / med, 2),
            "caption_start": (m.get("caption") or "").split("\n")[0][:140],
            "hashtags": sorted({h.lower() for h in HASHTAG.findall(m.get("caption") or "")}),
            "url": m.get("permalink"),
        })
    return out


def own_posts(ig_id):
    media = api(f"{ig_id}/media", fields="id,caption,timestamp,media_type,media_product_type,like_count,comments_count,permalink", limit=20).get("data", [])
    rows = []
    for m in media:
        row = {"format": fmt(m), "posted": m["timestamp"], "likes": m.get("like_count"),
               "comments": m.get("comments_count"), "caption_start": (m.get("caption") or "").split("\n")[0][:120],
               "url": m.get("permalink")}
        for metric in ("reach,saved,shares,views,total_interactions", "reach,saved,shares,total_interactions"):
            try:
                ins = api(f"{m['id']}/insights", metric=metric).get("data", [])
                for x in ins:
                    row[x["name"]] = (x.get("values") or [{}])[0].get("value", x.get("total_value", {}).get("value"))
                break
            except RuntimeError as e:
                row["insights_error"] = str(e)[:120]
        rows.append(row)
    return rows


def main():
    now = datetime.now(timezone.utc)
    me = our_account()
    ig_id = me["id"]
    names = [l.strip().lstrip("@") for l in WATCHLIST.read_text().splitlines()
             if l.strip() and not l.startswith("#")]
    watch, posts = [], []
    for u in names:
        try:
            acc = discover(ig_id, u)
            watch.append({"username": u, "followers": acc.get("followers_count")})
            posts += score_posts(acc, now)
        except RuntimeError as e:
            watch.append({"username": u, "error": str(e)[:160]})
            print(f"skip {u}: {e}", file=sys.stderr)

    recent = [p for p in posts if p["age_days"] <= 7]
    outliers = sorted([p for p in recent if p["score"] >= 1.5], key=lambda p: p["score"], reverse=True)[:40]

    formats = {}
    for p in posts:
        formats.setdefault(p["format"], []).append(p["score"])
    format_stats = {f: {"posts": len(v), "median_score": round(statistics.median(v), 2),
                        "share_of_outliers": round(sum(1 for o in outliers if o["format"] == f) / max(1, len(outliers)), 2)}
                    for f, v in formats.items()}

    tags = {}
    for p in outliers:
        for h in p["hashtags"]:
            tags[h] = tags.get(h, 0) + 1
    hashtag_stats = sorted(tags.items(), key=lambda kv: kv[1], reverse=True)[:30]

    try:
        own = own_posts(ig_id)
    except RuntimeError as e:
        own = [{"error": str(e)[:200]}]

    date = now.astimezone(ZoneInfo("Europe/Tirane")).strftime("%Y-%m-%d")
    out = ROOT / "data" / "instagram" / f"{date}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "date": date, "our_account": {"username": me.get("username"), "followers": me.get("followers_count")},
        "outliers": outliers, "formats": format_stats,
        "hashtags_on_outliers": [{"tag": t, "count": c} for t, c in hashtag_stats],
        "own_posts": own, "watchlist": watch,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for w in watch if "error" not in w)
    print(f"{ok}/{len(watch)} accounts read, {len(outliers)} outliers, {len(own)} own posts")


if __name__ == "__main__":
    main()
