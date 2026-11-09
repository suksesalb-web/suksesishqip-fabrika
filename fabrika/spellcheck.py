"""Albanian spellcheck for every piece of text in a queue file.

Usage: python fabrika/spellcheck.py queue/2026-11-08.json
Exits with code 1 and lists unknown words if anything fails.
Proper names and other words the dictionary doesn't know go in
fabrika/dict/allowlist.txt (one word per line).
"""
import json, re, sys
from pathlib import Path
from spylls.hunspell import Dictionary

HERE = Path(__file__).parent
WORD = re.compile(r"[A-Za-zËëÇç]+(?:[-'][A-Za-zËëÇç]+)?")

# Words that exist in the dictionary but are almost always a missing-ë typo
# in this page's writing. "te"/"ne"/"se" etc. are real words, so the
# dictionary can't catch them; these rules can.
SUSPICIOUS = {
    "eshte": "është", "per": "për", "shume": "shumë",
    "kohe": "kohë", "dite": "ditë", "jete": "jetë", "mire": "mirë",
    "nje": "një", "c'do": "çdo", "cdo": "çdo", "eshtë": "është",
}


def load_allow():
    p = HERE / "dict" / "allowlist.txt"
    if not p.exists():
        return set()
    return {l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}


def texts_of(post):
    out = [post.get("caption", "")]
    for s in post.get("slides", []) + post.get("beats", []):
        out += [str(v) for k, v in s.items() if isinstance(v, str) and k not in ("video_query", "video_id", "photo_query", "type")]
        out += [str(x) for x in s.get("items", [])]
        for side in ("left", "right"):
            if isinstance(s.get(side), dict):
                out += [s[side].get("label", "")] + [str(x) for x in s[side].get("items", [])]
    return out


def check_text(d, allow, text):
    import re
    text = re.sub(r"<[^>]+>", " ", text)  # voice expression tags like <breath>
    bad = []
    for w in WORD.findall(text):
        if "-" in w:  # "Potter-it": check the name, the case ending is fine
            w = w.split("-")[0]
        if w in allow or w.lower() in allow or w.isdigit():
            continue
        if w.lower() in SUSPICIOUS:
            bad.append(f"{w} (→ {SUSPICIOUS[w.lower()]}?)")
        elif not d.lookup(w):
            bad.append(w)
    return bad


def main(path):
    d = Dictionary.from_files(str(HERE / "dict" / "sq_AL"))
    allow = load_allow()
    q = json.loads(Path(path).read_text(encoding="utf-8"))
    problems = {}
    for p in q["posts"]:
        bad = []
        for t in texts_of(p):
            bad += check_text(d, allow, t)
        if bad:
            problems[p["id"]] = sorted(set(bad))
    if problems:
        print("SPELLCHECK FAILED:")
        for k, v in problems.items():
            print(f"  {k}: {', '.join(v)}")
        sys.exit(1)
    print(f"Spellcheck OK ({len(q['posts'])} posts)")


if __name__ == "__main__":
    main(sys.argv[1])
