#!/usr/bin/env python3
"""
Fix My Money — free photoreal presenter, v2 (2026-11-22).

From 4 photos of the same invented presenter (base = mouth closed, two open-mouth edits,
one blink edit) this builds a set of in-between mouth shapes and blink frames by optical-flow
morphing: each in-between is the source photo with its pixels *moved* part of the way toward
the target shape, so there is no see-through double-lip ghosting like a plain cross-fade.

Then it lip-syncs the set to any narration: per frame, the voice loudness picks one mouth
shape (hard cut, held at least 2 frames so it doesn't jitter), eyes blink every few seconds,
and the whole frame breathes with a slow push-in and a small sway.

    python3 presenter_morph.py <src_dir> <audio> <out.mp4>      (src_dir holds base/edit1..3.png)
    build_shapes(src_dir) -> dict of RGB uint8 frames, reused by the reel engine
"""
from __future__ import annotations

import math
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

FPS = 30
LEVELS = 6            # mouth shapes from closed (0) to most open (LEVELS-1)
AA_CAP = 0.55         # the "aa" edit is too wide (yawn); use only this fraction of the way to it


def _read(p: Path) -> np.ndarray:
    im = cv2.imread(str(p), cv2.IMREAD_COLOR)
    return cv2.cvtColor(im, cv2.COLOR_BGR2RGB)


def _diff_box(a, b, region, pad=40, thr=18):
    H, W = a.shape[:2]
    y0, y1, x0, x1 = region
    d = np.abs(a.astype(np.int16) - b.astype(np.int16)).mean(axis=2)
    m = np.zeros_like(d, dtype=np.uint8)
    m[y0:y1, x0:x1] = (d[y0:y1, x0:x1] > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    ys, xs = np.nonzero(m)
    if len(ys) == 0:
        return None
    return (max(0, ys.min() - pad), min(H, ys.max() + pad), max(0, xs.min() - pad), min(W, xs.max() + pad)), \
        float(ys.mean()), float(m.sum())


def _flow(a, b):
    ga, gb = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY), cv2.cvtColor(b, cv2.COLOR_RGB2GRAY)
    return cv2.calcOpticalFlowFarneback(ga, gb, None, 0.5, 4, 25, 5, 7, 1.5, 0)


def _warp(img, flow, s):
    h, w = flow.shape[:2]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(img, gx - s * flow[..., 0], gy - s * flow[..., 1], cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REFLECT)


def _morph(a, b, t):
    """Frame a fraction t of the way from a to b (both crops of the same box)."""
    if t <= 0:
        return a.copy()
    if t >= 1:
        return b.copy()
    f_ab, f_ba = _flow(a, b), _flow(b, a)
    wa = _warp(a, f_ba, t)        # a's pixels pulled t of the way toward b
    wb = _warp(b, f_ab, 1 - t)    # b's pixels pulled (1-t) of the way back toward a
    return (wa.astype(np.float32) * (1 - t) + wb.astype(np.float32) * t).astype(np.uint8)


def _feather(h, w, edge=0.22):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ry, rx = (yy - h / 2) / (h / 2), (xx - w / 2) / (w / 2)
    r = np.sqrt(rx ** 2 + ry ** 2)
    return np.clip((1 - r) / edge, 0, 1)[..., None]


def _paste(base, crop, box):
    y0, y1, x0, x1 = box
    out = base.copy()
    m = _feather(y1 - y0, x1 - x0)
    out[y0:y1, x0:x1] = (crop * m + base[y0:y1, x0:x1] * (1 - m)).astype(np.uint8)
    return out


def _align(base, img, face, exclude):
    """Affine-align `img` to `base` using the face minus the mouth (ECC). Returns aligned img."""
    y0, y1, x0, x1 = face
    gb = cv2.cvtColor(base, cv2.COLOR_RGB2GRAY).astype(np.float32)
    gi = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
    mask = np.zeros_like(gb, dtype=np.uint8)
    mask[y0:y1, x0:x1] = 255
    ey0, ey1, ex0, ex1 = exclude
    mask[ey0:ey1, ex0:ex1] = 0
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        # coarse-to-fine: first at quarter size, then full size
        sc = 0.25
        small = [cv2.resize(g, None, fx=sc, fy=sc) for g in (gb, gi)]
        msmall = cv2.resize(mask, None, fx=sc, fy=sc, interpolation=cv2.INTER_NEAREST)
        _, w0 = cv2.findTransformECC(small[0], small[1], warp.copy(), cv2.MOTION_AFFINE,
                                     (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5), msmall, 5)
        w0[:, 2] /= sc
        _, warp = cv2.findTransformECC(gb, gi, w0, cv2.MOTION_AFFINE,
                                       (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1e-6), mask, 5)
    except cv2.error as exc:
        print(f"align: ECC failed ({exc}); using unaligned")
    H, W = base.shape[:2]
    return cv2.warpAffine(img, warp, (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                          borderMode=cv2.BORDER_REFLECT)


def build_shapes(src: Path) -> dict:
    base = _read(src / "base.png")
    H, W = base.shape[:2]
    edits = [_read(p) for p in sorted(src.glob("edit*.png"))]
    face = (int(H * 0.08), int(H * 0.50), int(W * 0.22), int(W * 0.78))
    # rough mouth area (lower-middle of the face) is excluded from alignment
    rough_mouth = (int(H * 0.35), int(H * 0.50), int(W * 0.38), int(W * 0.70))
    aligned = [_align(base, e, face, rough_mouth) for e in edits]
    info = []
    for e in aligned:
        r = _diff_box(base, e, face, pad=30, thr=30)
        if r:
            info.append((e, *r))
    blink = min(info, key=lambda x: x[2])          # change sits highest = eyes
    mouths = sorted([x for x in info if x is not blink], key=lambda x: x[3])
    eh, aa = mouths[0], mouths[-1]
    # mouth box: where the two mouth edits differ from base inside the rough mouth area
    ry0, ry1, rx0, rx1 = rough_mouth
    d = np.maximum(np.abs(eh[0].astype(np.int16) - base).mean(axis=2), np.abs(aa[0].astype(np.int16) - base).mean(axis=2))
    sub = cv2.GaussianBlur(d[ry0:ry1, rx0:rx1].astype(np.float32), (21, 21), 0)
    ys, xs = np.nonzero(sub > 0.35 * sub.max())
    pad = 45
    mb = (ry0 + max(0, ys.min() - pad), min(H, ry0 + ys.max() + pad), rx0 + max(0, xs.min() - pad), min(W, rx0 + xs.max() + pad))
    y0, y1, x0, x1 = mb
    c0, ce, ca = base[y0:y1, x0:x1], eh[0][y0:y1, x0:x1], aa[0][y0:y1, x0:x1]
    ctop = _morph(ce, ca, AA_CAP)
    mouth = []
    for k in range(LEVELS):
        o = k / (LEVELS - 1)
        crop = _morph(c0, ce, o / 0.5) if o <= 0.5 else _morph(ce, ctop, (o - 0.5) / 0.5)
        mouth.append(crop)
    # blink: eye band only
    ey = blink[2]
    bb = (int(max(0, ey - H * 0.045)), int(ey + H * 0.04), int(W * 0.30), int(W * 0.72))
    b0, b1 = base[bb[0]:bb[1], bb[2]:bb[3]], blink[0][bb[0]:bb[1], bb[2]:bb[3]]
    eyes = [None, _morph(b0, b1, 0.5), b1]
    return dict(base=base, mouth_box=mb, mouth=mouth, eye_box=bb, eyes=eyes)


def frame(shapes, level: int, eye: int, t: float, T: float) -> np.ndarray:
    img = _paste(shapes["base"], shapes["mouth"][level], shapes["mouth_box"])
    if eye:
        img = _paste(img, shapes["eyes"][eye], shapes["eye_box"])
    H, W = img.shape[:2]
    z = 1.0 + 0.035 * (t / max(T, 1)) + 0.004 * math.sin(t * 1.1)
    ang = 0.6 * math.sin(t * 0.55) + 0.25 * math.sin(t * 1.7)          # degrees of gentle sway
    M = cv2.getRotationMatrix2D((W / 2, H * 0.30), ang, z)
    M[0, 2] += 5 * math.sin(t * 0.4)
    M[1, 2] += 4 * math.sin(t * 0.9)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def loudness(audio: Path):
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "a.f32"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(audio), "-ac", "1", "-ar", "48000",
                        "-f", "f32le", str(raw)], check=True)
        x = np.fromfile(raw, dtype=np.float32)
    hop = 48000 // FPS
    n = len(x) // hop
    env = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1))
    ref = np.percentile(env[env > 1e-4], 90) if np.any(env > 1e-4) else 1.0
    return np.clip(env / (ref + 1e-9), 0, 1), len(x) / 48000


def mouth_track(env: np.ndarray) -> list[int]:
    lv = np.round(np.convolve(env, [0.25, 0.5, 0.25], mode="same") ** 0.8 * (LEVELS - 1)).astype(int)
    out, cur, held = [], 0, 99
    for v in lv:
        if v != cur and held >= 2:      # hold each shape >= 2 frames: no jitter
            cur, held = int(v), 0
        out.append(cur)
        held += 1
    return out


def render(src: Path, audio: Path, out: Path) -> Path:
    shapes = build_shapes(src)
    env, T = loudness(audio)
    track = mouth_track(env)
    H, W = shapes["base"].shape[:2]
    n = int(T * FPS) + 1
    with tempfile.TemporaryDirectory() as td:
        vid = Path(td) / "v.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                              "-crf", "20", "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
        for f in range(n):
            t = f / FPS
            ph = (t + 1.1) % 3.7
            eye = 2 if ph < 0.13 else 0  # clean shut frame (the half-blink morph ghosts)
            p.stdin.write(frame(shapes, track[min(f, len(track) - 1)], eye, t, T).tobytes())
        p.stdin.close(); p.wait()
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vid), "-i", str(audio), "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    return out


if __name__ == "__main__":
    print(render(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])))
