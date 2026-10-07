#!/usr/bin/env python3
"""Fix My Money renderer.

Usage:
  python3 render.py post.json OUT_DIR [--only carousel|reel]

post.json schema (see README.md for full detail):
{
  "date": "2026-09-28", "day": 1,
  "carousel": {"slides": [ {...}, ... ], "caption": "..."},
  "reel": {"scenes": [ {...}, ... ], "caption": "..."}
}
Rich text: **accent (mint)**  [[alert (red)]]  plain.
"""
import json, os, re, sys, math, subprocess, wave, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
sys.path.insert(0, HERE)
CFG = json.load(open(os.path.join(HERE, "config.json")))

NAVY = (11, 27, 43)
NAVY2 = (18, 40, 62)
CARD = (22, 48, 74)
WHITE = (244, 247, 250)
MUTED = (140, 163, 184)
MINT = (61, 220, 151)
RED = (255, 99, 99)
AMBER = (255, 196, 87)

_font_cache = {}
def F(weight, size):
    key = (weight, size)
    if key not in _font_cache:
        name = {"b": "Poppins-Bold.ttf", "m": "Poppins-Medium.ttf", "r": "Poppins-Regular.ttf"}[weight]
        _font_cache[key] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _font_cache[key]

SUBS = {"→": "›", "←": "‹", "’": "'", "‘": "'", "“": '"', "”": '"'}
def clean(s):
    for a, b in SUBS.items():
        s = s.replace(a, b)
    return s

# ---------------- rich text ----------------
def parse_rich(s, base=WHITE):
    s = clean(s)
    runs, pos = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*|\[\[(.+?)\]\]", s):
        if m.start() > pos:
            runs.append((s[pos:m.start()], base))
        runs.append((m.group(1), MINT) if m.group(1) is not None else (m.group(2), RED))
        pos = m.end()
    if pos < len(s):
        runs.append((s[pos:], base))
    return runs

def wrap_rich(text, font, max_w, base=WHITE):
    """Returns list of lines; each line = list of (word, color). Honors \n."""
    lines = []
    for para in clean(text).split("\n"):
        words = []
        for chunk, col in parse_rich(para, base):
            for i, w in enumerate(re.split(r"(\s+)", chunk)):
                if w and not w.isspace():
                    words.append((w, col))
        cur, cur_w = [], 0
        space = font.getlength(" ")
        for w, col in words:
            ww = font.getlength(w)
            add = ww if not cur else space + ww
            if cur and cur_w + add > max_w:
                lines.append(cur); cur, cur_w = [(w, col)], ww
            else:
                cur.append((w, col)); cur_w += add
        lines.append(cur)
    return lines

def line_width(line, font):
    if not line:
        return 0
    return sum(font.getlength(w) for w, _ in line) + font.getlength(" ") * (len(line) - 1)

def draw_lines(d, lines, font, x, y, lh, align="left", box_w=None, alpha=1.0, bg=NAVY):
    for line in lines:
        lw = line_width(line, font)
        cx = x if align == "left" else x + (box_w - lw) / 2
        for w, col in line:
            d.text((cx, y), w, font=font, fill=blend(col, bg, alpha))
            cx += font.getlength(w) + font.getlength(" ")
        y += lh
    return y

def fit_font(text, weight, max_size, min_size, max_w, max_lines):
    size = max_size
    while size > min_size:
        f = F(weight, size)
        if len(wrap_rich(text, f, max_w)) <= max_lines:
            return f
        size -= 4
    return F(weight, min_size)

def blend(c, bg, a):
    return tuple(int(bg[i] + (c[i] - bg[i]) * a) for i in range(3))

# ---------------- number helpers ----------------
NUM_RE = re.compile(r"(\d[\d,]*\.?\d*)")
def indian_group(n):
    s = str(int(n))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:]); head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts) + "," + tail

def count_text(s, frac):
    m = NUM_RE.search(s)
    if not m or frac >= 1:
        return s
    raw = m.group(1)
    dec = len(raw.split(".")[1]) if "." in raw else 0
    v = float(raw.replace(",", "")) * frac
    if dec:
        num = f"{v:.{dec}f}"
    else:
        num = indian_group(v) if "," in raw else str(int(v))
    return s[:m.start()] + num + s[m.end():]

# ---------------- chrome (header/footer) ----------------
def chrome(d, W, H, idx=None, total=None, footer=True):
    d.text((72, 64), CFG["brand"].upper(), font=F("b", 30), fill=MINT)
    if idx is not None:
        t = f"{idx}/{total}"
        d.text((W - 72 - F("m", 28).getlength(t), 66), t, font=F("m", 28), fill=MUTED)
    if footer:
        d.text((72, H - 84), CFG["handle"], font=F("m", 26), fill=MUTED)
        disc = "Education only. Not investment advice."
        d.text((W - 72 - F("r", 24).getlength(disc), H - 82), disc, font=F("r", 24), fill=MUTED)

def xray_stamp(d, x, y, text="X-RAY"):
    f = F("b", 28)
    w = f.getlength(text) + 36
    d.rounded_rectangle((x, y, x + w, y + 52), radius=10, outline=MINT, width=3)
    d.text((x + 18, y + 8), text, font=f, fill=MINT)

# ---------------- carousel ----------------
CW, CH = 1080, 1350
PAD = 88

def slide_img():
    img = Image.new("RGB", (CW, CH), NAVY)
    d = ImageDraw.Draw(img)
    # subtle grid
    for gx in range(0, CW, 90):
        d.line((gx, 0, gx, CH), fill=(15, 33, 51))
    for gy in range(0, CH, 90):
        d.line((0, gy, CW, gy), fill=(15, 33, 51))
    return img, d

def render_slide(s, idx, total):
    img, d = slide_img()
    chrome(d, CW, CH, idx, total)
    t = s.get("type", "point")
    maxw = CW - 2 * PAD
    if t == "cover":
        y = 250
        if s.get("stamp"):
            xray_stamp(d, PAD, 180, s["stamp"]); y = 280
        if s.get("kicker"):
            f = F("m", 36)
            y = draw_lines(d, wrap_rich(s["kicker"], f, maxw, MUTED), f, PAD, y, 52) + 30
        f = fit_font(s["title"], "b", 96, 60, maxw, 6)
        y = draw_lines(d, wrap_rich(s["title"], f, maxw), f, PAD, y, int(f.size * 1.18)) + 36
        if s.get("sub"):
            f2 = F("r", 38)
            draw_lines(d, wrap_rich(s["sub"], f2, maxw, MUTED), f2, PAD, y, 54)
        d.text((PAD, CH - 170), "Swipe  ›", font=F("b", 34), fill=MINT)
    elif t == "point":
        y = 210
        if s.get("n"):
            d.text((PAD, y), s["n"], font=F("b", 120), fill=MINT); y += 170
        f = fit_font(s["title"], "b", 68, 48, maxw, 4)
        y = draw_lines(d, wrap_rich(s["title"], f, maxw), f, PAD, y, int(f.size * 1.22)) + 30
        if s.get("body"):
            f2 = F("r", 38)
            draw_lines(d, wrap_rich(s["body"], f2, maxw, (205, 216, 228)), f2, PAD, y, 58)
    elif t == "stat":
        y = 230
        if s.get("title"):
            f = F("m", 40)
            y = draw_lines(d, wrap_rich(s["title"], f, maxw, MUTED), f, PAD, y, 56) + 30
        fb = fit_font(s["big"], "b", 200, 100, maxw, 1)
        col = {"mint": MINT, "red": RED, "amber": AMBER}.get(s.get("color", "mint"), MINT)
        d.text((PAD, y), clean(s["big"]), font=fb, fill=col); y += int(fb.size * 1.25)
        if s.get("label"):
            f = F("b", 50)
            y = draw_lines(d, wrap_rich(s["label"], f, maxw), f, PAD, y, 66) + 24
        if s.get("note"):
            f = F("r", 32)
            draw_lines(d, wrap_rich(s["note"], f, maxw, MUTED), f, PAD, y, 46)
    elif t == "bars":
        y = 210
        f = fit_font(s["title"], "b", 60, 44, maxw, 3)
        y = draw_lines(d, wrap_rich(s["title"], f, maxw), f, PAD, y, int(f.size * 1.22)) + 50
        bars = s["bars"]
        vmax = max(abs(b["value"]) for b in bars) or 1
        bh, gap = 64, 58
        for b in bars:
            d.text((PAD, y), clean(b["label"]), font=F("m", 34), fill=WHITE)
            y += 52
            w = max(8, int((maxw - 220) * abs(b["value"]) / vmax))
            col = RED if b.get("alert") else (MINT if b.get("highlight") else (70, 110, 145))
            d.rounded_rectangle((PAD, y, PAD + w, y + bh), radius=12, fill=col)
            d.text((PAD + w + 20, y + 8), clean(b.get("display", str(b["value"]))), font=F("b", 40), fill=WHITE)
            y += bh + gap - 20
        if s.get("note"):
            f = F("r", 30)
            draw_lines(d, wrap_rich(s["note"], f, maxw, MUTED), f, PAD, max(y + 10, CH - 260), 44)
    elif t == "list":
        y = 210
        f = fit_font(s["title"], "b", 64, 46, maxw, 3)
        y = draw_lines(d, wrap_rich(s["title"], f, maxw), f, PAD, y, int(f.size * 1.2)) + 44
        fi = F("r", 38) if len(s["items"]) <= 5 else F("r", 34)
        for i, it in enumerate(s["items"]):
            mark = s.get("marks", "check")
            if mark == "num":
                d.text((PAD, y), f"{i+1}", font=F("b", 40), fill=MINT)
            elif mark == "cross":
                d.text((PAD, y - 4), "×", font=F("b", 48), fill=RED)
            else:
                d.rounded_rectangle((PAD, y + 8, PAD + 34, y + 42), radius=8, outline=MINT, width=4)
            lines = wrap_rich(it, fi, maxw - 70, (215, 225, 235))
            y = draw_lines(d, lines, fi, PAD + 70, y, int(fi.size * 1.45)) + 26
    elif t == "table":
        y = 210
        f = fit_font(s["title"], "b", 60, 44, maxw, 3)
        y = draw_lines(d, wrap_rich(s["title"], f, maxw), f, PAD, y, int(f.size * 1.22)) + 40
        cols = s["columns"]; rows = s["rows"]
        cw = maxw / len(cols)
        d.rounded_rectangle((PAD - 16, y - 12, CW - PAD + 16, y + 64), radius=12, fill=CARD)
        for j, c in enumerate(cols):
            d.text((PAD + j * cw, y), clean(c), font=F("b", 32), fill=MINT)
        y += 90
        for r in rows:
            for j, c in enumerate(r):
                fnt = F("m", 34) if j == 0 else F("r", 34)
                lines = wrap_rich(str(c), fnt, cw - 20, WHITE if j == 0 else (215, 225, 235))
                draw_lines(d, lines, fnt, PAD + j * cw, y, 46)
            y += 46 * max(len(wrap_rich(str(c), F("r", 34), cw - 20)) for c in r) + 30
            d.line((PAD, y - 16, CW - PAD, y - 16), fill=(35, 60, 85), width=2)
        if s.get("note"):
            fn = F("r", 30)
            draw_lines(d, wrap_rich(s["note"], fn, maxw, MUTED), fn, PAD, max(y + 10, CH - 260), 44)
    elif t == "end":
        y = 330
        f = fit_font(s["title"], "b", 80, 54, maxw, 5)
        y = draw_lines(d, wrap_rich(s["title"], f, maxw), f, PAD, y, int(f.size * 1.2)) + 40
        if s.get("sub"):
            f2 = F("r", 38)
            y = draw_lines(d, wrap_rich(s["sub"], f2, maxw, MUTED), f2, PAD, y, 56) + 40
        d.text((PAD, CH - 250), "Save this  ·  Send it to someone who needs it", font=F("m", 32), fill=MINT)
    if s.get("source"):
        fs = F("r", 22)
        d.text((PAD, CH - 124), "Source: " + clean(s["source"]), font=fs, fill=(100, 125, 150))
    return img

def render_carousel(c, out):
    os.makedirs(out, exist_ok=True)
    n = len(c["slides"])
    paths = []
    for i, s in enumerate(c["slides"], 1):
        p = os.path.join(out, f"slide_{i:02d}.png")
        render_slide(s, i, n).save(p, optimize=True)
        paths.append(p)
    with open(os.path.join(out, "carousel_caption.txt"), "w") as fh:
        fh.write(c["caption"].strip() + "\n")
    return paths

# ---------------- reel ----------------
RW, RH, FPS = 1080, 1920, 30

def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3

def reel_bg(t):
    img = Image.new("RGB", (RW, RH), NAVY)
    d = ImageDraw.Draw(img)
    off = int((t * 30) % 120)
    for gx in range(-120, RW + 120, 120):
        d.line((gx + off, 0, gx + off, RH), fill=(15, 33, 51))
    for gy in range(-120, RH + 120, 120):
        d.line((0, gy + off, RW, gy + off), fill=(15, 33, 51))
    return img, d

def draw_reel_frame(scene, st, t_total, T, idx_total):
    """st = seconds into scene, t_total = seconds into reel."""
    img, d = reel_bg(t_total)
    # progress bar
    d.rectangle((0, 0, int(RW * t_total / T), 10), fill=MINT)
    d.text((80, 120), CFG["brand"].upper(), font=F("b", 38), fill=MINT)
    d.text((80, RH - 150), CFG["handle"], font=F("m", 30), fill=MUTED)
    disc = "Education only. Not advice."
    d.text((RW - 80 - F("r", 28).getlength(disc), RH - 148), disc, font=F("r", 28), fill=MUTED)
    typ = scene.get("type", "text")
    maxw = RW - 160
    dur = scene["dur"]
    if typ in ("hook", "text", "end"):
        weight = "b"
        size_max = 128 if typ == "hook" else 100
        f = fit_font(scene["text"], weight, size_max, 56, maxw, 7)
        lines = wrap_rich(scene["text"], f, maxw)
        lh = int(f.size * 1.2)
        total_h = lh * len(lines)
        y0 = (RH - total_h) // 2 - 80
        # word-by-word reveal over first 45% of scene (min 0.25s/line)
        words = [w for ln in lines for w in ln]
        reveal = min(dur * 0.45, 0.18 * len(words) + 0.2)
        shown = len(words) if st >= reveal else int(len(words) * st / max(reveal, 0.01)) + 1
        k = 0; y = y0
        for ln in lines:
            lw = line_width(ln, f); x = (RW - lw) / 2
            for w, col in ln:
                if k < shown:
                    wt = min(1.0, (st - (k / max(len(words), 1)) * reveal) / 0.15) if st < reveal else 1.0
                    a = ease(wt)
                    d.text((x, y + int((1 - a) * 24)), w, font=f, fill=blend(col, NAVY, a))
                x += f.getlength(w) + f.getlength(" ")
                k += 1
            y += lh
        if scene.get("sub"):
            a = ease((st - reveal) / 0.4)
            fs = F("r", 44)
            sl = wrap_rich(scene["sub"], fs, maxw, MUTED)
            draw_lines(d, sl, fs, 80, y + 50, 62, align="center", box_w=maxw, alpha=a)
        if typ == "end":
            a = ease((st - reveal) / 0.4)
            ftxt = "Save this for later"
            d.text(((RW - F("b", 44).getlength(ftxt)) / 2, RH - 420), ftxt, font=F("b", 44), fill=blend(MINT, NAVY, a))
    elif typ == "stat":
        fl = F("m", 60)
        top = scene.get("title", "")
        y = 600
        if top:
            y = draw_lines(d, wrap_rich(top, fl, maxw, MUTED), fl, 80, y, 82, align="center", box_w=maxw) + 40
        frac = ease(st / min(1.2, dur * 0.5))
        big = count_text(clean(scene["big"]), frac)
        fb = fit_font(scene["big"], "b", 230, 110, maxw, 1)
        col = {"mint": MINT, "red": RED, "amber": AMBER}.get(scene.get("color", "mint"), MINT)
        scale_y = y + int((1 - frac) * 30)
        d.text(((RW - fb.getlength(big)) / 2, scale_y), big, font=fb, fill=col)
        y += int(fb.size * 1.3)
        if scene.get("label"):
            a = ease((st - 0.6) / 0.4)
            fl2 = fit_font(scene["label"], "b", 64, 44, maxw, 3)
            draw_lines(d, wrap_rich(scene["label"], fl2, maxw), fl2, 80, y, int(fl2.size * 1.25), align="center", box_w=maxw, alpha=a)
    elif typ == "bars":
        f = fit_font(scene["title"], "b", 80, 56, maxw, 3)
        y = draw_lines(d, wrap_rich(scene["title"], f, maxw), f, 80, 560, int(f.size * 1.2)) + 80
        bars = scene["bars"]
        # four or more bars would run into the footer at full size, so tighten them
        bh, gap = (110, 70) if len(bars) <= 3 else (84, 34)
        vmax = max(abs(b["value"]) for b in bars) or 1
        for i, b in enumerate(bars):
            local = ease((st - 0.3 - i * 0.35) / 0.8)
            d.text((80, y), clean(b["label"]), font=F("m", 52), fill=blend(WHITE, NAVY, min(1, local * 2)))
            y += 76
            w = max(6, int((maxw - 300) * abs(b["value"]) / vmax * local))
            col = RED if b.get("alert") else (MINT if b.get("highlight") else (70, 110, 145))
            d.rounded_rectangle((80, y, 80 + w, y + bh), radius=16, fill=col)
            if local > 0.05:
                d.text((80 + w + 24, y + (bh - 72) // 2), count_text(clean(b.get("display", str(b["value"]))), local), font=F("b", 60), fill=WHITE)
            y += bh + gap
        if scene.get("note"):
            a = ease((st - 1.8) / 0.5)
            fn = F("r", 38)
            draw_lines(d, wrap_rich(scene["note"], fn, maxw, MUTED), fn, 80, y + 20, 54, alpha=a)
    elif typ == "list":
        f = fit_font(scene["title"], "b", 88, 60, maxw, 3)
        y = draw_lines(d, wrap_rich(scene["title"], f, maxw), f, 80, 560, int(f.size * 1.2)) + 70
        fi = F("m", 60)
        per = max(0.35, (dur * 0.7) / max(1, len(scene["items"])))
        for i, it in enumerate(scene["items"]):
            a = ease((st - 0.3 - i * per) / 0.3)
            if a <= 0:
                break
            mark = scene.get("marks", "num")
            if mark == "cross":
                d.text((80, y - 6 + int((1 - a) * 20)), "×", font=F("b", 60), fill=blend(RED, NAVY, a))
            else:
                d.text((80, y + int((1 - a) * 20)), str(i + 1), font=F("b", 54), fill=blend(MINT, NAVY, a))
            lines = wrap_rich(it, fi, maxw - 90)
            y = draw_lines(d, lines, fi, 180, y + int((1 - a) * 20), 84, alpha=a) + 50
    return img

def make_audio(path, seconds):
    sr = 44100
    n = int(sr * seconds)
    t = np.arange(n) / sr
    # slow chord pad (Am9 -> Fmaj7 -> C -> G) , 4s per chord
    chords = [[220.0, 261.63, 329.63, 392.0], [174.61, 220.0, 261.63, 329.63],
              [261.63, 329.63, 392.0, 493.88], [196.0, 246.94, 293.66, 392.0]]
    sig = np.zeros(n)
    seg = 4.0
    for ci in range(int(math.ceil(seconds / seg))):
        a, b = int(ci * seg * sr), min(n, int((ci + 1) * seg * sr + 0.5 * sr))
        tt = t[a:b] - ci * seg
        env = np.minimum(1, tt / 0.8) * np.minimum(1, np.maximum(0, (seg + 0.5 - tt) / 0.8))
        for fr in chords[ci % 4]:
            sig[a:b] += env * (np.sin(2 * np.pi * fr * tt) * 0.5 + 0.2 * np.sin(2 * np.pi * fr * 2.001 * tt))
    # soft pulse on each beat (90 bpm)
    beat = 60 / 90
    for k in range(int(seconds / beat)):
        s0 = int(k * beat * sr); s1 = min(n, s0 + int(0.12 * sr))
        tt = t[s0:s1] - k * beat
        sig[s0:s1] += 0.6 * np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 35)
    fade = np.minimum(1, np.minimum(t / 1.0, (seconds - t) / 1.5))
    sig = sig * fade
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * 0.35
    data = (sig * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(data.tobytes())

def render_reel(r, out):
    os.makedirs(out, exist_ok=True)
    scenes = [dict(s) for s in r["scenes"]]
    tmp_video = os.path.join(out, "_video.mp4")
    audio = os.path.join(out, "_audio.wav")
    # Narration: a scene's `vo` line is spoken by the AI voice and the scene stretches
    # to fit it, so the voice never runs past its own text. No `vo` lines = music only.
    import audio as A
    lines = []
    if r.get("narrate", True) and any(s.get("vo") for s in scenes):
        voice = r.get("voice", CFG.get("voice", A.DEFAULT_VOICE))
        for s in scenes:
            clip = None
            if s.get("vo"):
                try:
                    clip = A.speak(s["vo"], voice=voice, speed=r.get("voice_speed", CFG.get("voice_speed", A.DEFAULT_SPEED)),
                                   language=r.get("language", CFG.get("language", "hi-IN")))
                except Exception as exc:  # a voice outage must never cost us the post
                    print(f"narration failed, scene stays silent: {type(exc).__name__}: {exc}")
            if clip is not None:
                s["dur"] = round(max(s["dur"], len(clip) / A.SR + 0.55), 2)
            lines.append(clip)
    T = sum(s["dur"] for s in scenes)
    track = None
    if any(c is not None for c in lines):
        track = np.zeros(int(T * A.SR) + A.SR, dtype=np.float32)
        start = 0.0
        for s, clip in zip(scenes, lines):
            if clip is not None:
                a = int((start + 0.2) * A.SR)
                track[a:a + len(clip)] += clip[: len(track) - a]
            start += s["dur"]
    A.write_wav(audio, A.mix(T, track))
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{RW}x{RH}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "20", "-pix_fmt", "yuv420p", tmp_video], stdin=subprocess.PIPE)
    # mouth openness per frame, from the narration's loudness
    mouth_at = None
    if track is not None:
        hop = A.SR // FPS
        nfr = len(track) // hop
        env = np.sqrt(np.mean(track[: nfr * hop].reshape(nfr, hop) ** 2, axis=1))
        ref = np.percentile(env[env > 1e-4], 90) if np.any(env > 1e-4) else 1.0
        mouth_at = np.clip(env / (ref + 1e-9), 0, 1)
        mouth_at = np.convolve(mouth_at, [0.25, 0.5, 0.25], mode="same")
    use_mascot = r.get("mascot", True)

    def with_mascot(img, s, t):
        if not use_mascot:
            return img
        import character as C
        mood = s.get("mood") or ("concerned" if s.get("color") == "red" else
                                 "happy" if s.get("type") == "end" or s.get("color") == "mint" else "neutral")
        m = float(mouth_at[min(len(mouth_at) - 1, int(t * FPS))]) if mouth_at is not None else 0.0
        size = 300
        spr = C.sprite(size, mouth=m, t=t, mood=mood)
        if s.get("type") == "bars":  # bars run to the right edge, so the coin moves up top
            pos = (RW - 70 - size, 150 + C.bob(t))
        elif s.get("type") == "end":   # centred under the closing line, clear of the save prompt
            pos = ((RW - size) // 2, RH - 470 - size + C.bob(t))
        else:
            pos = (RW - 70 - size, RH - 200 - size + C.bob(t))
        img.paste(spr, pos, spr)
        return img

    frame = 0
    start = 0.0
    for s in scenes:
        nf = int(round(s["dur"] * FPS))
        for i in range(nf):
            st = i / FPS
            img = with_mascot(draw_reel_frame(s, st, start + st, T, len(scenes)), s, start + st)
            proc.stdin.write(img.tobytes())
            frame += 1
        start += s["dur"]
    proc.stdin.close(); proc.wait()
    final = os.path.join(out, "reel.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp_video, "-i", audio, "-c:v", "copy",
                    "-af", f"loudnorm=I={-14 if track is not None else -20}:TP=-1.5:LRA=11", "-ar", "44100",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", final], check=True)
    os.remove(tmp_video); os.remove(audio)
    # cover frame (end of first scene) for preview/check
    with_mascot(draw_reel_frame(scenes[0], scenes[0]["dur"] - 0.01, scenes[0]["dur"], T, len(scenes)), scenes[0], 0.0).save(os.path.join(out, "reel_cover.png"))
    with open(os.path.join(out, "reel_caption.txt"), "w") as fh:
        fh.write(r["caption"].strip() + "\n")
    return final

if __name__ == "__main__":
    post = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    only = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--only" else None
    if post.get("carousel") and only in (None, "carousel"):
        print("carousel:", render_carousel(post["carousel"], os.path.join(out, "carousel")))
    if post.get("reel") and only in (None, "reel"):
        print("reel:", render_reel(post["reel"], os.path.join(out, "reel")))
