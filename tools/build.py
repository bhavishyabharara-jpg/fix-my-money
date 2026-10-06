#!/usr/bin/env python3
"""
Fix My Money — render narrated reels inside GitHub Actions.

Why here: the Sarvam voice key lives only in this repo's Actions secrets, so the voice
(and the presenter's lip-sync, which follows the voice) can only be made here.

1. Voice samples. If voice/request.json lists speakers that have no sample yet, write
   voice/samples/<speaker>.mp3 for each, reading the request's line. Used once, to pick
   the channel's voice.

2. Reels from specs. A queue job may carry "spec": "specs/<file>.json" (a post.json the
   daily run wrote, with Hinglish `vo` lines per scene). If the job's media file doesn't
   exist yet, render it here with the engine, so narration, music and the presenter are
   mixed in one pass. The job's media/cover paths say where the output goes.

A failure here never blocks publishing: a job whose render fails keeps its old media if it
has any, and is retried on the next run.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))


def voice_samples() -> int:
    req_path = ROOT / "voice" / "request.json"
    if not req_path.exists():
        return 0
    req = json.loads(req_path.read_text())
    out_dir = ROOT / "voice" / "samples"
    out_dir.mkdir(parents=True, exist_ok=True)
    import audio as A
    made = 0
    for spk in req.get("speakers", []):
        dst = out_dir / f"{spk}.mp3"
        if dst.exists():
            continue
        try:
            pcm = A.speak(req["text"], voice=f"sarvam:{spk}", speed=float(req.get("pace", 1.0)),
                          language=req.get("language", "hi-IN"))
        except Exception as exc:
            print(f"sample {spk}: FAILED {type(exc).__name__}: {str(exc)[:200]}")
            continue
        with tempfile.TemporaryDirectory() as td:
            wav = os.path.join(td, "v.wav")
            peak = max(1e-6, float(abs(pcm).max()))
            A.write_wav(wav, pcm / peak * 0.9)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "128k", str(dst)], check=True)
        made += 1
        print(f"sample {spk}: ok ({len(pcm) / A.SR:.1f}s)")
    return made


def render_specs() -> int:
    made = 0
    for job_path in sorted((ROOT / "queue").glob("*.json")):
        job = json.loads(job_path.read_text())
        spec = job.get("spec")
        if not spec or job.get("slot") != "reel":
            continue
        target = ROOT / job["media"][0]
        if target.exists() and not job.get("rebuild"):
            continue
        spec_path = ROOT / spec
        if not spec_path.exists():
            print(f"{job_path.name}: spec {spec} missing")
            continue
        with tempfile.TemporaryDirectory() as td:
            res = subprocess.run([sys.executable, str(ROOT / "engine" / "render.py"), str(spec_path), td, "--only", "reel"],
                                 capture_output=True, text=True)
            print(res.stdout[-2000:], res.stderr[-2000:])
            out = Path(td) / "reel" / "reel.mp4"
            if res.returncode != 0 or not out.exists():
                print(f"{job_path.name}: render FAILED")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(out, target)
            if job.get("cover"):
                shutil.copy(Path(td) / "reel" / "reel_cover.png", ROOT / job["cover"])
        if job.pop("rebuild", None):
            job_path.write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n")
        made += 1
        print(f"{job_path.name}: rendered -> {job['media'][0]}")
    return made


def previews() -> int:
    """Render specs in previews/*.json to previews/out/<name>.mp4. Never published."""
    made = 0
    for spec in sorted((ROOT / "previews").glob("*.json")):
        dst = ROOT / "previews" / "out" / f"{spec.stem}.mp4"
        if dst.exists():
            continue
        with tempfile.TemporaryDirectory() as td:
            res = subprocess.run([sys.executable, str(ROOT / "engine" / "render.py"), str(spec), td, "--only", "reel"],
                                 capture_output=True, text=True)
            print(res.stdout[-1500:], res.stderr[-1500:])
            out = Path(td) / "reel" / "reel.mp4"
            if out.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(out, dst)
                made += 1
                print(f"preview {spec.stem}: ok")
    return made


def main() -> int:
    if not os.environ.get("SARVAM_API_KEY", "").strip():
        print("build: SARVAM_API_KEY not set; skipping voice work")
        return 0
    n = voice_samples() + previews() + render_specs()
    print(f"build: {n} file(s) made")
    return 0


if __name__ == "__main__":
    sys.exit(main())
