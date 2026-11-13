"""Read-only health check: what Buffer says about today's posts, and what is live on Instagram.
Publishes nothing. Usage: python fabrika/status.py 2026-11-08"""
import json, os, sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
date = sys.argv[1]
pub = json.loads((ROOT / "published" / f"{date}.json").read_text())


def buffer(query, variables):
    r = requests.post("https://api.buffer.com", json={"query": query, "variables": variables},
                      headers={"Authorization": f"Bearer {os.environ['BUFFER_API_KEY']}"}, timeout=60)
    return r.json()


QUERIES = [
    "query($id: PostId!) { post(input: {id: $id}) { id status dueAt sentAt error { message } } }",
    "query($id: PostId!) { post(input: {id: $id}) { id status dueAt sentAt } }",
    "query($id: PostId!) { post(input: {id: $id}) { id status dueAt } }",
]
print("== BUFFER")
for pid, rec in sorted(pub.items()):
    for svc, ent in (("instagram", rec), ("tiktok", rec.get("tiktok") or {})):
        bid = ent.get("buffer_id")
        if not bid:
            continue
        for q in QUERIES:
            d = buffer(q, {"id": bid})
            if "errors" not in d:
                print(pid, svc, json.dumps(d["data"]["post"], ensure_ascii=False))
                break
        else:
            print(pid, svc, "query error:", json.dumps(d.get("errors"))[:300])

print("== INSTAGRAM (live)")
tok = os.environ.get("META_PAGE_TOKEN")
if tok:
    g = "https://graph.facebook.com/v27.0"
    me = requests.get(f"{g}/me", params={"fields": "instagram_business_account{id,username,followers_count,media_count}",
                                         "access_token": tok}, timeout=30).json()
    ig = me.get("instagram_business_account", {})
    print("account:", {k: ig.get(k) for k in ("username", "followers_count", "media_count")})
    media = requests.get(f"{g}/{ig.get('id')}/media", params={
        "fields": "timestamp,media_type,media_product_type,like_count,comments_count,caption,permalink",
        "limit": 15, "access_token": tok}, timeout=30).json()
    for m in media.get("data", []):
        print(m["timestamp"], m.get("media_product_type"), m.get("media_type"), "likes", m.get("like_count"),
              "|", (m.get("caption") or "").split("\n")[0][:60], "|", m.get("permalink"))
    if "error" in media:
        print("error:", media["error"].get("message"))

print("== BUFFER SCHEMA (analytics fields)")
try:
    d = buffer("{ __schema { types { name fields { name } } } }", {})
    for t in d["data"]["__schema"]["types"]:
        names = [f["name"] for f in (t.get("fields") or [])]
        hit = [n for n in names if any(k in n.lower() for k in ("stat", "metric", "analytic", "insight", "engagement", "view", "impression"))]
        if t["name"] in ("Post",) or hit:
            print(t["name"], hit if hit else names[:40])
except Exception as e:
    print("schema error:", e)
