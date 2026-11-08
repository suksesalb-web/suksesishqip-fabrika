"""Render a Reel: stock footage + Albanian text beats + Albanian voice (+ music).

Queue entry (style "reel"):
  {"id": "p2", "style": "reel", "time": "12:00",
   "video_query": "man walking alone city street night",
   "voice": "sq-AL-AnilaNeural",            # or "none"
   "music": "auto",                          # a file in fabrika/music/, "auto" or "none"
   "beats": [{"text": "...", "highlight": "..."}, ...],   # 3-6 beats, first one is the hook
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
DEFAULT_VOICE = "sq-AL-AnilaNeural"
VOICE_RATE = "+6%"
GAP = 0.35          # silence between beats (s)
TAIL = 0.8          # hold after the last beat (s)
SILENT_BEAT = 3.0   # beat length when there is no voice (s)


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
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=VOICE_RATE).save(str(path))


def voice_beat(text, voice, path):
    asyncio.run(_tts(text, voice, path))
    return duration(path)


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
        hf, hl_lines, hstep = fit(d, beat["highlight"], "i800", 72, 48, maxw - 30, 300, 1.3)
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


# ---------- main ----------

def render_reel(post, pdir, used, offline=False):
    beats = post["beats"]
    voice = post.get("voice", DEFAULT_VOICE)
    tmp = Path(tempfile.mkdtemp())
    info = {"video": None, "music": None, "voice": voice}

    # 1. voice per beat -> timings
    starts, ends, t = [], [], 0.0
    audio_parts = []
    for i, b in enumerate(beats):
        spoken = b.get("say") or " ".join(x for x in (b["text"], b.get("highlight", "")) if x)
        if voice != "none" and not offline:
            ap = tmp / f"v{i}.mp3"
            dur = voice_beat(spoken, voice, ap)
            audio_parts.append((ap, dur))
        else:
            dur = SILENT_BEAT
            audio_parts.append((None, dur))
        starts.append(t)
        t += dur + GAP
        ends.append(t)
    total = round(t - GAP + TAIL, 2)

    # 2. footage, cropped/scaled to 1080x1920, darkened, looped to length
    src = tmp / "src.mp4"
    if offline:
        placeholder_video(src, total)
    else:
        if post.get("video_id"):  # locked: a reviewer kept this footage
            data, vid, page = pixabay_video_by_id(post["video_id"])
        else:
            data, vid, page = pixabay_video(post["video_query"], used)
        src.write_bytes(data)
        used.add("v" + vid)
        info["video"] = {"pixabay_id": vid, "page": page, "query": post["video_query"]}

    # 3. overlays
    frame_overlay().save(tmp / "frame.png")
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

    # 5. music under the voice
    track = pick_music(post.get("music", "auto"))
    final_audio = tmp / "audio.m4a"
    if track:
        info["music"] = track.name
        vol = "0.22" if real else "0.7"
        run(["ffmpeg", "-y", "-i", str(voice_wav), "-stream_loop", "-1", "-i", str(track), "-filter_complex",
             f"[1:a]volume={vol},afade=t=in:d=0.6,afade=t=out:st={max(0, total - 1.2)}:d=1.2[m];"
             f"[0:a][m]amix=inputs=2:normalize=0:duration=first[out]",
             "-map", "[out]", "-t", str(total), "-c:a", "aac", "-b:a", "160k", str(final_audio)])
    else:
        run(["ffmpeg", "-y", "-i", str(voice_wav), "-c:a", "aac", "-b:a", "160k", str(final_audio)])

    # 6. video: base + constant layer + beat layers (each fades in), then audio
    inputs = ["-stream_loop", "-1", "-i", str(src), "-loop", "1", "-i", str(tmp / "frame.png")]
    for i in range(len(beats)):
        inputs += ["-loop", "1", "-i", str(tmp / f"b{i}.png")]
    chain = [f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,"
             f"eq=saturation=0.85[base]",
             "[base][1:v]overlay=0:0:shortest=0[v0]"]
    last = "v0"
    for i in range(len(beats)):
        s, e = starts[i], ends[i] if i < len(beats) - 1 else total
        fade = "" if i == 0 else f",fade=t=in:st={s:.2f}:d=0.25:alpha=1"  # hook visible from frame 1
        chain.append(f"[{i + 2}:v]format=rgba{fade}[o{i}]")
        chain.append(f"[{last}][o{i}]overlay=0:0:enable='between(t,{s:.2f},{e:.2f})'[v{i + 1}]")
        last = f"v{i + 1}"
    part = pdir / "reel.part.mp4"
    out = pdir / "reel.mp4"
    run(["ffmpeg", "-y", *inputs, "-i", str(final_audio), "-filter_complex", ";".join(chain),
         "-map", f"[{last}]", "-map", f"{len(beats) + 2}:a", "-t", str(total),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "copy", "-movflags", "+faststart", str(part)])
    part.rename(out)

    # 7. review frames: middle of each beat
    files = [out]
    for i in range(len(beats)):
        e = ends[i] if i < len(beats) - 1 else total
        ts = starts[i] + min(1.2, (e - starts[i]) / 2)
        fp = pdir / f"frame-{i + 1:02d}.jpg"
        run(["ffmpeg", "-y", "-ss", f"{ts:.2f}", "-i", str(out), "-frames:v", "1", "-q:v", "3", str(fp)])
        files.append(fp)
    shutil.rmtree(tmp, ignore_errors=True)
    info["duration"] = total
    return files, info
