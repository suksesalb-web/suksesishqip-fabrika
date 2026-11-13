"""Remove scheduled posts from Buffer (Instagram and TikTok) so a slot can be replaced.

Usage: python fabrika/unpublish.py 2026-11-13 p3,p4
Deletes the Buffer posts recorded in published/<date>.json for those ids and drops the ids from
that file, so publish.py will send the new versions. Posts that already went out can't be removed.
"""
import json, os, sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.buffer.com"


def gql(query, variables=None):
    r = requests.post(API, json={"query": query, "variables": variables or {}},
                      headers={"Authorization": f"Bearer {os.environ['BUFFER_API_KEY']}"}, timeout=60)
    r.raise_for_status()
    return r.json()


def delete_mutation():
    """Find Buffer's delete mutation and its argument shape by introspection."""
    d = gql("{ __schema { mutationType { fields { name args { name type { name kind ofType { name kind } } } } } } }")
    fields = d["data"]["__schema"]["mutationType"]["fields"]
    names = [f["name"] for f in fields]
    print("mutations:", [n for n in names if "elete" in n or "emove" in n])
    f = next((f for f in fields if f["name"] == "deletePost"), None)
    if not f:
        raise RuntimeError("no deletePost mutation; available: " + ", ".join(names))
    arg = f["args"][0]
    tname = arg["type"].get("name") or (arg["type"].get("ofType") or {}).get("name")
    return f["name"], arg["name"], tname


def main(date, ids):
    pub_path = ROOT / "published" / f"{date}.json"
    published = json.loads(pub_path.read_text(encoding="utf-8"))
    name, argname, tname = delete_mutation()
    print("using", name, argname, tname)
    if tname and tname.endswith("Input"):
        q = f"mutation($v: {tname}!) {{ {name}({argname}: $v) {{ __typename }} }}"
        mk = lambda pid: {"id": pid}
    else:
        q = f"mutation($v: {tname}!) {{ {name}({argname}: $v) {{ __typename }} }}"
        mk = lambda pid: pid
    failed = False
    for pid in ids:
        rec = published.get(pid)
        if not rec:
            print(pid, "not in published log, nothing to delete")
            continue
        for svc, ent in (("instagram", rec), ("tiktok", rec.get("tiktok") or {})):
            bid = ent.get("buffer_id")
            if not bid:
                continue
            res = gql(q, {"v": mk(bid)})
            ok = not res.get("errors") and "Error" not in json.dumps(res.get("data", {}))
            print(pid, svc, bid, "deleted" if ok else "FAILED", json.dumps(res, ensure_ascii=False)[:300])
            failed |= not ok
        if not failed:
            published.pop(pid)
    pub_path.write_text(json.dumps(published, ensure_ascii=False, indent=2), encoding="utf-8")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1], [x.strip() for x in sys.argv[2].split(",") if x.strip()])
