"""Send approved posts to Buffer.

Usage: python fabrika/publish.py approved/2026-11-08.json
approved file: {"date": "2026-11-08", "approve": ["p1", "p3"], "now": ["p1"]}
("now" is optional: those ids publish immediately instead of at their time.)

Images are taken from out/<date>/manifest.json and passed to Buffer as
raw.githubusercontent.com URLs (the repo is public, so Buffer can fetch them).
Already-published ids (published/<date>.json) are skipped, so re-running is safe.
"""
import json, os, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import requests

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.buffer.com"
TZ = ZoneInfo("Europe/Tirane")
REPO = os.environ.get("GITHUB_REPOSITORY", "suksesalb-web/suksesishqip-fabrika")
BRANCH = os.environ.get("BRANCH", "main")
CREDIT = "\n\n📷 Pixabay"
REEL_CREDIT = "\n\n🎬🎵 Pixabay"


def gql(query, variables=None):
    r = requests.post(API, json={"query": query, "variables": variables or {}},
                      headers={"Authorization": f"Bearer {os.environ['BUFFER_API_KEY']}"}, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"], ensure_ascii=False))
    return data["data"]


def channels():
    """All connected Buffer channels by service: {"instagram": (id, name), "tiktok": (id, name), ...}"""
    out = {}
    orgs = gql("query { account { organizations { id name } } }")["account"]["organizations"]
    for org in orgs:
        chans = gql("query($o: OrganizationId!) { channels(input: {organizationId: $o}) { id name service } }",
                    {"o": org["id"]})["channels"]
        for c in chans:
            out.setdefault(c["service"].lower(), (c["id"], c["name"]))
    if "instagram" not in out:
        raise RuntimeError("no Instagram channel connected in Buffer")
    return out


CREATE = """
mutation($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess { post { id dueAt } }
    ... on MutationError { message }
  }
}
"""


def main(path):
    ap = json.loads(Path(path).read_text(encoding="utf-8"))
    date = ap["date"]
    queue = {p["id"]: p for p in json.loads((ROOT / "queue" / f"{date}.json").read_text(encoding="utf-8"))["posts"]}
    manifest = {p["id"]: p for p in json.loads((ROOT / "out" / date / "manifest.json").read_text(encoding="utf-8"))["posts"]}
    pub_path = ROOT / "published" / f"{date}.json"
    published = json.loads(pub_path.read_text(encoding="utf-8")) if pub_path.exists() else {}

    chans = channels()
    print("Buffer channels:", {k: v[1] for k, v in chans.items()})
    now = datetime.now(timezone.utc)
    failed = False
    late = 0
    for pid in ap["approve"]:
        post, m = queue[pid], manifest[pid]
        if m["status"] != "rendered":
            print(pid, "not rendered, skipping")
            continue
        is_reel = post.get("style") == "reel"
        # Every post goes to Instagram and TikTok (Reels as video, image posts as TikTok photo carousels).
        targets = ["instagram"] + (["tiktok"] if "tiktok" in chans else [])
        rec = published.get(pid, {})
        urls = [f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{f}" for f in m["files"]]
        if is_reel:
            urls = [next(u for u in urls if u.endswith(".mp4"))]
        local = datetime.fromisoformat(f"{date}T{post['time']}").replace(tzinfo=TZ)
        due = local.astimezone(timezone.utc)
        if pid in ap.get("now", []):
            when = {"mode": "shareNow"}
        elif due > now + timedelta(minutes=5):
            when = {"mode": "customScheduled", "dueAt": due.strftime("%Y-%m-%dT%H:%M:%S.000Z")}
        else:  # its slot already passed (late run): post soon, spaced 20 min apart
            late += 1
            when = {"mode": "customScheduled",
                    "dueAt": (now + timedelta(minutes=5 + 20 * (late - 1))).strftime("%Y-%m-%dT%H:%M:%S.000Z")}
        for svc in targets:
            done = rec.get("buffer_id") if svc == "instagram" else rec.get(svc, {}).get("buffer_id")
            if done:
                print(pid, svc, "already published, skipping")
                continue
            if is_reel:
                assets = [{"video": {"url": urls[0], "metadata": {"thumbnailOffset": 0}}}]
            else:
                first = post["slides"][0]
                alt = first.get("text") or first.get("title") or first.get("quote", "")
                assets = [{"image": {"url": u, "metadata": {"altText": alt}}} for u in urls]
            inp = {
                "text": post["caption"] + (REEL_CREDIT if is_reel else CREDIT),
                "channelId": chans[svc][0],
                "schedulingType": "automatic",
                "assets": assets,
                **when,
            }
            if svc == "instagram":
                inp["metadata"] = {"instagram": {"type": "reel" if is_reel else "post", "shouldShareToFeed": True}}
            try:
                res = gql(CREATE, {"input": inp})["createPost"]
            except RuntimeError as e:
                if inp["mode"] != "shareNow":
                    print(pid, svc, "FAILED:", e)
                    res = {"message": str(e)}
                else:
                    print(pid, svc, "shareNow not accepted, scheduling in 3 minutes instead:", e)
                    inp["mode"] = "customScheduled"
                    inp["dueAt"] = (now + timedelta(minutes=3)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
                    res = gql(CREATE, {"input": inp})["createPost"]
            if "post" in res:
                entry = {"buffer_id": res["post"]["id"], "dueAt": res["post"]["dueAt"], "images": len(urls)}
                print(pid, svc, "scheduled for", res["post"]["dueAt"])
            else:
                entry = {"error": res.get("message")}
                print(pid, svc, "FAILED:", res.get("message"))
                failed = True
            if svc == "instagram":
                rec.update(entry)
            else:
                rec[svc] = entry
        published[pid] = rec
    pub_path.parent.mkdir(exist_ok=True)
    pub_path.write_text(json.dumps(published, ensure_ascii=False, indent=2), encoding="utf-8")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1])
