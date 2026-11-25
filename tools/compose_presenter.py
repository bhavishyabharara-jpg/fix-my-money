#!/usr/bin/env python3
"""
Fix My Money — put the realistic AI presenter into a rendered reel. 2026-11-25.

    compose_presenter.py <base.mp4> <presenter.mp4> <presenter.json> <out.mp4> <cover.png>

base.mp4        the reel without the coin (engine/render.py writes it when presenter_mode is "human")
presenter.mp4   the InfiniteTalk clip, lip-synced to the reel's own narration (same timeline)
presenter.json  where the presenter sits on every frame (x, y, size of the coin's square slot)

The presenter is shown as a rounded 3:4 "facecam" card in the coin's place (bottom of the card on
the bottom of the coin's slot), with a thin white edge, a soft shadow and a small "AI" tag, because
every AI presenter is disclosed. Audio is the base reel's (voice + music, loudness-normalised).
"""
from __future__ import annotations

import json
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pathlib import Path

FONT = str(Path(__file__).resolve().parent.parent / "engine" / "fonts" / "Poppins-Bold.ttf")
RATIO = 4 / 3          # card height / width
RADIUS = 0.11          # corner radius as a share of the width
FACE_TOP = 0.03        # the presenter clip is a head-and-shoulders portrait: keep a little headroom


def frames(path: str, w: int, h: int, fps: int, vf: str = ""):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps}{',' + vf if vf else ''}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield Image.frombuffer("RGB", (w, h), buf, "raw", "RGB", 0, 1)
    p.wait()


def probe(path: str) -> tuple[int, int]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split(",")[:2]
    return int(w), int(h)


def card_assets(w: int):
    """Mask, shadow and AI tag for a card of width w (cached per size)."""
    h = int(w * RATIO)
    r = int(w * RADIUS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    pad = 18
    shadow = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((pad, pad + 6, pad + w, pad + h + 6), r, fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    edge = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle((0, 0, w - 1, h - 1), r, outline=(255, 255, 255, 235), width=max(3, w // 100))
    fs = max(18, w // 13)
    font = ImageFont.truetype(FONT, fs)
    tw = int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength("AI", font=font))
    tag = Image.new("RGBA", (tw + fs, int(fs * 1.5)), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    td.rounded_rectangle((0, 0, tag.width - 1, tag.height - 1), tag.height // 2, fill=(15, 23, 42, 200))
    td.text((fs // 2, int(fs * 0.12)), "AI", font=font, fill=(255, 255, 255, 255))
    return h, mask, shadow, pad, edge, tag


def main(base: str, pres: str, meta_path: str, out: str, cover: str) -> None:
    meta = json.loads(Path(meta_path).read_text())
    fps, W, H = meta["fps"], meta["w"], meta["h"]
    place = meta["placements"]
    pw, ph = probe(pres)
    # head-and-shoulders crop of the presenter clip at 3:4
    cw = pw - pw % 2
    chh = min(ph, int(cw * RATIO)); chh -= chh % 2   # even sizes: yuv420 crops round odd ones
    cy = int(ph * FACE_TOP)
    pres_vf = f"crop={cw}:{chh}:0:{cy}"
    cache = {}
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(fps), "-i", "-", "-i", base, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                            "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest",
                            "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    pframes = frames(pres, cw, chh, fps, pres_vf)
    last = None
    for i, frame in enumerate(frames(base, W, H, fps)):
        try:
            last = next(pframes)
        except StopIteration:
            pass  # presenter a frame short: hold his last frame
        x, y, size = place[min(i, len(place) - 1)]
        if last is not None:
            if size not in cache:
                cache[size] = card_assets(size)
            h, mask, shadow, pad, edge, tag = cache[size]
            top = y + size - h          # card's bottom sits on the coin slot's bottom
            if top < 90:                # near the header (bars scene): hang the card down from the slot instead
                top = y
            frame = frame.convert("RGBA")
            frame.alpha_composite(shadow, (max(0, x - pad), max(0, top - pad)))
            face = last.resize((size, h), Image.LANCZOS)
            frame.paste(face, (x, top), mask)
            frame.alpha_composite(edge, (x, top))
            frame.alpha_composite(tag, (x + size - tag.width - size // 22, top + size // 22))
            frame = frame.convert("RGB")
        if i == meta.get("cover_frame", 0):
            frame.save(cover)
        enc.stdin.write(frame.tobytes())
    enc.stdin.close()
    enc.wait()
    if enc.returncode:
        raise SystemExit("compose: encode failed")
    print(f"composed {out}")


if __name__ == "__main__":
    main(*sys.argv[1:6])
