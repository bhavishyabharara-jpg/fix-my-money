#!/usr/bin/env python3
"""
Fix My Money — realistic AI presenter via fal.ai (added 2026-11-22).

Turns one portrait image + the reel's narration audio into a lip-synced talking-head
video, using an audio-driven avatar model on fal.ai. The engine composites that video
into the reel. Called from tools/build.py inside GitHub Actions, where FAL_KEY lives
as a repo secret. With no FAL_KEY, or on any failure, it returns None and the reel falls
back to the "Sikka" coin presenter, so publishing never depends on fal.

Config (engine/config.json):
  "presenter_model": "fal-ai/kling-video/ai-avatar/v2/standard"   (≈ $0.056 per second)
  "presenter_image": "https://.../presenter.png"                   (public URL)

Disclosure rule (PLAYBOOK, owner reset 22 Nov, rule 8): every reel with this presenter is
labelled as AI on Instagram and says "Presenter and voice are AI-generated." in the caption.
"""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.request
from pathlib import Path

QUEUE = "https://queue.fal.run"
DEFAULT_MODEL = "fal-ai/kling-video/ai-avatar/v2/standard"


def _req(method: str, url: str, body: dict | None = None, timeout: int = 120) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Key {os.environ['FAL_KEY']}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _data_uri(path: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def talking_head(audio: Path, out: Path, image_url: str, model: str = DEFAULT_MODEL,
                 prompt: str = "a friendly Indian finance explainer talking to camera, natural head movement",
                 max_wait_s: int = 1500) -> Path | None:
    """Render a talking-head mp4 for `audio` into `out`. Returns out, or None on failure."""
    if not os.environ.get("FAL_KEY"):
        print("presenter: FAL_KEY not set; using the coin presenter")
        return None
    try:
        mime = "audio/mpeg" if audio.suffix == ".mp3" else "audio/wav"
        sub = _req("POST", f"{QUEUE}/{model}",
                   {"image_url": image_url, "audio_url": _data_uri(audio, mime), "prompt": prompt})
        status_url, result_url = sub["status_url"], sub["response_url"]
        t0 = time.time()
        while time.time() - t0 < max_wait_s:
            st = _req("GET", status_url)
            if st.get("status") == "COMPLETED":
                break
            time.sleep(10)
        else:
            print("presenter: timed out")
            return None
        res = _req("GET", result_url)
        video_url = (res.get("video") or {}).get("url")
        if not video_url:
            print(f"presenter: no video in result: {str(res)[:200]}")
            return None
        out.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(video_url, out)
        print(f"presenter: ok ({model}, {time.time() - t0:.0f}s)")
        return out
    except Exception as exc:  # never block publishing
        print(f"presenter: FAILED {type(exc).__name__}: {str(exc)[:200]}")
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("usage: presenter.py <audio.mp3> <out.mp4> <image_url> [model]")
        raise SystemExit(2)
    r = talking_head(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], *(sys.argv[4:5]))
    raise SystemExit(0 if r else 1)
