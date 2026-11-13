"""Render every post in a queue file into Instagram-ready JPGs.

Usage:
  python fabrika/render.py queue/2026-11-08.json            # fetch photos from Pixabay
  python fabrika/render.py queue/2026-11-08.json --offline  # placeholder backgrounds

Output: out/<date>/<post_id>/01.jpg, 02.jpg ... and out/<date>/manifest.json
"""
import io, json, os, random, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "fabrika"
FONTS = HERE / "fonts"
W, H = 1080, 1350
PAD = 90
GOLD = (212, 175, 55)
WHITE = (255, 255, 255)
SOFT = (225, 225, 225)
GREY = (165, 165, 165)
INK = (12, 12, 12)
HANDLE = "@suksesishqip"
USED = ROOT / "data" / "used_photos.txt"


def font(name, size):
    return ImageFont.truetype(str(FONTS / f"{name}.ttf"), size)


# ---------- photos ----------

def pixabay_by_id(pid):
    import requests
    r = requests.get("https://pixabay.com/api/", params=dict(key=os.environ["PIXABAY_API_KEY"], id=pid), timeout=30)
    r.raise_for_status()
    h = r.json()["hits"][0]
    img = requests.get(h["largeImageURL"], timeout=60)
    img.raise_for_status()
    return Image.open(io.BytesIO(img.content)).convert("RGB"), str(h["id"]), h.get("pageURL", "")


def pixabay_photo(query, used):
    import requests
    key = os.environ["PIXABAY_API_KEY"]
    params = dict(key=key, q=query, image_type="photo", orientation="vertical",
                  safesearch="true", per_page=50, min_width=1080, min_height=1350,
                  order="popular")
    r = requests.get("https://pixabay.com/api/", params=params, timeout=30)
    r.raise_for_status()
    hits = [h for h in r.json().get("hits", []) if str(h["id"]) not in used]
    if not hits:  # widen: allow horizontal photos too
        params["orientation"] = "all"
        r = requests.get("https://pixabay.com/api/", params=params, timeout=30)
        r.raise_for_status()
        hits = [h for h in r.json().get("hits", []) if str(h["id"]) not in used]
    if not hits:
        raise RuntimeError(f"no unused Pixabay photo for '{query}'")
    h = random.choice(hits[:6])
    img = requests.get(h["largeImageURL"], timeout=60)
    img.raise_for_status()
    return Image.open(io.BytesIO(img.content)).convert("RGB"), str(h["id"]), h.get("pageURL", "")


def placeholder_photo(seed):
    rnd = random.Random(seed)
    base = Image.new("RGB", (W, H), (rnd.randint(20, 60), rnd.randint(20, 50), rnd.randint(20, 40)))
    d = ImageDraw.Draw(base)
    for _ in range(6):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(150, 450)
        c = tuple(rnd.randint(60, 160) for _ in range(3))
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    return base.filter(ImageFilter.GaussianBlur(90))


def fill(img):
    return ImageOps.fit(img, (W, H), method=Image.LANCZOS, centering=(0.5, 0.4))


def darken(img, amount):
    return Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), amount)


def gradient(img, start, strength):
    """Darken from y=start down to the bottom, up to `strength` (0-1)."""
    g = Image.new("L", (1, H), 0)
    for y in range(H):
        t = 0 if y < start else (y - start) / (H - start)
        g.putpixel((0, y), int(255 * strength * min(1, t * 1.4)))
    mask = g.resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, mask)


# ---------- text helpers ----------

def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
            continue
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit(d, text, name, start, minsize, maxw, maxh, lh=1.22):
    """Largest font size (<= start) whose wrapped text fits maxw x maxh."""
    for size in range(start, minsize - 1, -2):
        f = font(name, size)
        lines = wrap(d, text, f, maxw)
        if any(d.textlength(l, font=f) > maxw for l in lines):
            continue
        step = int(size * lh)
        h = sum(step if l else step // 2 for l in lines)
        if h <= maxh:
            return f, lines, step, h
    raise ValueError(f"text too long to fit: {text[:40]}…")


def draw_lines(d, lines, f, x, y, step, color):
    for l in lines:
        if l:
            d.text((x, y), l, font=f, fill=color)
            y += step
        else:
            y += step // 2
    return y


def footer(d, right=None, color=GOLD):
    f = font("i700", 30)
    d.text((PAD, H - 110), HANDLE, font=f, fill=color)
    if right == "swipe":
        t = "Rrëshqit"
        x = W - PAD - 60 - d.textlength(t, font=f)
        d.text((x, H - 110), t, font=f, fill=WHITE)
        ay = H - 92
        d.line([(W - 140, ay), (W - 96, ay)], fill=WHITE, width=3)
        d.polygon([(W - 90, ay), (W - 104, ay - 9), (W - 104, ay + 9)], fill=WHITE)
    elif right:
        d.text((W - PAD - d.textlength(right, font=f), H - 110), right, font=f, fill=GREY)


def avatar():
    a = Image.open(HERE / "logo.png").convert("RGB").resize((110, 110))
    m = Image.new("L", (110, 110), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 109, 109], fill=255)
    return a, m


# ---------- styles ----------

def s_tweet(photo, s):
    img = gradient(darken(fill(photo), 0.5), 200, 0.95)
    d = ImageDraw.Draw(img)
    f, lines, step, h = fit(d, s["text"], "i400", 64, 40, W - 2 * PAD, 640, 1.35)
    top = H - 190 - h - 150
    a, m = avatar()
    img.paste(a, (PAD, top), m)
    d.text((PAD + 135, top + 18), "Suksesi Shqip", font=font("i700", 40), fill=WHITE)
    d.text((PAD + 135, top + 66), HANDLE, font=font("i400", 32), fill=GREY)
    draw_lines(d, lines, f, PAD, top + 150, step, WHITE)
    return img


def s_statement(photo, s):
    img = darken(fill(photo), 0.62)
    d = ImageDraw.Draw(img)
    main, hl = s["text"], s.get("highlight", "")
    fm, lm, stm, hm = fit(d, main, "i800", 92, 56, W - 2 * PAD, 620, 1.12)
    lh_, sth, hh = [], 0, 0
    if hl:
        size = fm.size
        while True:
            fh = font("i800", size)
            lh_ = wrap(d, hl, fh, W - 2 * PAD - 30)
            if len(lh_) <= 1 or size <= 56:
                break
            size -= 4
        sth = int(fh.size * 1.25)
        hh = sth * len(lh_)
    y = (H - (hm + (50 + hh if hl else 0))) // 2 - 30
    y = draw_lines(d, lm, fm, PAD, y, stm, WHITE)
    if hl:
        y += 50
        for l in lh_:
            b = fh.getbbox(l)
            d.rectangle([PAD - 12, y + b[1] - 14, PAD + d.textlength(l, font=fh) + 14, y + b[3] + 14], fill=GOLD)
            d.text((PAD, y), l, font=fh, fill=INK)
            y += sth
    footer(d)
    return img


def s_quote(photo, s):
    img = gradient(darken(fill(photo), 0.45), 300, 0.92)
    d = ImageDraw.Draw(img)
    f, lines, step, h = fit(d, s["quote"], "s700", 78, 46, W - 2 * PAD, 560, 1.22)
    y = H - 230 - h - 120
    d.text((PAD - 6, y - 150), "“", font=font("s700", 200), fill=GOLD)
    y = draw_lines(d, lines, f, PAD, y, step, WHITE)
    d.rectangle([PAD, y + 30, PAD + 110, y + 35], fill=GOLD)
    d.text((PAD, y + 60), s["author"].upper(), font=font("i700", 32), fill=GOLD)
    if s.get("source"):
        d.text((PAD, y + 104), s["source"], font=font("s600i", 30), fill=GREY)
    footer(d)
    return img


def s_cover(photo, s):
    img = gradient(darken(fill(photo), 0.42), 240, 0.97)
    d = ImageDraw.Draw(img)
    f, lines, step, h = fit(d, s["title"], "s700", 100, 60, W - 2 * PAD, 470, 1.12)
    sub_lines, sstep, sh = [], 0, 0
    if s.get("subtitle"):
        sf, sub_lines, sstep, sh = fit(d, s["subtitle"], "s600i", 50, 36, W - 2 * PAD, 190, 1.3)
    y = H - 190 - sh - 40 - h
    if s.get("kicker"):
        d.text((PAD, y - 80), s["kicker"].upper(), font=font("i700", 30), fill=GOLD)
        d.rectangle([PAD, y - 36, PAD + 80, y - 33], fill=GOLD)
    y = draw_lines(d, lines, f, PAD, y, step, WHITE) + 40
    if sub_lines:
        draw_lines(d, sub_lines, sf, PAD, y, sstep, SOFT)
    footer(d, "swipe")
    return img


def s_slide(photo, s, num, page):
    img = Image.new("RGB", (W, H), (14, 13, 12))
    strip = darken(ImageOps.fit(photo, (W, 300), centering=(0.5, 0.4)).filter(ImageFilter.GaussianBlur(6)), 0.6)
    img.paste(strip, (0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 300, W, 304], fill=GOLD)
    d.text((PAD, 370), f"{num:02d}", font=font("i800", 110), fill=GOLD)
    tf, tl, ts, th = fit(d, s["title"], "i800", 76, 44, W - 2 * PAD, 260, 1.12)
    y = draw_lines(d, tl, tf, PAD, 530, ts, WHITE) + 34
    bf, bl, bs, bh = fit(d, s.get("body", ""), "i400", 54, 32, W - 2 * PAD, H - 200 - y, 1.42)
    draw_lines(d, bl, bf, PAD, y, bs, SOFT)
    footer(d, page)
    return img


def s_cta(photo):
    img = darken(fill(photo), 0.7)
    d = ImageDraw.Draw(img)
    a, m = avatar()
    a, m = a.resize((150, 150)), m.resize((150, 150))
    img.paste(a, ((W - 150) // 2, 380), m)
    def center(t, f, y, c):
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=c)
    center("Ruaje këtë postim.", font("s700", 76), 600, WHITE)
    center("Dërgoja dikujt që i duhet.", font("s600i", 50), 710, SOFT)
    center("Ndiq " + HANDLE, font("i700", 38), 850, GOLD)
    return img


def render_post(post, photo):
    st = post["style"]
    sl = post["slides"]
    if st == "tweet":
        return [s_tweet(photo, sl[0])]
    if st == "statement":
        return [s_statement(photo, sl[0])]
    if st == "quote":
        return [s_quote(photo, sl[0])]
    if st == "story":
        total = len(sl) + 1
        imgs = [s_cover(photo, sl[0])]
        for i, s in enumerate(sl[1:], 1):
            imgs.append(s_slide(photo, s, i, f"{i + 1}/{total}"))
        imgs.append(s_cta(photo))
        return imgs
    raise ValueError(f"unknown style {st}")


def main(path, offline=False):
    q = json.loads(Path(path).read_text(encoding="utf-8"))
    date = q["date"]
    outdir = ROOT / "out" / date
    outdir.mkdir(parents=True, exist_ok=True)
    used = set(USED.read_text().split()) if USED.exists() else set()
    manifest = {"date": date, "rendered_at": int(time.time()), "posts": []}
    old_path = outdir / "manifest.json"
    prev = {e["id"]: e for e in json.loads(old_path.read_text(encoding="utf-8"))["posts"]} if old_path.exists() else {}
    for p in q["posts"]:
        if p.get("keep") and prev.get(p["id"], {}).get("status") == "rendered":  # already published: leave as is
            manifest["posts"].append(prev[p["id"]])
            print(p["id"], "kept")
            continue
        entry = {"id": p["id"], "status": "rendered", "files": [], "photo": None}
        if p.get("style") == "reel":
            try:
                from reel import render_reel
                pdir = outdir / p["id"]
                pdir.mkdir(exist_ok=True)
                for old in list(pdir.glob("*.jpg")) + list(pdir.glob("*.mp4")):
                    old.unlink()
                files, info = render_reel(p, pdir, used, offline)
                entry["files"] = [str(f.relative_to(ROOT)) for f in files]
                entry["reel"] = info
                entry["photo"] = info.get("video")
            except Exception as e:
                entry["status"] = "failed"
                entry["error"] = f"{type(e).__name__}: {e}"
            manifest["posts"].append(entry)
            print(p["id"], entry["status"], entry.get("error", ""))
            continue
        try:
            if offline:
                photo, pid, page = placeholder_photo(p["id"]), None, ""
            elif p.get("photo_query") == "none":  # fallback: plain dark background
                photo = Image.new("RGB", (W, H), (20, 18, 16))
                pid, page = None, ""
            elif p.get("photo_id"):  # locked photo: a reviewer kept it
                photo, pid, page = pixabay_by_id(p["photo_id"])
            else:
                photo, pid, page = pixabay_photo(p["photo_query"], used)
                used.add(pid)
            entry["photo"] = {"pixabay_id": pid, "page": page, "query": p.get("photo_query")}
            pdir = outdir / p["id"]
            pdir.mkdir(exist_ok=True)
            for old in pdir.glob("*.jpg"):
                old.unlink()
            for i, img in enumerate(render_post(p, photo), 1):
                fp = pdir / f"{i:02d}.jpg"
                img.save(fp, "JPEG", quality=92, optimize=True)
                entry["files"].append(str(fp.relative_to(ROOT)))
        except Exception as e:  # one bad post never blocks the others
            entry["status"] = "failed"
            entry["error"] = f"{type(e).__name__}: {e}"
        manifest["posts"].append(entry)
        print(p["id"], entry["status"], entry.get("error", ""))
    (outdir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if not offline:
        USED.parent.mkdir(exist_ok=True)
        USED.write_text("\n".join(sorted(used)) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], offline="--offline" in sys.argv)
