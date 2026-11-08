"""Daily YouTube trend report for the niche.

Finds the most-watched short videos of the last 48 hours for each niche
search, ranks them by views per hour, and writes data/trends/<date>.json.
Cost: ~100 quota units per search + 1 per 50 videos (well under 10,000/day).
"""
import json, os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import requests

ROOT = Path(__file__).resolve().parent.parent
API = "https://www.googleapis.com/youtube/v3"
KEY = os.environ["YOUTUBE_API_KEY"]

SEARCHES = [
    "motivation", "discipline", "self improvement", "mindset",
    "side hustle", "make money", "personal finance tips",
    "stoicism", "success story", "entrepreneur advice",
]


def get(path, **params):
    r = requests.get(f"{API}/{path}", params={**params, "key": KEY}, timeout=30)
    r.raise_for_status()
    return r.json()


def main():
    now = datetime.now(timezone.utc)
    since = (now - timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ")
    found = {}
    for q in SEARCHES:
        res = get("search", part="snippet", q=q, type="video", order="viewCount",
                  publishedAfter=since, videoDuration="short", maxResults=25,
                  relevanceLanguage="en", safeSearch="strict")
        for it in res.get("items", []):
            vid = it["id"]["videoId"]
            found.setdefault(vid, {"query": q, "title": it["snippet"]["title"],
                                   "channel": it["snippet"]["channelTitle"],
                                   "published": it["snippet"]["publishedAt"]})
    ids = list(found)
    for i in range(0, len(ids), 50):
        res = get("videos", part="statistics", id=",".join(ids[i:i + 50]))
        for it in res.get("items", []):
            st = it.get("statistics", {})
            v = found[it["id"]]
            v["views"] = int(st.get("viewCount", 0))
            v["likes"] = int(st.get("likeCount", 0)) if "likeCount" in st else None
            v["comments"] = int(st.get("commentCount", 0)) if "commentCount" in st else None
    rows = []
    for vid, v in found.items():
        if "views" not in v:
            continue
        pub = datetime.fromisoformat(v["published"].replace("Z", "+00:00"))
        hours = max(1.0, (now - pub).total_seconds() / 3600)
        rows.append({**v, "hours_live": round(hours, 1), "views_per_hour": round(v["views"] / hours),
                     "url": f"https://www.youtube.com/shorts/{vid}"})
    rows.sort(key=lambda r: r["views_per_hour"], reverse=True)
    date = now.astimezone(ZoneInfo("Europe/Tirane")).strftime("%Y-%m-%d")
    out = ROOT / "data" / "trends" / f"{date}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"date": date, "source": "youtube", "window_hours": 48,
                               "searches": SEARCHES, "top": rows[:60]},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(rows)} videos, top: {rows[0]['title'] if rows else '-'}")


if __name__ == "__main__":
    main()
