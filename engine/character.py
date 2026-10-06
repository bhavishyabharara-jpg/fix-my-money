"""
"Sikka" — the Fix My Money presenter.

A friendly gold coin with round glasses who talks through every reel. Drawn in code, so it
is ours outright and renders identically every time. The mouth follows the narration's
loudness frame by frame, the eyes blink every few seconds, and it bobs gently.

    sprite(mouth=0..1, t=seconds, mood="neutral"|"happy"|"concerned") -> RGBA image
"""
from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

GOLD = (246, 190, 72)
GOLD_DARK = (212, 148, 40)
GOLD_LIGHT = (255, 221, 134)
RIM = (176, 116, 26)
INK = (28, 33, 48)
WHITE = (255, 255, 255)
CHEEK = (255, 128, 128)
MOUTH = (110, 34, 40)
TONGUE = (236, 104, 104)
FRAME = (34, 44, 66)

S = 2  # supersample factor for clean edges


def _blink(t: float) -> float:
    """0 = eyes open, 1 = shut. A quick blink every ~3.4 s, offset so the first lands late."""
    phase = (t + 1.3) % 3.4
    if phase < 0.14:
        return math.sin(phase / 0.14 * math.pi)
    return 0.0


@lru_cache(maxsize=4)
def _body(size: int) -> Image.Image:
    W = size * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = int(W * 0.06)
    # soft drop shadow
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((pad + W * 0.03, pad + W * 0.05, W - pad + W * 0.03, W - pad + W * 0.05), fill=(0, 0, 0, 90))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(W * 0.03)))
    # coin: rim, face, inner ring, highlight
    d.ellipse((pad, pad, W - pad, W - pad), fill=RIM)
    r2 = pad + int(W * 0.035)
    d.ellipse((r2, r2, W - r2, W - r2), fill=GOLD)
    r3 = pad + int(W * 0.075)
    d.ellipse((r3, r3, W - r3, W - r3), outline=GOLD_DARK, width=max(2, int(W * 0.012)))
    d.arc((r3 + W * 0.04, r3 + W * 0.04, W - r3 - W * 0.04, W - r3 - W * 0.04), 200, 290,
          fill=GOLD_LIGHT, width=max(3, int(W * 0.03)))
    # rupee mark, embossed on the forehead
    cx = W / 2
    y0 = W * 0.19
    w = W * 0.10
    lw = max(3, int(W * 0.018))
    col = GOLD_DARK
    d.line((cx - w, y0, cx + w, y0), fill=col, width=lw)
    d.line((cx - w, y0 + W * 0.035, cx + w, y0 + W * 0.035), fill=col, width=lw)
    d.arc((cx - w * 1.4, y0 - W * 0.002, cx + w * 0.6, y0 + W * 0.075), 270, 90, fill=col, width=lw)
    d.line((cx - w * 0.4, y0 + W * 0.075, cx + w * 0.5, y0 + W * 0.15), fill=col, width=lw)
    return img


def sprite(size: int = 260, mouth: float = 0.0, t: float = 0.0, mood: str = "neutral") -> Image.Image:
    W = size * S
    img = _body(size).copy()
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, W / 2

    # cheeks
    for sx in (-1, 1):
        x = cx + sx * W * 0.25
        d.ellipse((x - W * 0.06, cy + W * 0.07, x + W * 0.06, cy + W * 0.12), fill=CHEEK + (120,))

    # eyes behind round glasses
    blink = _blink(t)
    look = math.sin(t * 0.7) * W * 0.008
    for sx in (-1, 1):
        ex, ey = cx + sx * W * 0.14, cy - W * 0.02
        er = W * 0.075
        lid = er * (1 - 0.92 * blink)
        d.ellipse((ex - er, ey - lid, ex + er, ey + lid), fill=WHITE)
        if blink < 0.6:
            pr = W * 0.035
            d.ellipse((ex - pr + look, ey - pr, ex + pr + look, ey + pr), fill=INK)
            d.ellipse((ex - pr * 0.3 + look, ey - pr * 0.7, ex + pr * 0.25 + look, ey - pr * 0.15), fill=WHITE)
        gr = W * 0.105
        d.ellipse((ex - gr, ey - gr, ex + gr, ey + gr), outline=FRAME, width=max(3, int(W * 0.016)))
    d.line((cx - W * 0.035, cy - W * 0.03, cx + W * 0.035, cy - W * 0.03), fill=FRAME, width=max(3, int(W * 0.014)))

    # eyebrows carry the mood
    lift = {"happy": -0.012, "concerned": 0.0, "neutral": -0.004}.get(mood, 0)
    for sx in (-1, 1):
        bx = cx + sx * W * 0.14
        by = cy - W * 0.155 + lift * W
        tilt = (W * 0.02 * sx) if mood == "concerned" else 0
        d.line((bx - W * 0.06, by - tilt, bx + W * 0.06, by + tilt), fill=INK, width=max(4, int(W * 0.02)))

    # mouth: a smile line when quiet, an open mouth while speaking
    my = cy + W * 0.17
    mw = W * 0.12
    m = max(0.0, min(1.0, mouth))
    if m < 0.08:
        lw = max(4, int(W * 0.018))
        if mood == "concerned":   # a small frown
            d.arc((cx - mw * 0.8, my - W * 0.01, cx + mw * 0.8, my + W * 0.06), 205, 335, fill=MOUTH, width=lw)
        else:
            d.arc((cx - mw, my - W * 0.06, cx + mw, my + W * 0.04), 15, 165, fill=MOUTH, width=lw)
    else:
        h = W * (0.025 + 0.085 * m)
        ww = mw * (0.85 + 0.15 * (1 - m))
        d.rounded_rectangle((cx - ww, my - h * 0.5, cx + ww, my + h * 0.5), radius=int(h * 0.5), fill=MOUTH)
        if h > W * 0.05:
            d.ellipse((cx - ww * 0.55, my, cx + ww * 0.55, my + h * 0.5), fill=TONGUE)

    out = img.resize((size, size), Image.LANCZOS)
    return out


def bob(t: float, amp: float = 6.0) -> int:
    return int(round(math.sin(t * 2 * math.pi / 2.6) * amp))
