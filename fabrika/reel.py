"""Render a Reel: stock footage + Albanian text beats + Albanian voice (+ music).

Queue entry (style "reel"):
  {"id": "p2", "style": "reel", "time": "12:00",
   "video_query": "man walking alone city street night",
   "voice": "sq-AL-AnilaNeural",            # or "none"
   "music": "auto",                          # a file in fabrika/music/, "auto" or "none"
   "beats": [{"text": "...", "highlight": "..."}, ...],   # 3-6 beats, first one is the hook
   "captions": "words",                      # "words": word-by-word captions after the hook
                                             # "beats" (default for now): each beat's full text on screen
   "caption": "..."}

Each beat is on screen while the voice reads it (beats without voice: ~3 s each).
Output: out/<date>/<id>/reel.mp4 plus one review frame per beat (frame-01.jpg ...).
"""
import asyncio, io, json, os, random, shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "fabrika"
FONTS = HERE / "fonts"
MUSIC = HERE / "music"
W, H, FPS = 1080, 1920, 30
PAD = 90
GOLD = (212, 175, 55)
WHITE = (255, 255, 255)
INK = (12, 12, 12)
HANDLE = "@suksesishqip"
DEFAULT_VOICE = "gemini:Riko"          # Gemini TTS; Anila (Edge) is the last-resort fallback
FALLBACK_VOICE = "sq-AL-AnilaNeural"
GEMINI_MODEL = "gemini-3.8-flash-tts"
GEMINI_STYLE = ("Speak in standard Albanian, naturally, like a friend telling you something true over coffee: "
                "calm, convincing, short natural pauses, never like an advert.")
HYPE_STYLE = ("Speak in standard Albanian with high energy and excitement, like a storyteller revealing a shocking true story "
              "to a friend: punchy, fast-paced, strong emphasis on the numbers, short dramatic pauses, never monotone, "
              "never like an advert.")
HYPE_SPEED = 1.07   # Riko on Hype Reels, approved by Mario 2026-11-13
HYPE_LOOK = "grafit"   # default look for Hype Reels, approved by Mario 2026-11-14: "grafit" (graphite/mint, see BRAND.md);
                       # "classic" (black/yellow/red) is still available with "look": "classic"
VOICE_RATE = "+6%"
GAP = 0.35          # silence between beats (s)
TAIL = 0.8          # hold after the last beat (s)
SILENT_BEAT = 3.0   # beat length when there is no voice (s)
SPLIT = 4.2         # beats longer than this get a second shot (cut mid-beat)


def font(name, size):
    return ImageFont.truetype(str(FONTS / f"{name}.ttf"), size)


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {p.stderr[-800:]}")
    return p.stdout


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)]).strip())


# ---------- footage ----------

def pixabay_video(query, used):
    import requests
    key = os.environ["PIXABAY_API_KEY"]
    r = requests.get("https://pixabay.com/api/videos/", timeout=30,
                     params=dict(key=key, q=query, video_type="film", safesearch="true",
                                 per_page=50, order="popular"))
    r.raise_for_status()
    hits = [h for h in r.json().get("hits", []) if str(h["id"]) not in used and h.get("duration", 0) >= 6]
    if not hits:
        raise RuntimeError(f"no unused Pixabay video for '{query}'")

    def pick(h):  # best rendition to fill a vertical frame
        vs = h["videos"]
        for name in ("large", "medium"):
            v = vs.get(name) or {}
            if v.get("url") and v.get("height", 0) >= 1080 and v.get("size", 0) < 120_000_000:
                return v
        return vs.get("medium") or vs.get("small")

    vertical = [h for h in hits if h["videos"]["medium"]["height"] > h["videos"]["medium"]["width"]]
    pool = vertical[:6] or hits[:6]
    h = random.choice(pool)
    v = pick(h)
    data = requests.get(v["url"], timeout=180)
    data.raise_for_status()
    return data.content, str(h["id"]), h.get("pageURL", "")


def pixabay_videos(query, used, n):
    """Up to n different clips for one search (vertical first). Returns [(bytes, id, page)]."""
    import requests
    r = requests.get("https://pixabay.com/api/videos/", timeout=30,
                     params=dict(key=os.environ["PIXABAY_API_KEY"], q=query, video_type="film",
                                 safesearch="true", per_page=50, order="popular"))
    r.raise_for_status()
    hits = [h for h in r.json().get("hits", []) if "v" + str(h["id"]) not in used and h.get("duration", 0) >= 5]
    if not hits:
        raise RuntimeError(f"no unused Pixabay video for '{query}'")
    vertical = [h for h in hits if h["videos"]["medium"]["height"] > h["videos"]["medium"]["width"]]
    # most popular first (best match for the search); vertical clips ahead of horizontal
    pool = (vertical[:max(3, n)] + [h for h in hits if h not in vertical])[:max(4, n + 2)]
    out = []
    for h in pool[:n]:
        vs = h["videos"]
        v = next((vs[k] for k in ("large", "medium") if (vs.get(k) or {}).get("url")
                  and vs[k].get("height", 0) >= 1080 and vs[k].get("size", 0) < 120_000_000), vs["medium"])
        data = requests.get(v["url"], timeout=180)
        data.raise_for_status()
        out.append((data.content, str(h["id"]), h.get("pageURL", "")))
    return out


def pixabay_video_by_id(vid):
    import requests
    r = requests.get("https://pixabay.com/api/videos/", timeout=30,
                     params=dict(key=os.environ["PIXABAY_API_KEY"], id=vid))
    r.raise_for_status()
    h = r.json()["hits"][0]
    vs = h["videos"]
    v = next((vs[n] for n in ("large", "medium") if (vs.get(n) or {}).get("url")
              and vs[n].get("height", 0) >= 1080 and vs[n].get("size", 0) < 120_000_000), vs["medium"])
    data = requests.get(v["url"], timeout=180)
    data.raise_for_status()
    return data.content, str(h["id"]), h.get("pageURL", "")


def placeholder_video(path, seconds):
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"gradients=s=1080x1920:d={seconds}:speed=0.02:c0=0x1a1a2e:c1=0x3a2f1f",
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(path)])


# ---------- voice ----------

async def _tts(text, voice, path):
    """Save the voice and return word timings [(start_s, end_s, word), ...] (may be empty)."""
    import edge_tts
    try:
        c = edge_tts.Communicate(text, voice, rate=VOICE_RATE, boundary="WordBoundary")
    except TypeError:  # older edge-tts: word boundaries are the default
        c = edge_tts.Communicate(text, voice, rate=VOICE_RATE)
    words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]))
    return words


def gemini_tts(text, voice, style, out_wav):
    """One Gemini TTS request for the whole Reel. Retries once after a minute on rate limits."""
    import base64, time, requests
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("no GEMINI_API_KEY")
    bodies = [
        {"contents": [{"role": "user", "parts": [{"text": text, "speech_metadata": {"style": style}}]}],
         "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"voice": voice}}}},
        {"contents": [{"role": "user", "parts": [{"text": f"{style}\n{text}"}]}],
         "generationConfig": {"responseModalities": ["AUDIO"],
                              "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}},
    ]
    last = ""
    for attempt in range(3):
        for body in bodies:
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
                              headers={"x-goog-api-key": key}, json=body, timeout=180)
            if r.status_code == 200:
                part = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
                raw = base64.b64decode(part["data"])
                src = out_wav.with_suffix(".raw")
                src.write_bytes(raw)
                inp = ["-i", str(src)] if raw[:4] == b"RIFF" else ["-f", "s16le", "-ar", "24000", "-ac", "1", "-i", str(src)]
                run(["ffmpeg", "-y", *inp, "-ar", "44100", "-ac", "1", str(out_wav)])
                return
            last = f"{r.status_code} {r.text[:200]}"
            if r.status_code == 429:
                break
        time.sleep(65)
    raise RuntimeError("gemini tts failed: " + last)


def _speech_weight(t):
    """Rough spoken length of a beat: letters count, punctuation inside a beat adds a short pause."""
    import re
    t = re.sub(r"<[^>]+>", "", t)
    return max(1.0, len(re.sub(r"[^\w]", "", t)) + 4 * len(re.findall(r"[.,;:!?…]\s+\S", t)))


def pick_cuts(pauses, weights, total):
    """Choose one pause per beat boundary, in order.

    pauses: [(mid_s, length_s), ...] sorted by time. A cut must land on a real pause; long pauses
    (Gemini's paragraph breaks between beats) are preferred over short ones (commas/full stops inside a
    beat), and each cut should be near where the beat is expected to end. Returns None if impossible.
    """
    n_cuts = len(weights) - 1
    if n_cuts <= 0:
        return []
    if len(pauses) < n_cuts:
        return None
    tot_w = sum(weights)
    want, acc = [], 0.0
    for w in weights[:-1]:
        acc += w
        want.append(total * acc / tot_w)
    longest = max(l for _, l in pauses) or 1.0
    INF = float("inf")
    m = len(pauses)
    # cost[k][j]: best cost with cut k placed on pause j
    cost = [[INF] * m for _ in range(n_cuts)]
    back = [[-1] * m for _ in range(n_cuts)]

    def local(k, j):
        mid, ln = pauses[j]
        return abs(mid - want[k]) / max(total, 1e-6) * 10 + (1 - ln / longest) * 3

    for j in range(m):
        if pauses[j][0] > 0.6:
            cost[0][j] = local(0, j)
    for k in range(1, n_cuts):
        for j in range(m):
            # best predecessor among pauses at least 0.6 s earlier
            cands = [(cost[k - 1][i], i) for i in range(j) if pauses[j][0] - pauses[i][0] >= 0.6 and cost[k - 1][i] < INF]
            if cands:
                c, i = min(cands)
                cost[k][j], back[k][j] = c + local(k, j), i
    last = [(cost[n_cuts - 1][j], j) for j in range(m) if total - pauses[j][0] >= 0.6 and cost[n_cuts - 1][j] < INF]
    if not last:
        return None
    _, j = min(last)
    cuts = []
    for k in range(n_cuts - 1, -1, -1):
        cuts.append(pauses[j][0])
        j = back[k][j]
    return cuts[::-1]


def sync_ok(parts, texts):
    """Each beat's clip must fit its text: speaking speed (letters per second) within a sane band of
    the Reel's median. A wrong cut gives one beat too much audio and its neighbour too little."""
    rates = [_speech_weight(t) / max(d, 0.05) for (_, d), t in zip(parts, texts)]
    med = sorted(rates)[len(rates) // 2]
    bad = [i + 1 for i, r in enumerate(rates) if r < med * 0.6 or r > med * 1.6]
    return not bad, bad, [round(r, 1) for r in rates]


def split_on_pauses(wav, texts, tmp):
    """Cut one narration into one clip per beat, on real pauses only. Raises if the cut can't be trusted."""
    import re
    total = duration(wav)
    p = subprocess.run(["ffmpeg", "-i", str(wav), "-af", "silencedetect=noise=-38dB:d=0.12", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", p.stderr)]
    pauses = [((a + b) / 2, b - a) for a, b in zip(starts, ends) if a > 0.05 and b < total - 0.05]
    cuts = pick_cuts(pauses, [_speech_weight(t) for t in texts], total)
    if cuts is None:
        raise RuntimeError(f"not enough pauses to split the narration ({len(pauses)} for {len(texts)} beats)")
    bounds = [0.0] + cuts + [total]
    parts = []
    trim = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
            "silenceremove=start_periods=1:start_threshold=-45dB,areverse")
    for i in range(len(texts)):
        out = tmp / f"v{i}.mp3"
        run(["ffmpeg", "-y", "-i", str(wav), "-ss", f"{bounds[i]:.3f}", "-to", f"{bounds[i + 1]:.3f}",
             "-af", trim, "-ar", "44100", "-ac", "2", str(out)])
        parts.append((out, duration(out)))
    ok, bad, rates = sync_ok(parts, texts)
    if not ok:
        raise RuntimeError(f"narration split looks out of sync on beat(s) {bad} (letters/s {rates})")
    return parts


def gemini_per_beat(texts, voice, style, tmp):
    """Fallback: one Gemini request per beat, so each clip belongs to its beat by construction."""
    trim = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
            "silenceremove=start_periods=1:start_threshold=-45dB,areverse")
    parts = []
    for i, t in enumerate(texts):
        wav = tmp / f"g{i}.wav"
        gemini_tts(t, voice, style, wav)
        out = tmp / f"v{i}.mp3"
        run(["ffmpeg", "-y", "-i", str(wav), "-af", trim, "-ar", "44100", "-ac", "2", str(out)])
        parts.append((out, duration(out)))
    return parts


def voice_beat(text, voice, path):
    words = asyncio.run(_tts(text, voice, path))
    return duration(path), words


# ---------- overlays ----------

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, name, start, minsize, maxw, maxh, lh):
    for size in range(start, minsize - 1, -2):
        f = font(name, size)
        lines = wrap(d, text, f, maxw)
        if all(d.textlength(l, font=f) <= maxw for l in lines) and len(lines) * int(size * lh) <= maxh:
            return f, lines, int(size * lh)
    raise ValueError(f"beat text too long: {text[:40]}…")


def beat_overlay(beat, first):
    """Transparent 1080x1920 PNG with the beat's text, centred in the Reels safe zone."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    maxw = W - 2 * PAD
    name, start = ("s700", 124) if first else ("i800", 80)
    f, lines, step = fit(d, beat["text"], name, start, 52, maxw, 640, 1.18)
    hl_lines, hstep, hf = [], 0, None
    if beat.get("highlight"):
        hf, hl_lines, hstep = fit(d, beat["highlight"], "i800", 64, 44, maxw - 30, 300, 1.3)
    block = len(lines) * step + (40 + len(hl_lines) * hstep if hl_lines else 0)
    # Reels UI covers the bottom ~25% and the top ~12%: keep text in the middle band.
    y = int(H * 0.42 - block / 2)
    for l in lines:
        x = (W - d.textlength(l, font=f)) / 2
        d.text((x + 3, y + 4), l, font=f, fill=(0, 0, 0, 170))   # soft shadow
        d.text((x, y), l, font=f, fill=WHITE)
        y += step
    if hl_lines:
        y += 40
        for l in hl_lines:
            tw = d.textlength(l, font=hf)
            x = (W - tw) / 2
            b = hf.getbbox(l)
            d.rectangle([x - 16, y + b[1] - 14, x + tw + 16, y + b[3] + 14], fill=GOLD + (255,))
            d.text((x, y), l, font=hf, fill=INK)
            y += hstep
    return img


def frame_overlay():
    """Constant layer: top/bottom darkening and the handle."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad = Image.new("L", (1, H))
    for yy in range(H):
        t = yy / H
        a = 0.38 + 0.42 * (abs(t - 0.42) / 0.58)  # darker towards edges, readable centre
        grad.putpixel((0, yy), int(255 * min(0.85, a)))
    img.putalpha(grad.resize((W, H)))
    d = ImageDraw.Draw(img)
    f = font("i700", 34)
    d.text(((W - d.textlength(HANDLE, font=f)) / 2, int(H * 0.68)), HANDLE, font=f, fill=GOLD + (255,))
    return img


# ---------- word-by-word captions ----------

CAP_SIZE = 108
CAP_Y = 0.44  # centre of the caption band (fraction of height)


def word_times(tokens, bounds, dur):
    """Start time of each displayed token inside its beat (seconds)."""
    if bounds and len(bounds) == len(tokens):
        return [b[0] for b in bounds]
    # counts differ (numbers, symbols read out): spread by length over the voiced span
    a = bounds[0][0] if bounds else 0.0
    b = bounds[-1][1] if bounds else dur
    lens = [max(2, len(t)) for t in tokens]
    tot, acc, out = sum(lens), 0, []
    for l in lens:
        out.append(a + (b - a) * acc / tot)
        acc += l
    return out


def chunks(tokens, maxw_chars=20, maxn=3):
    """Group token indexes into short caption chunks, breaking after punctuation."""
    out, cur = [], []
    for i, t in enumerate(tokens):
        if cur and (len(cur) >= maxn or len(" ".join(tokens[j] for j in cur + [i])) > maxw_chars):
            out.append(cur)
            cur = []
        cur.append(i)
        if t[-1] in ".,!?:;…":
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def caption_png(words, active, path):
    """Chunk of 1-3 words, the spoken word in gold. Black stroke keeps it readable on any footage."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    maxw = W - 2 * PAD
    text = " ".join(words)
    size = next((sz for sz in range(CAP_SIZE, 83, -4)  # one line if it fits at >= 84 px
                 if d.textlength(text, font=font("i800", sz)) <= maxw), None)
    if size:
        f, lines = font("i800", size), [text]
    else:
        for size in range(CAP_SIZE, 50, -4):
            f = font("i800", size)
            lines = wrap(d, text, f, maxw)
            if all(d.textlength(l, font=f) <= maxw for l in lines) and len(lines) <= 2:
                break
    step = int(size * 1.2)
    y = int(H * CAP_Y - len(lines) * step / 2)
    k = 0
    for l in lines:
        x = (W - d.textlength(l, font=f)) / 2
        for w in l.split():
            col = GOLD if k == active else WHITE
            d.text((x, y), w, font=f, fill=col + (255,), stroke_width=7, stroke_fill=(0, 0, 0, 255))
            x += d.textlength(w + " ", font=f)
            k += 1
        y += step
    img.save(path)


def highlight_png(text, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    hf, lines, step = fit(d, text, "i800", 84, 48, W - 2 * PAD - 30, 400, 1.3)
    y = int(H * CAP_Y - len(lines) * step / 2)
    for l in lines:
        tw = d.textlength(l, font=hf)
        x = (W - tw) / 2
        b = hf.getbbox(l)
        d.rectangle([x - 18, y + b[1] - 16, x + tw + 18, y + b[3] + 16], fill=GOLD + (255,))
        d.text((x, y), l, font=hf, fill=INK)
        y += step
    img.save(path)


def caption_track(beats, starts, ends, total, timings, tmp):
    """Transparent caption video: hook beat in full, then word-by-word captions, payoff in a gold box."""
    segs = []  # (start, png)
    blank = tmp / "blank.png"
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
    n = 0
    for i, b in enumerate(beats):
        s0 = starts[i]
        if i == 0:
            p = tmp / "c_hook.png"
            beat_overlay(b, True).save(p)
            segs.append((0.0, p))
            continue
        tokens = b["text"].split()
        hl = b.get("highlight", "").split()
        bounds, dur = timings[i]
        times = word_times(tokens + hl, bounds, dur)
        for ch in chunks(tokens):
            for j, idx in enumerate(ch):
                p = tmp / f"c{n}.png"; n += 1
                caption_png([tokens[k] for k in ch], j, p)
                segs.append((s0 + (0 if idx == 0 else times[idx]), p))
        if hl:
            p = tmp / f"c{n}.png"; n += 1
            highlight_png(b["highlight"], p)
            segs.append((s0 + times[len(tokens)], p))
    segs.sort(key=lambda x: x[0])
    lines, min_d = [], 1.0 / FPS
    for k, (t0, p) in enumerate(segs):
        t1 = segs[k + 1][0] if k + 1 < len(segs) else total
        if t1 - t0 < min_d:
            continue
        lines += [f"file '{p}'", f"duration {t1 - t0:.3f}"]
    lines.append(f"file '{segs[-1][1]}'")
    lst = tmp / "caps.txt"
    lst.write_text("\n".join(lines))
    out = tmp / "caps.mov"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", f"fps={FPS},format=argb",
         "-t", str(total), "-c:v", "qtrle", str(out)])
    return out, segs


# ---------- music ----------

def pick_music(choice):
    if choice == "none" or not MUSIC.exists():
        return None
    tracks = sorted(p for p in MUSIC.iterdir() if p.suffix.lower() in (".mp3", ".m4a", ".wav"))
    if not tracks:
        return None
    if choice and choice.startswith("mood:"):  # e.g. "mood:piano"
        mood = choice[5:]
        same = [t for t in tracks if t.name.startswith(mood + "-")]
        return random.choice(same or tracks)
    if choice and choice != "auto":
        p = MUSIC / choice
        return p if p.exists() else random.choice(tracks)
    return random.choice(tracks)


# ---------- motion engine (Remotion) ----------

REMOTION = ROOT / "remotion"


def _norm(w):
    return "".join(ch for ch in w.lower() if ch.isalnum())


def item_frames(items, words, beat_len):
    """Frame (inside the beat) at which each list item should appear: when the voice says its first word."""
    out, k = [], 0
    for it in items:
        first = _norm(it.split()[0]) if it.split() else ""
        hit = None
        for j in range(k, len(words)):
            if first and _norm(words[j][2]).startswith(first[:5]):
                hit = j
                break
        if hit is None:
            return None
        out.append(max(0, int(words[hit][0] * FPS) - 3))
        k = hit + 1
    return out


def audio_track(post, beats, starts, total, timings, audio_parts, tmp, info):
    """Voice + sound effects + music, loudness-normalised (same mix as footage Reels)."""
    voice_wav = tmp / "voice.wav"
    inputs, filt = [], []
    real = [(i, p) for i, (p, _) in enumerate(audio_parts) if p]
    if real:
        for k, (i, p) in enumerate(real):
            inputs += ["-i", str(p)]
            ms = int(starts[i] * 1000)
            filt.append(f"[{k}:a]adelay={ms}|{ms}[a{k}]")
        mix = "".join(f"[a{k}]" for k in range(len(real)))
        filt.append(f"{mix}amix=inputs={len(real)}:normalize=0,apad,atrim=0:{total}[out]")
        run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]",
             "-ar", "44100", "-ac", "2", str(voice_wav)])
        parts, labels = [], []
        for i in range(1, len(beats)):
            ms = max(0, int((starts[i] - 0.25) * 1000))
            parts.append(f"anoisesrc=d=0.5:c=pink:a=0.6,highpass=f=500,lowpass=f=6000,"
                         f"afade=t=in:d=0.3,afade=t=out:st=0.3:d=0.2,volume=0.30,"
                         f"aformat=sample_rates=44100:channel_layouts=stereo,adelay={ms}|{ms}[x{i}]")
            labels.append(f"[x{i}]")
        SFX = {   # small synthetic sounds (ffmpeg aevalsrc), volume, length
            "pop": ("0.8*sin(2*PI*(500+2500*t)*t)*exp(-40*t)", 0.35, 0.12),
            "tick": ("0.6*sin(2*PI*2600*t)*exp(-180*t)", 0.22, 0.03),
            "drop": ("0.8*sin(2*PI*(900-700*t)*t)*exp(-6*t)", 0.35, 0.45),
            "cash": ("0.5*(sin(2*PI*2093*t)+sin(2*PI*2637*t))*exp(-9*t)+0.4*sin(2*PI*1568*(t-0.08))*exp(-9*(t-0.08))*gte(t,0.08)", 0.30, 0.5),
            "riser": ("0.5*sin(2*PI*(200+900*t*t)*t)*(t/0.6)", 0.20, 0.6),
        }
        for k, (t_sfx, kind) in enumerate(post.get("_sfx", [])):
            expr, vol, length = SFX[kind]
            ms = max(0, int(t_sfx * 1000))
            parts.append(f"aevalsrc='{expr}':s=44100:d={length},aformat=sample_rates=44100:channel_layouts=stereo,"
                         f"afade=t=out:st={max(0.0, length - 0.03):.2f}:d=0.03,volume={vol},adelay={ms}|{ms}[s{k}]")
            labels.append(f"[s{k}]")
        for k, t_hit in enumerate(post.get("_hits", [])):   # a low hit when a key visual lands (hype Reels)
            ms = max(0, int(t_hit * 1000))
            parts.append(f"aevalsrc='0.9*sin(2*PI*(42+70*exp(-7*t))*t)*exp(-5*t)':s=44100:d=0.7,"
                         f"aformat=sample_rates=44100:channel_layouts=stereo,volume=0.55,adelay={ms}|{ms}[h{k}]")
            labels.append(f"[h{k}]")
        if labels and post.get("sfx", True):
            sv = tmp / "voice_sfx.wav"
            run(["ffmpeg", "-y", "-i", str(voice_wav), "-filter_complex",
                 ";".join(parts) + f";[0:a]{''.join(labels)}amix=inputs={len(labels) + 1}:normalize=0:duration=first[out]",
                 "-map", "[out]", "-ar", "44100", "-ac", "2", str(sv)])
            voice_wav = sv
    else:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", str(total), str(voice_wav)])
    track = pick_music(post.get("music", "mood:lofi"))
    final_audio = tmp / "audio.m4a"
    if track:
        info["music"] = track.name
        vol = "0.10" if real else "0.7"
        run(["ffmpeg", "-y", "-i", str(voice_wav), "-stream_loop", "-1", "-i", str(track), "-filter_complex",
             f"[1:a]volume={vol},afade=t=in:d=0.6,afade=t=out:st={max(0, total - 1.2)}:d=1.2[m];"
             f"[0:a]loudnorm=I=-16:TP=-2,aresample=44100,asplit=2[vo][sc];[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[md];"
             f"[vo][md]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
             "-map", "[out]", "-t", str(total), "-c:a", "aac", "-b:a", "160k", str(final_audio)])
    else:
        run(["ffmpeg", "-y", "-i", str(voice_wav), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
             "-c:a", "aac", "-b:a", "160k", str(final_audio)])
    return final_audio


def render_motion(post, pdir, tmp, info, beats, starts, ends, total, timings, audio_parts):
    """Animated Reel (no footage): hook, text, list, steps, number and compare beats drawn by Remotion."""
    n = len(beats)
    bounds = starts[1:] + [total]
    total_frames = int(round(total * FPS))
    props_beats = []
    for i, b in enumerate(beats):
        f0 = int(round(starts[i] * FPS))
        f1 = total_frames if i == n - 1 else int(round(bounds[i] * FPS))
        pb = {k: v for k, v in b.items() if k not in ("say", "video_query", "video_id")}
        pb["type"] = b.get("type", "hook" if i == 0 else "text")
        pb.update({"from": f0, "dur": max(1, f1 - f0)})
        if pb["type"] in ("list", "steps") and timings[i][0]:
            fr = item_frames(b.get("items", []), timings[i][0], f1 - f0)
            if fr:
                pb["item_times"] = fr
        props_beats.append(pb)
    # background footage per beat (blurred and darkened behind the animation)
    bgdir = REMOTION / "public" / "bg"
    if post.get("video_query") and post["video_query"] != "none" and os.environ.get("PIXABAY_API_KEY"):
        shutil.rmtree(bgdir, ignore_errors=True)
        bgdir.mkdir(parents=True)
        used = info.setdefault("_used", set())
        try:
            pool = pixabay_videos(post["video_query"], used, n)
        except RuntimeError:
            pool = []
        info["clips"] = []
        for i, b in enumerate(beats):
            c = None
            if b.get("video_id"):
                c = pixabay_video_by_id(b["video_id"])
            elif b.get("video_query"):
                try:
                    c = pixabay_videos(b["video_query"], used, 1)[0]
                except RuntimeError:
                    c = None
            if c is None and pool:
                c = pool[i % len(pool)]
            if c is None:
                continue
            fp = bgdir / f"b{i}.mp4"
            fp.write_bytes(c[0])
            used.add("v" + c[1])
            props_beats[i]["bg"] = f"bg/b{i}.mp4"
            props_beats[i]["bg_frames"] = int(duration(fp) * FPS)
            info["clips"].append({"beat": i + 1, "pixabay_id": c[1], "page": c[2]})
        info.pop("_used", None)
    props = {"durationInFrames": total_frames, "handle": HANDLE, "beats": props_beats}
    pf = tmp / "props.json"
    pf.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    silent = tmp / "motion.mp4"
    cmd = ["npx", "remotion", "render", "src/index.ts", "Explainer", str(silent), f"--props={pf}",
           "--codec=h264", "--crf=20", "--muted"]
    if os.environ.get("REMOTION_BROWSER"):
        cmd.append(f"--browser-executable={os.environ['REMOTION_BROWSER']}")
    p = subprocess.run(cmd, cwd=REMOTION, capture_output=True, text=True)
    shutil.rmtree(REMOTION / "public" / "bg", ignore_errors=True)
    if p.returncode != 0:
        raise RuntimeError("remotion failed: " + (p.stderr or p.stdout)[-1500:])
    audio = audio_track(post, beats, starts, total, timings, audio_parts, tmp, info)
    part, out = pdir / "reel.part.mp4", pdir / "reel.mp4"
    run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(part)])
    part.rename(out)
    files = [out]
    for i in range(n):  # review: each beat near its end, when everything in it is on screen
        ts = starts[i] + 0.8 * (bounds[i] - starts[i])
        fp = pdir / f"frame-{i + 1:02d}.jpg"
        run(["ffmpeg", "-y", "-ss", f"{ts:.2f}", "-i", str(out), "-frames:v", "1", "-q:v", "3", str(fp)])
        files.append(fp)
    shutil.rmtree(tmp, ignore_errors=True)
    info.update({"engine": "motion", "duration": total,
                 "shots": [{"frame": f"frame-{i + 1:02d}.jpg", "beat": i + 1} for i in range(n)]})
    return files, info


# ---------- hype engine (Remotion, high-contrast story look) ----------

def _norm_word(w):
    return "".join(ch for ch in w.lower() if ch.isalnum())


def speech_segments(path, dur):
    """Speech stretches inside one beat's voice clip (the pauses split it into phrases)."""
    import re
    p = subprocess.run(["ffmpeg", "-i", str(path), "-af", "silencedetect=noise=-35dB:d=0.12", "-f", "null", "-"],
                       capture_output=True, text=True)
    ss = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", p.stderr)]
    se = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", p.stderr)]
    segs, t = [], 0.0
    for a, b in zip(ss, se):
        if a > t + 0.05:
            segs.append((t, a))
        t = b
    if dur > t + 0.05:
        segs.append((t, dur))
    return segs or [(0.0, dur)]


def word_times(text, segs, dur):
    """Start time (s) of every caption word: phrases (split at punctuation) mapped onto the voice's speech stretches."""
    import re
    words = text.split()
    phrases, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[,.;:!?…]$", w):
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)
    spans = segs if len(segs) == len(phrases) else [(segs[0][0], segs[-1][1])]
    groups = phrases if len(segs) == len(phrases) else [words]
    out = []
    for (a, b), g in zip(spans, groups):
        L = [max(1, len(_norm_word(w))) for w in g]
        tot, acc = sum(L), 0
        for w, l in zip(g, L):
            out.append(a + (b - a) * acc / tot)
            acc += l
    return out


def render_hype(post, pdir, tmp, info, beats, starts, total, timings, audio_parts):
    """Story Reel in the high-contrast look: one scene per beat, visuals and captions timed on the voice."""
    n = len(beats)
    bounds = starts[1:] + [total]
    total_frames = int(round(total * FPS))
    props_beats, hits, sfx = [], [], []
    for i, b in enumerate(beats):
        f0 = int(round(starts[i] * FPS))
        f1 = total_frames if i == n - 1 else int(round(bounds[i] * FPS))
        text = b.get("text", "")
        words = text.split()
        path, dur = audio_parts[i]
        if path:
            segs = speech_segments(path, dur)
        else:
            dur = (bounds[i] - starts[i]) * 0.8
            segs = [(0.0, dur)]
        wt = word_times(text, segs, dur)
        word_at = [max(0, int(round(t * FPS)) - 2) for t in wt]

        def find(token, after=0):
            key = _norm_word(str(token).split()[0]) if str(token).split() else ""
            for j in range(after, len(words)):
                if key and _norm_word(words[j]).startswith(key[:6]):
                    return j
            return None

        pb = {k: v for k, v in b.items() if k not in ("say", "video_query", "video_id", "at", "scene")}
        pb.update({"type": b.get("type", "hook" if i == 0 else "text"), "from": f0, "dur": max(1, f1 - f0),
                   "speech": int(round(dur * FPS)), "text": text, "word_at": word_at})
        if "keys" not in pb:
            pb["keys"] = [w for w in words if any(ch.isdigit() for ch in w)]
        trig = b.get("at") or (b.get("highlight") if pb["type"] == "text" else None) or (b.get("reply") if pb["type"] == "chat" else None)
        if trig:
            j = find(trig)
            if j is not None:
                pb["at"] = word_at[j]
        if pb["type"] in ("list", "checks"):
            labels = b.get("items") or [r.get("label", "") for r in b.get("rows", [])]
            ats, k = [], 0
            for it in labels:
                j = find(it, k)
                if j is None:
                    ats = []
                    break
                ats.append(word_at[j])
                k = j + 1
            if ats:
                pb["item_at"] = ats
        t0 = starts[i]
        at_s = (pb["at"] / FPS) if pb.get("at") is not None else None
        sp = dur
        typ = pb["type"]
        if b.get("figure"):   # pop when a figure appears
            ft = {"hook": sp * 0.5, "text": (at_s or sp * 0.45) + 0.2, "year": (at_s if b.get("stamp") else 1.0) or 1.0}.get(typ)
            if ft is not None:
                sfx.append((t0 + ft, "pop" if not (typ == "year" and b.get("stamp")) else "drop"))
        if typ == "versus":
            sfx += [(t0 + 0.15, "pop"), (t0 + (at_s if at_s is not None else sp * 0.5), "pop")]
        for x in pb.get("item_at", []):
            sfx.append((t0 + x / FPS, "pop"))
        if typ == "count":
            c0 = t0 + (at_s if at_s is not None else 4 / FPS)
            sfx += [(c0 + k * 0.08, "tick") for k in range(12)]
            if (b.get("prefix") or "").strip() in ("€", "$") or "lek" in (b.get("suffix") or ""):
                sfx.append((c0 + 0.95, "cash"))
        if typ == "icons":
            c0 = t0 + (at_s if at_s is not None else 6 / FPS)
            sfx += [(c0 + k * 0.1, "tick") for k in range(min(10, int(b.get("n", 10))))]
        if typ == "year":
            sfx += [(t0 + 0.1 + k * 0.09, "tick") for k in range(10)]
        if b.get("figure") == "money" or (typ == "hook" and any(ch in (b.get("big") or "") for ch in "€$")):
            sfx.append((t0 + (sp * 0.5 if typ != "hook" else 0.05), "cash"))
        if at_s is not None and typ in ("year", "text", "chat") and at_s > 0.7:   # tension before the reveal
            sfx.append((max(t0, t0 + at_s - 0.6), "riser"))
        if pb.get("at") is not None and pb["type"] in ("hook", "chat", "year", "text", "bars") and \
                (pb["type"] != "hook" or b.get("stamp")) and (pb["type"] != "year" or b.get("stamp")):
            hits.append(starts[i] + pb["at"] / FPS)
        props_beats.append(pb)
    look = post.get("look", HYPE_LOOK)
    props = {"durationInFrames": total_frames, "handle": HANDLE, "beats": props_beats, "rich": bool(post.get("rich", True)), "look": look}
    pf = tmp / "props.json"
    pf.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    silent = tmp / "hype.mp4"
    cmd = ["npx", "remotion", "render", "src/index.ts", "HypeReel", str(silent), f"--props={pf}",
           "--codec=h264", "--crf=20", "--muted"]
    if os.environ.get("REMOTION_BROWSER"):
        cmd.append(f"--browser-executable={os.environ['REMOTION_BROWSER']}")
    p = subprocess.run(cmd, cwd=REMOTION, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("remotion failed: " + (p.stderr or p.stdout)[-1500:])
    post = dict(post)
    post.setdefault("music", "mood:cinematic")
    post["_hits"] = hits
    post["_sfx"] = sorted(sfx)[:60]
    info["sfx"] = len(post["_sfx"])
    audio = audio_track(post, beats, starts, total, timings, audio_parts, tmp, info)
    part, out = pdir / "reel.part.mp4", pdir / "reel.mp4"
    run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-af", "apad", "-t", f"{total:.2f}", "-movflags", "+faststart", str(part)])
    part.rename(out)
    files = [out]
    for i in range(n):  # review: each beat near its end, when everything in it is on screen
        ts = starts[i] + 0.85 * (bounds[i] - starts[i])
        fp = pdir / f"frame-{i + 1:02d}.jpg"
        run(["ffmpeg", "-y", "-ss", f"{ts:.2f}", "-i", str(out), "-frames:v", "1", "-q:v", "3", str(fp)])
        files.append(fp)
    shutil.rmtree(tmp, ignore_errors=True)
    info.update({"engine": "hype", "look": look, "duration": total,
                 "shots": [{"frame": f"frame-{i + 1:02d}.jpg", "beat": i + 1, "start": round(starts[i], 2)} for i in range(n)]})
    return files, info


# ---------- stickman engine ----------

def render_stickman(post, pdir, tmp, info, beats, starts, total, timings, audio_parts):
    """Minimalist stickman acting out each beat, captions with red keywords (see fabrika/stickman.py)."""
    from stickman import render_video
    n = len(beats)
    bounds = starts[1:] + [total]
    voiced = [timings[i][1] if audio_parts[i][0] else (bounds[i] - starts[i]) * 0.7 for i in range(n)]
    silent = tmp / "stickman.mp4"
    render_video(beats, starts, bounds, total, voiced, silent)
    post = dict(post)
    post.setdefault("sfx", False)        # calm look: no whooshes
    post.setdefault("music", "mood:piano")
    audio = audio_track(post, beats, starts, total, timings, audio_parts, tmp, info)
    part, out = pdir / "reel.part.mp4", pdir / "reel.mp4"
    run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(part)])
    part.rename(out)
    files = [out]
    for i in range(n):  # review: each beat near its end, when the whole caption is on screen
        ts = starts[i] + 0.85 * (bounds[i] - starts[i])
        fp = pdir / f"frame-{i + 1:02d}.jpg"
        run(["ffmpeg", "-y", "-ss", f"{ts:.2f}", "-i", str(out), "-frames:v", "1", "-q:v", "3", str(fp)])
        files.append(fp)
    shutil.rmtree(tmp, ignore_errors=True)
    info.update({"engine": "stickman", "duration": total,
                 "scenes": [b.get("scene", "") for b in beats],
                 "shots": [{"frame": f"frame-{i + 1:02d}.jpg", "beat": i + 1} for i in range(n)]})
    return files, info


# ---------- main ----------

def render_reel(post, pdir, used, offline=False):
    beats = post["beats"]
    voice = post.get("voice", DEFAULT_VOICE)
    if voice == FALLBACK_VOICE and not post.get("force_voice"):  # owner's choice: Riko first, Anila only as fallback
        voice = DEFAULT_VOICE
    tmp = Path(tempfile.mkdtemp())
    info = {"video": None, "music": None, "voice": voice}

    # 1. voice per beat -> timings
    starts, ends, t = [], [], 0.0
    audio_parts, timings = [], []
    if post.get("engine") == "stickman":  # red keywords are inside the text, not extra words
        spoken_all = [b.get("say") or b.get("text", "") for b in beats]
    else:
        spoken_all = [b.get("say") or " ".join(x for x in (b.get("text", ""), b.get("highlight", "")) if x)
                      for b in beats]
    gem = None
    style = post.get("voice_style") or (HYPE_STYLE if post.get("engine") == "hype" else GEMINI_STYLE)
    if voice.startswith("gemini:") and not offline:
        try:
            wav = tmp / "narration.wav"
            gemini_tts("\n\n".join(spoken_all), voice.split(":", 1)[1], style, wav)
            try:
                gem = split_on_pauses(wav, spoken_all, tmp)
                info["voice_sync"] = "split"
            except RuntimeError as e:  # cut not trustworthy: voice each beat on its own (always in sync)
                print("Narration split rejected, voicing each beat separately:", e)
                info["voice_split_rejected"] = str(e)[:200]
                gem = gemini_per_beat(spoken_all, voice.split(":", 1)[1], style, tmp)
                info["voice_sync"] = "per-beat"
            info["voice"] = voice
            speed = float(post.get("voice_speed", HYPE_SPEED if post.get("engine") == "hype" else 1.0))
            if gem and abs(speed - 1.0) > 0.01:   # Mario: Riko a bit faster keeps people watching
                fast = []
                for k, (ap, _) in enumerate(gem):
                    fp = tmp / f"fast{k}.mp3"
                    run(["ffmpeg", "-y", "-i", str(ap), "-af", f"atempo={speed:.3f}", "-ar", "44100", "-ac", "2", str(fp)])
                    fast.append((fp, duration(fp)))
                gem = fast
                info["voice_speed"] = speed
        except Exception as e:  # last resort: Anila
            print("Gemini voice failed, using Anila:", e)
            voice = FALLBACK_VOICE
            info["voice"] = voice
            info["voice_fallback"] = str(e)[:200]
    for i, b in enumerate(beats):
        spoken = spoken_all[i]
        if gem:
            ap, dur = gem[i]
            audio_parts.append((ap, dur))
            words = []
        elif voice != "none" and not offline:
            ap = tmp / f"v{i}.mp3"
            import re
            dur, words = voice_beat(re.sub(r"<[^>]+>", " ", spoken).strip(), voice, ap)
            audio_parts.append((ap, dur))
        else:
            dur, words = SILENT_BEAT, []
            audio_parts.append((None, dur))
        timings.append((words, dur))
        starts.append(t)
        t += dur + GAP
        ends.append(t)
    total = round(t - GAP + TAIL, 2)

    if post.get("engine") == "stickman":
        return render_stickman(post, pdir, tmp, info, beats, starts, total, timings, audio_parts)
    if post.get("engine") == "hype":
        return render_hype(post, pdir, tmp, info, beats, starts, round(total + 0.2, 2), timings, audio_parts)
    if post.get("engine") == "motion":
        return render_motion(post, pdir, tmp, info, beats, starts, ends, total, timings, audio_parts)

    # 2. footage: a cut on every beat, and beats longer than SPLIT seconds get a second shot.
    #    Per beat: beat["video_id"] (locked) > beat["video_query"] > clips from the post's video_query.
    n = len(beats)
    bounds = starts[1:] + [total]
    shots_per = [2 if bounds[i] - starts[i] > SPLIT else 1 for i in range(n)]
    clips = [[None] * k for k in shots_per]
    info["clips"] = []
    if not (offline or post.get("video_query") == "none"):
        locked = post.get("video_ids") or ([post["video_id"]] * sum(shots_per) if post.get("video_id") else [])
        flat = [(i, j) for i in range(n) for j in range(shots_per[i])]
        need = [(i, j) for (i, j) in flat if not beats[i].get("video_query") and not beats[i].get("video_id")
                and not (flat.index((i, j)) < len(locked) and locked[flat.index((i, j))])]
        pool = pixabay_videos(post["video_query"], used, len(need)) if need else []
        per_beat = {}
        for k, (i, j) in enumerate(flat):
            vid = (locked[k] if k < len(locked) else None) or (beats[i].get("video_id") if j == 0 else None)
            if vid:
                c = pixabay_video_by_id(vid)
            elif beats[i].get("video_query"):
                if i not in per_beat:
                    try:
                        per_beat[i] = pixabay_videos(beats[i]["video_query"], used, shots_per[i])
                    except RuntimeError:
                        per_beat[i] = pixabay_videos(post["video_query"], used, shots_per[i])
                c = per_beat[i][j % len(per_beat[i])]
            else:
                c = pool[need.index((i, j)) % len(pool)]
            path = tmp / f"src{i}_{j}.mp4"
            if not path.exists():
                path.write_bytes(c[0])
            used.add("v" + c[1])
            clips[i][j] = path
            info["clips"].append({"pixabay_id": c[1], "page": c[2]})
        info["video"] = {"pixabay_id": info["clips"][0]["pixabay_id"], "page": info["clips"][0]["page"],
                         "query": post["video_query"]}
        info["video_ids"] = [c["pixabay_id"] for c in info["clips"]]
    else:
        g = tmp / "grad.mp4"
        placeholder_video(g, total)
        clips = [[g] * k for k in shots_per]
    # scenes: (clip, start, length, is_beat_cut)
    scenes = []
    for i in range(n):
        L = bounds[i] - starts[i]
        if shots_per[i] == 2:
            h = round(L * 0.5, 3)
            scenes += [(clips[i][0], starts[i], h, True), (clips[i][1], starts[i] + h, round(L - h, 3), False)]
        else:
            scenes.append((clips[i][0], starts[i], round(L, 3), True))

    # 3. overlays
    mode = post.get("captions", "beats")  # switch default to "words" once approved
    info["captions"] = mode
    frame_overlay().save(tmp / "frame.png")
    if mode == "words":
        caps, segs = caption_track(beats, starts, ends, total, timings, tmp)
        info["word_sync"] = [("exact" if len(w) == len((b["text"] + " " + b.get("highlight", "")).split())
                              else "estimated" if w else "none") for (w, _), b in zip(timings, beats)]
    else:
        for i, b in enumerate(beats):
            beat_overlay(b, i == 0).save(tmp / f"b{i}.png")

    # 4. voice track: beats placed at their start times
    voice_wav = tmp / "voice.wav"
    inputs, filt = [], []
    real = [(i, p) for i, (p, _) in enumerate(audio_parts) if p]
    if real:
        for k, (i, p) in enumerate(real):
            inputs += ["-i", str(p)]
            ms = int(starts[i] * 1000)
            filt.append(f"[{k}:a]adelay={ms}|{ms}[a{k}]")
        mix = "".join(f"[a{k}]" for k in range(len(real)))
        filt.append(f"{mix}amix=inputs={len(real)}:normalize=0,apad,atrim=0:{total}[out]")
        run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]",
             "-ar", "44100", "-ac", "2", str(voice_wav)])
    else:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo", "-t", str(total), str(voice_wav)])

    # 4b. sound effects: a whoosh on every cut, a low hit when the payoff lands
    if post.get("sfx", True) and real:
        parts, labels = [], []
        for i in range(1, len(beats)):
            ms = max(0, int((starts[i] - 0.25) * 1000))
            parts.append(f"anoisesrc=d=0.5:c=pink:a=0.6,highpass=f=500,lowpass=f=6000,"
                         f"afade=t=in:d=0.3,afade=t=out:st=0.3:d=0.2,volume=0.30,"
                         f"aformat=sample_rates=44100:channel_layouts=stereo,adelay={ms}|{ms}[x{i}]")
            labels.append(f"[x{i}]")
        if beats[-1].get("highlight"):
            ms = int((starts[-1] + max(0.3, timings[-1][1] * 0.55)) * 1000)
            if timings[-1][0]:  # land exactly on the first payoff word
                ms = int((starts[-1] + timings[-1][0][len(beats[-1]["text"].split())][0]) * 1000) \
                    if len(timings[-1][0]) > len(beats[-1]["text"].split()) else ms
            parts.append(f"sine=f=55:d=0.7,afade=t=out:st=0:d=0.7,volume=0.9,"
                         f"aformat=sample_rates=44100:channel_layouts=stereo,adelay={ms}|{ms}[xh]")
            labels.append("[xh]")
        if labels:
            sfx_voice = tmp / "voice_sfx.wav"
            run(["ffmpeg", "-y", "-i", str(voice_wav), "-filter_complex",
                 ";".join(parts) + f";[0:a]{''.join(labels)}amix=inputs={len(labels) + 1}:normalize=0:duration=first[out]",
                 "-map", "[out]", "-ar", "44100", "-ac", "2", str(sfx_voice)])
            voice_wav = sfx_voice

    # 5. music under the voice
    track = pick_music(post.get("music", "auto"))
    final_audio = tmp / "audio.m4a"
    if track:
        info["music"] = track.name
        vol = "0.10" if real else "0.7"
        run(["ffmpeg", "-y", "-i", str(voice_wav), "-stream_loop", "-1", "-i", str(track), "-filter_complex",
             f"[1:a]volume={vol},afade=t=in:d=0.6,afade=t=out:st={max(0, total - 1.2)}:d=1.2[m];"
             f"[0:a]loudnorm=I=-16:TP=-2,aresample=44100,asplit=2[vo][sc];[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[md];"
             f"[vo][md]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
             "-map", "[out]", "-t", str(total), "-c:a", "aac", "-b:a", "160k", str(final_audio)])
    else:
        run(["ffmpeg", "-y", "-i", str(voice_wav), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
             "-c:a", "aac", "-b:a", "160k", str(final_audio)])

    # 6. video: one scene per beat (punch-in at the cut, then a slow push or pull),
    #    joined, then the constant layer and the text (beats slide up into place).
    inputs, chain = [], []
    for q, (clip, s0, L, _) in enumerate(scenes):
        # skip the first second (many clips fade in from black)
        off = 1.0 if q == 0 or clip != scenes[q - 1][0] else round(1.0 + scenes[q - 1][2] + 0.5, 2)
        inputs += ["-stream_loop", "-1", "-ss", f"{off:.2f}", "-i", str(clip)]
        punch = "0.10*max(0,1-on/8)"
        drift = "1+0.0016*on" if q % 2 == 0 else "1.09-0.0016*on"
        z = f"max(1,{drift}+{punch})"
        chain.append(f"[{q}:v]scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,fps={FPS},"
                     f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
                     f"trim=duration={L},setpts=PTS-STARTPTS,setsar=1,eq=saturation=0.85[s{q}]")
    n_sc = len(scenes)
    chain.append("".join(f"[s{q}]" for q in range(n_sc)) + f"concat=n={n_sc}:v=1:a=0[base]")
    k = n_sc
    inputs += ["-loop", "1", "-i", str(tmp / "frame.png")]
    chain.append(f"[base][{k}:v]overlay=0:0:shortest=0[v0]")
    k += 1
    last = "v0"
    if mode == "words":
        inputs += ["-i", str(caps)]
        chain.append(f"[v0][{k}:v]overlay=0:0:eof_action=repeat[v1]")
        k += 1
        last = "v1"
    else:
        for i in range(n):
            inputs += ["-loop", "1", "-i", str(tmp / f"b{i}.png")]
            s0, e = starts[i], bounds[i]
            if i == 0:  # hook visible from frame 1
                chain.append(f"[{k}:v]format=rgba[o{i}]")
                ypos = "0"
            else:
                chain.append(f"[{k}:v]format=rgba,fade=t=in:st={s0:.2f}:d=0.2:alpha=1[o{i}]")
                ypos = f"'if(lt(t-{s0:.2f},0.3),60*(1-(t-{s0:.2f})/0.3),0)'"
            chain.append(f"[{last}][o{i}]overlay=x=0:y={ypos}:enable='between(t,{s0:.2f},{e:.2f})'[v{i + 1}]")
            last = f"v{i + 1}"
            k += 1
    audio_idx = k
    part = pdir / "reel.part.mp4"
    out = pdir / "reel.mp4"
    run(["ffmpeg", "-y", *inputs, "-i", str(final_audio), "-filter_complex", ";".join(chain),
         "-map", f"[{last}]", "-map", f"{audio_idx}:a", "-t", str(total),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "copy", "-movflags", "+faststart", str(part)])
    part.rename(out)

    # 7. review frames: one per shot (frame-01.jpg ...), so every piece of footage gets checked
    files = [out]
    for q, (_, s0, L, _) in enumerate(scenes):
        ts = s0 + min(1.0, L / 2)
        fp = pdir / f"frame-{q + 1:02d}.jpg"
        run(["ffmpeg", "-y", "-ss", f"{ts:.2f}", "-i", str(out), "-frames:v", "1", "-q:v", "3", str(fp)])
        files.append(fp)
    info["shots"] = [{"frame": f"frame-{q + 1:02d}.jpg", "beat": next(i for i in range(n) if starts[i] <= s0 + 0.01
                      and (i == n - 1 or starts[i + 1] > s0 + 0.01)) + 1, "start": round(s0, 2)}
                     for q, (_, s0, L, _) in enumerate(scenes)]
    shutil.rmtree(tmp, ignore_errors=True)
    info["duration"] = total
    return files, info
