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


def instagram_channel():
    orgs = gql("query { account { organizations { id name } } }")["account"]["organizations"]
    for org in orgs:
        chans = gql("query($o: OrganizationId!) { channels(input: {organizationId: $o}) { id name service } }",
                    {"o": org["id"]})["channels"]
        for c in chans:
            if c["service"].lower() == "instagram":
                return c["id"], c["name"]
    raise RuntimeError("no Instagram channel connected in Buffer")


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

    channel_id, channel_name = instagram_channel()
    print(f"Instagram channel: {channel_name}")
    now = datetime.now(timezone.utc)
    failed = False
    late = 0
    for pid in ap["approve"]:
        if published.get(pid, {}).get("buffer_id"):
            print(pid, "already published, skipping")
            continue
        post, m = queue[pid], manifest[pid]
        if m["status"] != "rendered":
            print(pid, "not rendered, skipping")
            continue
        urls = [f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{f}" for f in m["files"]]
        local = datetime.fromisoformat(f"{date}T{post['time']}").replace(tzinfo=TZ)
        due = local.astimezone(timezone.utc)
        if post.get("style") == "reel":
            video = next(u for u in urls if u.endswith(".mp4"))
            urls = [video]
            assets = [{"video": {"url": video, "metadata": {"thumbnailOffset": 0}}}]
            ig = {"type": "reel", "shouldShareToFeed": True}
        else:
            first = post["slides"][0]
            alt = first.get("text") or first.get("title") or first.get("quote", "")
            assets = [{"image": {"url": u, "metadata": {"altText": alt}}} for u in urls]
            ig = {"type": "post", "shouldShareToFeed": True}
        inp = {
            "text": post["caption"] + (REEL_CREDIT if post.get("style") == "reel" else CREDIT),
            "channelId": channel_id,
            "schedulingType": "automatic",
            "assets": assets,
            "metadata": {"instagram": ig},
        }
        if pid in ap.get("now", []):
            inp["mode"] = "shareNow"
        elif due > now + timedelta(minutes=5):
            inp["mode"] = "customScheduled"
            inp["dueAt"] = due.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        else:
            # Its slot already passed (late run): post soon, spaced 20 min apart.
            late += 1
            inp["mode"] = "customScheduled"
            inp["dueAt"] = (now + timedelta(minutes=5 + 20 * (late - 1))).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        try:
            res = gql(CREATE, {"input": inp})["createPost"]
        except RuntimeError as e:
            if inp["mode"] != "shareNow":
                raise
            print(pid, "shareNow not accepted, scheduling in 3 minutes instead:", e)
            inp["mode"] = "customScheduled"
            inp["dueAt"] = (now + timedelta(minutes=3)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            res = gql(CREATE, {"input": inp})["createPost"]
        if "post" in res:
            published[pid] = {"buffer_id": res["post"]["id"], "dueAt": res["post"]["dueAt"], "images": len(urls)}
            print(pid, "scheduled for", res["post"]["dueAt"])
        else:
            published[pid] = {"error": res.get("message")}
            print(pid, "FAILED:", res.get("message"))
            failed = True
    pub_path.parent.mkdir(exist_ok=True)
    pub_path.write_text(json.dumps(published, ensure_ascii=False, indent=2), encoding="utf-8")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1])
