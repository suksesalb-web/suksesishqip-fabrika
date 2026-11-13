"""Collect Buffer's per-post metrics for Instagram and TikTok (views, likes, comments, shares...).

Usage: python fabrika/post_metrics.py   -> data/metrics/<date>.json
Reads every published/*.json of the last 30 days and asks Buffer for each post's metrics
(TikTok numbers are not available anywhere else). Read-only: publishes nothing.
"""
import json, os
from datetime import date, timedelta
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
Q = "query($id: PostId!) { post(input: {id: $id}) { metrics { type name value unit } metricsUpdatedAt } }"


def buffer(variables):
    r = requests.post("https://api.buffer.com", json={"query": Q, "variables": variables},
                      headers={"Authorization": f"Bearer {os.environ['BUFFER_API_KEY']}"}, timeout=60)
    return r.json()


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


if __name__ == "__main__":
    main()
