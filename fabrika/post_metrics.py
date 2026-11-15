"""Collect Buffer's per-post metrics for Instagram and TikTok (views, likes, comments, shares...).

Usage: python fabrika/post_metrics.py   -> data/metrics/<date>.json
Reads every published/*.json of the last 30 days and asks Buffer for each post's metrics
(TikTok numbers are not available anywhere else). Read-only: publishes nothing.
Also writes data/metrics/latest.md: a short "what worked" ranking the daily run reads before writing.
"""
import json, os, statistics
from datetime import date, datetime, timedelta
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
Q = "query($id: PostId!) { post(input: {id: $id}) { metrics { type name value unit } metricsUpdatedAt } }"


def buffer(variables):
    r = requests.post("https://api.buffer.com", json={"query": Q, "variables": variables},
                      headers={"Authorization": f"Bearer {os.environ['BUFFER_API_KEY']}"}, timeout=60)
    return r.json()


def _n(row, svc, key):
    return (row.get(svc) or {}).get(key) or 0


def summary(rows, now=None):
    """Markdown ranking of our own posts: what won, what lost, the usual level per format.
    Posts younger than 20 hours are listed apart: their numbers are not final."""
    now = now or datetime.now()
    old, new = [], []
    for r in rows:
        try:
            t = datetime.fromisoformat(f"{r['date']}T{r.get('time') or '12:00'}")
        except ValueError:
            t = now - timedelta(days=2)
        (old if now - t > timedelta(hours=20) else new).append(r)

    def line(r):
        kind = (r.get("style") or "?") + ("/" + r["engine"] if r.get("engine") else "")
        first = " ".join((r.get("first_line") or "").split())[:90]
        return (f"- {r['date']} {r.get('time') or ''} {kind}: TikTok {_n(r, 'tiktok', 'views')} views, "
                f"{_n(r, 'tiktok', 'shares')} shares, {_n(r, 'tiktok', 'averageTimeWatched')} s avg | "
                f"Instagram {_n(r, 'instagram', 'reach')} reach, {_n(r, 'instagram', 'shares')} shares, "
                f"{_n(r, 'instagram', 'saves')} saves | \"{first}\"")

    tt = [_n(r, "tiktok", "views") for r in old if r.get("tiktok")]
    base = statistics.median(tt) if tt else 0
    ranked = sorted([r for r in old if r.get("tiktok")], key=lambda r: _n(r, "tiktok", "views"), reverse=True)
    recent = [r for r in ranked if (now.date() - date.fromisoformat(r["date"])).days <= 5]
    ig = sorted([r for r in old if r.get("instagram")], key=lambda r: _n(r, "instagram", "reach"), reverse=True)
    out = [f"# What worked (our own numbers, {now.date().isoformat()})", "",
           "Written automatically by fabrika/post_metrics.py every morning. Read it before writing posts:",
           "build on the winners (same kind of hook and topic, new angle), and do not repeat what sits at the bottom.",
           f"The usual TikTok level (median) is {base:.0f} views: a post is a winner only when it is several times above it.", "",
           "## TikTok winners (do more like these)"]
    out += [line(r) for r in ranked[:8]]
    out += ["", "## TikTok weakest of the last 5 days (do not repeat this kind of hook or topic)"]
    out += [line(r) for r in recent[-8:]]
    out += ["", "## Instagram top 5 by reach"]
    out += [line(r) for r in ig[:5]]
    out += ["", "## Usual level per format (median)"]
    groups = {}
    for r in old:
        groups.setdefault((r.get("style") or "?") + ("/" + r["engine"] if r.get("engine") else ""), []).append(r)
    for k, v in sorted(groups.items()):
        out.append(f"- {k} ({len(v)} posts): TikTok {statistics.median([_n(r, 'tiktok', 'views') for r in v]):.0f} views "
                   f"(best {max(_n(r, 'tiktok', 'views') for r in v)}), "
                   f"Instagram {statistics.median([_n(r, 'instagram', 'reach') for r in v]):.0f} reach")
    if new:
        out += ["", "## Too new to judge (under 20 hours)"] + [line(r) for r in new]
    return "\n".join(out) + "\n"


def main():
    since = date.today() - timedelta(days=30)
    out = []
    for f in sorted((ROOT / "published").glob("*.json")):
        try:
            d = date.fromisoformat(f.stem)
        except ValueError:
            continue
        if d < since:
            continue
        queue = ROOT / "queue" / f.name
        posts = {p["id"]: p for p in json.loads(queue.read_text(encoding="utf-8"))["posts"]} if queue.exists() else {}
        for pid, rec in json.loads(f.read_text(encoding="utf-8")).items():
            p = posts.get(pid, {})
            first = (p.get("slides") or p.get("beats") or [{}])[0]
            row = {"date": f.stem, "id": pid, "time": p.get("time"), "style": p.get("style"), "engine": p.get("engine"),
                   "first_line": (first.get("text") or first.get("title") or first.get("quote") or first.get("big") or "")[:120]}
            for svc, ent in (("instagram", rec), ("tiktok", rec.get("tiktok") or {})):
                bid = ent.get("buffer_id")
                if not bid:
                    continue
                res = buffer({"id": bid})
                post = (res.get("data") or {}).get("post") or {}
                row[svc] = {m["type"]: m["value"] for m in (post.get("metrics") or [])}
                if res.get("errors"):
                    row[svc + "_error"] = json.dumps(res["errors"])[:200]
            out.append(row)
            print(row["date"], pid, row.get("style"), "IG", row.get("instagram"), "TT", row.get("tiktok"))
    path = ROOT / "data" / "metrics" / f"{date.today().isoformat()}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (path.parent / "latest.md").write_text(summary(out), encoding="utf-8")


if __name__ == "__main__":
    main()
