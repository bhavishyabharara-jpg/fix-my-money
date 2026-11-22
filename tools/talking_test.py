#!/usr/bin/env python3
"""
Fix My Money — FREE realistic-presenter test (2026-11-22).

Same idea as the Sikka coin: the mouth follows the narration's loudness. Instead of a drawn
mouth, we blend between a few AI-edited photos of the same invented presenter (mouth closed,
"eh", "aa", eyes shut). Only the changed region of each edit (found by diffing it against the
base photo, inside the face area) is blended onto the base, so the background never flickers.

Input: previews/talking_test.json  {"base": url, "edits": [url, ...], "audio": "voice/samples/amit.mp3"}
Output: previews/out/talking_test.mp4 (never published)
"""
from __future__ import annotations

import io
import json
import math
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30


def load(url: str) -> np.ndarray:
    with urllib.request.urlopen(url, timeout=120) as r:
        im = Image.open(io.BytesIO(r.read())).convert("RGB").resize((W, H), Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def region_mask(base: np.ndarray, edit: np.ndarray) -> tuple[np.ndarray, float, float]:
    d = np.abs(edit - base).mean(axis=2)
    face = np.zeros_like(d)
    face[int(H * 0.08):int(H * 0.50), int(W * 0.22):int(W * 0.78)] = 1  # head sits in the upper third
    d = d * face
    m = (d > 18).astype(np.float32)
    mi = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(14))
    mask = np.asarray(mi).astype(np.float32) / 255.0
    ys, xs = np.nonzero(m)
    cy = float(ys.mean()) if len(ys) else 0.0
    return mask[..., None], cy, float(m.sum())


def audio_env(path: Path, n_frames_hint: int | None = None):
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "a.f32"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", "48000",
                        "-f", "f32le", str(raw)], check=True)
        x = np.fromfile(raw, dtype=np.float32)
    hop = 48000 // FPS
    n = len(x) // hop
    env = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1))
    ref = np.percentile(env[env > 1e-4], 90) if np.any(env > 1e-4) else 1.0
    m = np.clip(env / (ref + 1e-9), 0, 1)
    return np.convolve(m, [0.2, 0.3, 0.3, 0.2], mode="same"), len(x) / 48000


def main() -> int:
    cfg_path = ROOT / "previews" / "talking_test.json"
    dst = ROOT / "previews" / "out" / "talking_test.mp4"
    if not cfg_path.exists() or dst.exists():
        return 0
    cfg = json.loads(cfg_path.read_text())
    base = load(cfg["base"])
    edits = []
    for u in cfg["edits"]:
        e = load(u)
        mask, cy, area = region_mask(base, e)
        edits.append(dict(img=e, mask=mask, cy=cy, area=area))
        print(f"edit {u[-24:]}: changed area {area:.0f}px, centre y {cy:.0f}")
    # the edit whose change sits highest is the blink; of the rest, the bigger change is "aa"
    blink = min(edits, key=lambda e: e["cy"])
    mouths = sorted([e for e in edits if e is not blink], key=lambda e: e["area"])
    eh, aa = (mouths + mouths)[:2] if len(mouths) == 1 else (mouths[0], mouths[-1])

    def comp(target, mask, w):
        return lambda img: img * (1 - mask * w) + target * (mask * w)

    mouth, dur = audio_env(ROOT / cfg["audio"])
    nf = int(dur * FPS) + 1
    with tempfile.TemporaryDirectory() as td:
        vid = Path(td) / "v.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "20",
                              "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
        for f in range(nf):
            t = f / FPS
            m = float(mouth[min(f, len(mouth) - 1)])
            img = base.copy()
            # mouth: 0 -> base, 0.5 -> eh, 1 -> aa (linear blend between neighbours)
            if m <= 0.5:
                img = comp(eh["img"], eh["mask"], m / 0.5)(img)
            else:
                img = comp(eh["img"], eh["mask"], 1.0)(img)
                img = comp(aa["img"], aa["mask"], (m - 0.5) / 0.5)(img)
            ph = (t + 1.1) % 3.6  # blink every ~3.6 s, ~130 ms
            if ph < 0.13:
                img = comp(blink["img"], blink["mask"], math.sin(ph / 0.13 * math.pi))(img)
            # gentle life: slow push-in plus a tiny sway
            z = 1.0 + 0.03 * (t / max(dur, 1)) + 0.004 * math.sin(t * 1.3)
            pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
            cw, ch = int(W / z), int(H / z)
            ox = (W - cw) // 2 + int(4 * math.sin(t * 0.7))
            oy = (H - ch) // 3
            pil = pil.crop((ox, oy, ox + cw, oy + ch)).resize((W, H), Image.BICUBIC)
            p.stdin.write(pil.tobytes())
        p.stdin.close(); p.wait()
        dst.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vid), "-i", str(ROOT / cfg["audio"]),
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
                        str(dst)], check=True)
    print(f"talking_test: ok -> {dst.relative_to(ROOT)} ({dur:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
