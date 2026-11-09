"""Stickman Reels ("engine": "stickman"): a minimalist white line-art stickman acting out each beat
on a dark background, captions word by word with red keywords. Drawn frame by frame with cairo.

Each beat: {"text": "...", "red": "word(s) in text shown in red", "scene": "<scene>", "say": optional,
            "clock": "05:30" (wake scene only, optional)}
Scenes: wake, commute, desk, home, stress, phone, laptop, walk, run, stairs, money, think, face.
"""
import math, subprocess
from pathlib import Path
import cairo
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fabrika" / "fonts"
W, H, FPS = 1080, 1920, 30
BG = (0.17, 0.17, 0.19)
LINE = (0.62, 0.62, 0.66)
FILL = (0.30, 0.30, 0.33)
WHITE = (0.95, 0.95, 0.95)
RED = (0.91, 0.22, 0.31)
RED255 = (232, 56, 79, 255)
FLOOR = 1080
S = 1.45
HANDLE = "@suksesishqip"
SCENES_LIST = ("wake", "commute", "desk", "home", "stress", "phone", "laptop", "walk", "run",
               "stairs", "money", "think", "face")


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


# ---------- poses (relative to the hip, facing right; y negative is up) ----------
STAND = dict(neck=(0, -110), head=(0, -152), elb1=(8, -60), hand1=(10, -12),
             elb2=(-6, -60), hand2=(-8, -12), knee1=(4, 55), foot1=(6, 110),
             knee2=(-4, 55), foot2=(-6, 110))
SLUMP = dict(STAND, neck=(10, -104), head=(32, -132), elb1=(16, -55), hand1=(20, -8),
             elb2=(4, -55), hand2=(6, -8))
SIT = dict(STAND, knee1=(55, 2), foot1=(58, 60), knee2=(50, 2), foot2=(52, 60))
SIT_DESK = dict(SIT, neck=(12, -106), head=(40, -128), elb1=(50, -70), hand1=(95, -72),
                elb2=(44, -66), hand2=(88, -66))
SIT_PHONE = dict(SIT, neck=(8, -106), head=(30, -132), elb1=(40, -48), hand1=(52, -78),
                 elb2=(34, -46), hand2=(48, -74))
BED = dict(STAND, knee1=(55, 0), foot1=(112, 0), knee2=(55, 0), foot2=(112, 0))
HEAD_HAND = dict(SLUMP, elb1=(66, -92), hand1=(44, -146))
CHIN = dict(STAND, neck=(2, -110), head=(6, -152), elb1=(34, -70), hand1=(26, -122),
            elb2=(20, -66), hand2=(32, -70))
FRONT = dict(STAND, elb1=(22, -60), hand1=(26, -14), elb2=(-22, -60), hand2=(-26, -14),
             knee1=(14, 55), foot1=(22, 110), knee2=(-14, 55), foot2=(-22, 110))


def mix(p, q, t):
    return {k: (lerp(p[k][0], q[k][0], t), lerp(p[k][1], q[k][1], t)) for k in p}


def walk(base, t, speed=1.6, stride=1.0, carry=True):
    ph = math.sin(t * math.pi * 2 * speed)
    p = dict(base)
    l1, l2 = max(0, ph) * 14, max(0, -ph) * 14
    p.update(knee1=(22 * ph * stride, 55 - l1), foot1=(40 * ph * stride, 110 - l1 * 0.6),
             knee2=(-22 * ph * stride, 55 - l2), foot2=(-40 * ph * stride, 110 - l2 * 0.6))
    if not carry:
        p.update(elb1=(14 * ph, -60), hand1=(26 * ph, -14))
    p.update(elb2=(-14 * ph, -60), hand2=(-26 * ph, -14))
    return p, abs(math.cos(t * math.pi * 2 * speed)) * 4


def run_pose(t, speed=2.6):
    ph = math.sin(t * math.pi * 2 * speed)
    p = dict(STAND, neck=(22, -106), head=(36, -146))
    p.update(knee1=(40 * ph, 50 - max(0, ph) * 24), foot1=(30 * ph - 12, 108 - max(0, ph) * 40),
             knee2=(-40 * ph, 50 - max(0, -ph) * 24), foot2=(-30 * ph - 12, 108 - max(0, -ph) * 40),
             elb1=(20 - 24 * ph, -72), hand1=(36 - 30 * ph, -50),
             elb2=(20 + 24 * ph, -72), hand2=(36 + 30 * ph, -50))
    return p, abs(math.cos(t * math.pi * 2 * speed)) * 10


def rot(pt, a):
    c, s = math.cos(a), math.sin(a)
    return (pt[0] * c - pt[1] * s, pt[0] * s + pt[1] * c)


def stick(ctx, x, y, pose, facing=1, upper_rot=0.0, briefcase=False, front=False):
    P = {}
    for k, v in pose.items():
        if k in ("neck", "head", "elb1", "hand1", "elb2", "hand2"):
            v = rot(v, upper_rot)
        P[k] = (x + v[0] * S * facing, y + v[1] * S)
    ctx.set_source_rgb(*WHITE)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(13)
    hip = (x, y)
    for chain in (("neck", "elb2", "hand2"), (None, "knee2", "foot2"), (None, "knee1", "foot1"),
                  ("SPINE",), ("neck", "elb1", "hand1")):
        if chain == ("SPINE",):
            ctx.move_to(*hip); ctx.line_to(*P["neck"]); ctx.stroke()
            continue
        ctx.move_to(*(hip if chain[0] is None else P[chain[0]]))
        for j in chain[1:]:
            ctx.line_to(*P[j])
        ctx.stroke()
    if briefcase:
        hx, hy = P["hand2"]
        ctx.rectangle(hx - 42, hy + 8, 84, 62)
        ctx.set_source_rgb(*FILL); ctx.fill_preserve()
        ctx.set_source_rgb(*WHITE); ctx.set_line_width(6); ctx.stroke()
        ctx.move_to(hx - 14, hy + 8); ctx.line_to(hx - 14, hy); ctx.line_to(hx + 14, hy)
        ctx.line_to(hx + 14, hy + 8); ctx.stroke()
    hx, hy = P["head"]
    ctx.arc(hx, hy, 34, 0, 2 * math.pi); ctx.set_source_rgb(*WHITE); ctx.fill()
    ctx.set_source_rgb(*BG)
    if front:
        for dx in (-11, 11):
            ctx.arc(hx + dx, hy - 2, 5.5, 0, 2 * math.pi); ctx.fill()
    else:
        ex, ey = rot((13, -3), upper_rot * 0.6)
        ctx.arc(hx + ex * facing, hy + ey, 6.5, 0, 2 * math.pi); ctx.fill()
    return P


# ---------- props ----------
def stroke(ctx, w=6, col=LINE):
    ctx.set_source_rgb(*col); ctx.set_line_width(w); ctx.stroke()


def filled(ctx, w=6):
    ctx.set_source_rgb(*FILL); ctx.fill_preserve(); stroke(ctx, w)


def floor(ctx, y=FLOOR):
    ctx.move_to(-300, y); ctx.line_to(W + 300, y); stroke(ctx, 6)


def rr(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def door(ctx, x, w=190, h=420, open_=0.0):
    ctx.rectangle(x - 12, FLOOR - h - 12, w + 24, h + 12); stroke(ctx)
    dw = w * (1 - 0.75 * open_)
    ctx.rectangle(x, FLOOR - h, dw, h); filled(ctx, 5)
    ctx.arc(x + dw - 28, FLOOR - h / 2, 10, 0, 2 * math.pi); stroke(ctx, 5)


def bed(ctx):
    ctx.move_to(180, FLOOR); ctx.line_to(180, FLOOR - 230); stroke(ctx, 7)
    ctx.move_to(880, FLOOR); ctx.line_to(880, FLOOR - 130); stroke(ctx, 7)
    ctx.rectangle(180, FLOOR - 150, 700, 50); filled(ctx)
    rr(ctx, 205, FLOOR - 190, 150, 40, 20); stroke(ctx)


def desk(ctx, x, monitor=True):
    ctx.rectangle(x, FLOOR - 190, 330, 18); filled(ctx)
    for lx in (x + 20, x + 310):
        ctx.move_to(lx, FLOOR - 172); ctx.line_to(lx, FLOOR); stroke(ctx)
    if monitor:
        ctx.rectangle(x + 150, FLOOR - 340, 150, 110); filled(ctx)
        ctx.move_to(x + 225, FLOOR - 230); ctx.line_to(x + 225, FLOOR - 190); stroke(ctx)


def chair(ctx, x, back_left=True):
    ctx.move_to(x - 60, FLOOR - 150); ctx.line_to(x + 60, FLOOR - 150); stroke(ctx, 7)
    for lx in (x - 50, x + 50):
        ctx.move_to(lx, FLOOR - 150); ctx.line_to(lx, FLOOR); stroke(ctx)
    bx = x - 60 if back_left else x + 60
    ctx.move_to(bx, FLOOR - 150); ctx.line_to(bx, FLOOR - 300); stroke(ctx, 7)


def wall_clock(ctx, x, y, r, t, speed):
    ctx.arc(x, y, r, 0, 2 * math.pi); stroke(ctx, 7, WHITE)
    a1 = t * speed * 2 * math.pi - math.pi / 2
    a2 = a1 / 12 + 0.6
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x, y); ctx.line_to(x + math.cos(a1) * r * 0.78, y + math.sin(a1) * r * 0.78); stroke(ctx, 6, WHITE)
    ctx.move_to(x, y); ctx.line_to(x + math.cos(a2) * r * 0.5, y + math.sin(a2) * r * 0.5); stroke(ctx, 8, WHITE)


def lamp(ctx, x):
    ctx.move_to(x, 0); ctx.line_to(x, FLOOR - 620); stroke(ctx, 4)
    ctx.move_to(x - 25, FLOOR - 620); ctx.line_to(x + 25, FLOOR - 620); ctx.line_to(x + 55, FLOOR - 575)
    ctx.line_to(x - 55, FLOOR - 575); ctx.close_path(); stroke(ctx)


def shelf(ctx, x):
    ctx.rectangle(x, FLOOR - 720, 200, 330); stroke(ctx)
    for yy in (FLOOR - 610, FLOOR - 500):
        ctx.move_to(x, yy); ctx.line_to(x + 200, yy); stroke(ctx, 5)


def window(ctx, x, y, w=240, h=280, moon=False):
    ctx.rectangle(x, y, w, h); stroke(ctx)
    ctx.move_to(x + w / 2, y); ctx.line_to(x + w / 2, y + h); stroke(ctx, 5)
    ctx.move_to(x, y + h / 2); ctx.line_to(x + w, y + h / 2); stroke(ctx, 5)
    if moon:
        ctx.arc(x + w * 0.72, y + h * 0.26, 26, 0, 2 * math.pi); ctx.set_source_rgb(*WHITE); ctx.fill()
        ctx.arc(x + w * 0.72 - 12, y + h * 0.26 - 6, 24, 0, 2 * math.pi); ctx.set_source_rgb(*BG); ctx.fill()


def big_text(ctx, txt, y, size=190, col=RED):
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents(txt)
    ctx.set_source_rgb(*col); ctx.move_to((W - e.x_advance) / 2, y); ctx.show_text(txt)


def zoomed(ctx, t, d, z0=1.0, z1=1.05, cy=FLOOR - 200):
    z = lerp(z0, z1, min(1, t / max(d, 0.1)))
    ctx.translate(W / 2, cy); ctx.scale(z, z); ctx.translate(-W / 2, -cy)


STAND_Y = FLOOR - 110 * S


# ---------- scenes: fn(ctx, t, d, beat, k) where k = beat index (for variety) ----------
def sc_wake(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d); bed(ctx)
    up = ease((t - 0.5) / 0.7)
    pose = mix(BED, dict(BED, neck=(8, -108), head=(24, -146)), ease((t - 1.3) / 0.5))
    stick(ctx, 560, FLOOR - 166, pose, 1, upper_rot=lerp(-math.pi / 2, -0.05, up))
    ctx.restore()
    if b.get("clock"):
        c = b["clock"]
        big_text(ctx, c if int(t * 2) % 2 == 0 else c.replace(":", " "), 470)


def sc_commute(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d, 1.04, 1.0)
    floor(ctx)
    door(ctx, 760, open_=ease((t - 0.2) / 0.4))
    x = lerp(140, 800, min(1, t / max(d, 0.1)))
    p, bob = walk(STAND, t)
    stick(ctx, x, STAND_Y - bob, p, 1, briefcase=True)
    ctx.restore()


def sc_desk(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d)
    floor(ctx); wall_clock(ctx, W / 2, 360, 95, t, 1.6)
    chair(ctx, 380); desk(ctx, 470)
    p = dict(SIT_DESK)
    tap = math.sin(t * 22) * 4
    p["hand1"] = (p["hand1"][0], p["hand1"][1] + tap)
    p["hand2"] = (p["hand2"][0], p["hand2"][1] - tap)
    stick(ctx, 380, FLOOR - 160, p, 1)
    ctx.restore()


def sc_home(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d)
    floor(ctx); door(ctx, 70, open_=1 - ease((t - 1.3) / 0.4)); lamp(ctx, 720); shelf(ctx, 860)
    ctx.rectangle(600, FLOOR - 150, 240, 14); stroke(ctx)
    for lx in (620, 820):
        ctx.move_to(lx, FLOOR - 136); ctx.line_to(lx, FLOOR); stroke(ctx)
    chair(ctx, 530)
    x = lerp(150, 330, min(t, 1.6) / 1.6)
    if t < 1.6:
        p, bob = walk(SLUMP, t, 1.3)
    else:
        p, bob = mix(SLUMP, dict(SLUMP, head=(36, -122)), ease((t - 1.8) / 0.6)), 0
    stick(ctx, x, STAND_Y - bob, p, 1, briefcase=True)
    ctx.restore()


def sc_stress(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d, 1.0, 1.08)
    floor(ctx); wall_clock(ctx, W / 2, 470, 80, t, 2.5)
    ctx.rectangle(760, FLOOR - 170, 170, 170); stroke(ctx)
    ctx.rectangle(820, FLOOR - 330, 150, 160); stroke(ctx)
    stick(ctx, 460, STAND_Y, mix(SLUMP, HEAD_HAND, ease((t - 0.3) / 0.5)), 1)
    ctx.restore()


def sc_phone(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d, 1.0, 1.07)
    floor(ctx); window(ctx, 640, FLOOR - 640, moon=True)
    # couch
    rr(ctx, 230, FLOOR - 170, 520, 80, 20); filled(ctx)
    rr(ctx, 230, FLOOR - 300, 520, 140, 24); stroke(ctx)
    ctx.move_to(260, FLOOR - 90); ctx.line_to(260, FLOOR); stroke(ctx)
    ctx.move_to(720, FLOOR - 90); ctx.line_to(720, FLOOR); stroke(ctx)
    p = dict(SIT_PHONE)
    P = stick(ctx, 420, FLOOR - 196, p, 1)
    # glowing phone; thumb scrolls
    hx, hy = P["hand1"]
    glow = cairo.RadialGradient(hx + 10, hy - 20, 5, hx + 10, hy - 20, 110)
    glow.add_color_stop_rgba(0, 0.8, 0.85, 1.0, 0.25); glow.add_color_stop_rgba(1, 0.8, 0.85, 1.0, 0)
    ctx.set_source(glow); ctx.paint()
    ctx.save(); ctx.translate(hx + 6, hy - 22); ctx.rotate(-0.5)
    rr(ctx, -16, -30, 32, 58, 6); ctx.set_source_rgb(0.85, 0.88, 0.95); ctx.fill()
    for i in range(3):
        yy = -22 + ((t * 40 + i * 18) % 50)
        ctx.rectangle(-10, yy, 20, 4); ctx.set_source_rgb(*BG); ctx.fill()
    ctx.restore()
    ctx.restore()


def sc_laptop(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d)
    ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(0, 0, 0, 0.18); ctx.fill()
    floor(ctx); window(ctx, 120, FLOOR - 700, moon=True)
    chair(ctx, 380); desk(ctx, 470, monitor=False)
    # laptop + desk lamp
    ctx.move_to(560, FLOOR - 192); ctx.line_to(700, FLOOR - 192); stroke(ctx, 7, WHITE)
    ctx.move_to(700, FLOOR - 192); ctx.line_to(745, FLOOR - 300); stroke(ctx, 7, WHITE)
    ctx.move_to(770, FLOOR - 192); ctx.line_to(770, FLOOR - 320); ctx.line_to(720, FLOOR - 380); stroke(ctx, 6)
    g = cairo.RadialGradient(700, FLOOR - 300, 5, 700, FLOOR - 250, 260)
    g.add_color_stop_rgba(0, 1, 0.92, 0.7, 0.22); g.add_color_stop_rgba(1, 1, 0.92, 0.7, 0)
    ctx.set_source(g); ctx.paint()
    p = dict(SIT_DESK, neck=(6, -108), head=(22, -148), hand1=(98, -66), hand2=(90, -62))
    tap = math.sin(t * 26) * 4
    p["hand1"] = (p["hand1"][0], p["hand1"][1] + tap)
    p["hand2"] = (p["hand2"][0], p["hand2"][1] - tap)
    stick(ctx, 380, FLOOR - 160, p, 1)
    ctx.restore()


def sc_walk(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d, 1.0, 1.04)
    floor(ctx)
    off = (t * 260) % 520
    for i in range(-1, 4):  # street lamps passing by
        x = i * 520 - off + 200
        ctx.move_to(x, FLOOR); ctx.line_to(x, FLOOR - 560); ctx.line_to(x + 60, FLOOR - 560); stroke(ctx, 6)
        ctx.arc(x + 70, FLOOR - 548, 12, 0, 2 * math.pi); stroke(ctx, 5)
    p, bob = walk(SLUMP if b.get("mood") == "sad" else STAND, t, 1.4, carry=False)
    stick(ctx, W / 2 - 40, STAND_Y - bob, p, 1)
    ctx.restore()


def sc_run(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d, 1.02, 1.0)
    floor(ctx)
    off = (t * 900) % 360
    for i in range(-1, 5):
        x = i * 360 - off
        ctx.move_to(x, FLOOR + 40); ctx.line_to(x + 120, FLOOR + 40); stroke(ctx, 4)
    for i, yy in enumerate((FLOOR - 260, FLOOR - 180, FLOOR - 100)):
        x0 = W / 2 - 220 - ((t * 700 + i * 90) % 200)
        ctx.move_to(x0, yy); ctx.line_to(x0 + 110, yy); stroke(ctx, 4)
    p, bob = run_pose(t)
    stick(ctx, W / 2, STAND_Y - bob, p, 1)
    ctx.restore()


def sc_stairs(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d, 1.0, 1.05)
    step_w, step_h, n, x0 = 140, 80, 6, 60
    ctx.move_to(-100, FLOOR)
    for i in range(n):
        ctx.line_to(x0 + i * step_w, FLOOR - i * step_h)
        ctx.line_to(x0 + i * step_w, FLOOR - (i + 1) * step_h)
    ctx.line_to(W + 100, FLOOR - n * step_h); stroke(ctx)
    top = FLOOR - n * step_h
    fx = x0 + (n - 1) * step_w + 120
    ctx.move_to(fx, top); ctx.line_to(fx, top - 170); stroke(ctx, 6, WHITE)
    ctx.move_to(fx, top - 170); ctx.line_to(fx + 80, top - 145); ctx.line_to(fx, top - 120)
    ctx.close_path(); ctx.set_source_rgb(*RED); ctx.fill()
    x = lerp(x0 - 40, x0 + 3.6 * step_w, min(1, t / max(d, 0.1)))
    lvl = max(0.0, (x - x0) / step_w + 1)            # step under the hip
    y = FLOOR - (int(lvl) + ease((lvl % 1 - 0.75) / 0.25)) * step_h - 110 * S
    p, bob = walk(STAND, t, 1.2, carry=False)
    stick(ctx, x, y - bob, p, 1)
    ctx.restore()


def sc_money(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d)
    floor(ctx)
    n = int(lerp(2, 12, ease(t / max(d * 0.8, 0.1))))
    for i in range(n):
        y = FLOOR - 22 - i * 26
        ctx.save(); ctx.translate(640, y); ctx.scale(1, 0.32)
        ctx.arc(0, 0, 90, 0, 2 * math.pi); ctx.restore(); filled(ctx, 5)
    # a coin dropping onto the stack
    ft = (t * 1.6) % 1
    cy = lerp(300, FLOOR - 22 - n * 26, ease(ft))
    ctx.arc(640, cy, 30, 0, 2 * math.pi); ctx.set_source_rgb(*RED); ctx.fill()
    stick(ctx, 370, STAND_Y, mix(STAND, CHIN, ease((t - 0.4) / 0.6)), 1)
    ctx.restore()


def sc_think(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d, 1.0, 1.06)
    floor(ctx)
    stick(ctx, W / 2 - 60, STAND_Y, mix(STAND, CHIN, ease((t - 0.2) / 0.5)), 1)
    a = ease((t - 0.7) / 0.4)
    if a > 0:
        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(170)
        ctx.set_source_rgba(*RED, a)
        ctx.move_to(W / 2 + 40, FLOOR - 470 - 20 * a + math.sin(t * 3) * 8); ctx.show_text("?")
    ctx.restore()


def sc_face(ctx, t, d, b, k):
    ctx.save(); zoomed(ctx, t, d, 1.0, 1.06)
    g = ease((t - 0.8) / 1.0)
    rg = cairo.RadialGradient(W / 2, FLOOR - 200, 10, W / 2, FLOOR - 200, 520)
    rg.add_color_stop_rgba(0, *RED, 0.22 * g); rg.add_color_stop_rgba(1, *RED, 0)
    ctx.set_source(rg); ctx.paint()
    floor(ctx)
    if t <= 0.5:
        stick(ctx, W / 2, STAND_Y, SLUMP, 1)
    else:
        up = ease((t - 0.6) / 0.6)
        p = dict(FRONT, head=(0, lerp(-128, -152, up)), neck=(0, lerp(-102, -110, up)))
        stick(ctx, W / 2, STAND_Y, p, 1, front=True)
    ctx.restore()


SCENES = {"wake": sc_wake, "commute": sc_commute, "desk": sc_desk, "home": sc_home, "stress": sc_stress,
          "phone": sc_phone, "laptop": sc_laptop, "walk": sc_walk, "run": sc_run, "stairs": sc_stairs,
          "money": sc_money, "think": sc_think, "face": sc_face}


# ---------- captions (PIL, repo fonts) ----------
def _font(size):
    return ImageFont.truetype(str(FONTS / "i700.ttf"), size)


def caption_layout(text, red):
    """Words with colour flags, wrapped into lines that fit."""
    words = text.split()
    red_words = set()
    if red:
        rw = red.split()
        for i in range(len(words) - len(rw) + 1):
            if [w.strip(".,!?:;…").lower() for w in words[i:i + len(rw)]] == \
               [w.strip(".,!?:;…").lower() for w in rw]:
                red_words.update(range(i, i + len(rw)))
                break
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    for size in range(72, 46, -4):
        f = _font(size)
        sp = d.textlength(" ", font=f)
        lines, cur, cw = [], [], 0
        for i, w in enumerate(words):
            ww = d.textlength(w, font=f)
            if cur and cw + sp + ww > W - 160:
                lines.append(cur); cur, cw = [], 0
            cw += (sp if cur else 0) + ww
            cur.append(i)
        lines.append(cur)
        if len(lines) <= 3:
            break
    return words, red_words, lines, f


def caption_png(text, red, nvis, cache):
    key = (text, nvis)
    if key in cache:
        return cache[key]
    words, red_words, lines, f = caption_layout(text, red)
    img = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    sp = d.textlength(" ", font=f)
    step = int(f.size * 1.25)
    for li, line in enumerate(lines):
        tot = sum(d.textlength(words[i], font=f) for i in line) + sp * (len(line) - 1)
        x = (W - tot) / 2
        for i in line:
            if i < nvis:
                d.text((x, 20 + li * step), words[i], font=f,
                       fill=RED255 if i in red_words else (242, 242, 242, 255))
            x += d.textlength(words[i], font=f) + sp
    surf = pil_to_surface(img)
    cache[key] = surf
    return surf


def pil_to_surface(img):
    r, g, b, a = img.split()
    data = bytearray(Image.merge("RGBA", (b, g, r, a)).tobytes())  # premultiplication skipped: text is opaque
    return cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, img.width, img.height, img.width * 4)


def handle_png():
    img = Image.new("RGBA", (W, 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(str(FONTS / "i400.ttf"), 34)
    d.text(((W - d.textlength(HANDLE, font=f)) / 2, 10), HANDLE, font=f, fill=(150, 150, 158, 255))
    return pil_to_surface(img)


# ---------- main ----------
def render_video(beats, starts, bounds, total, voiced, out_mp4):
    """Silent stickman video. voiced[i] = seconds of speech in beat i (for word timing)."""
    cache, handle = {}, handle_png()
    n_frames = int(round(total * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                          "-pix_fmt", "yuv420p", str(out_mp4)], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    bi = 0
    for fi in range(n_frames):
        tt = fi / FPS
        while bi + 1 < len(beats) and tt >= starts[bi + 1]:
            bi += 1
        b = beats[bi]
        t, d = tt - starts[bi], bounds[bi] - starts[bi]
        ctx = cairo.Context(surf)
        ctx.set_source_rgb(*BG); ctx.paint()
        scene = b.get("scene") if b.get("scene") in SCENES else default_scene(bi, len(beats))
        SCENES[scene](ctx, t, d, b, bi)
        # captions: words appear as they're spoken (spread over the voiced span)
        words = b["text"].split()
        span = max(0.4, voiced[bi] * 0.9)
        nvis = len(words) if t >= span else int(len(words) * t / span) + 1
        ctx.set_source_surface(caption_png(b["text"], b.get("red", ""), nvis, cache), 0, 1150)
        ctx.paint()
        ctx.set_source_surface(handle, 0, 1390); ctx.paint_with_alpha(0.8)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg failed while encoding the stickman video")


def default_scene(i, n):
    if i == n - 1:
        return "face"
    return ("think", "walk", "desk", "stress", "laptop", "stairs")[i % 6]
