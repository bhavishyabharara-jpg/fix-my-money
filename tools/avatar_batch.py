#!/usr/bin/env python3
"""
Fix My Money — add the realistic AI presenter to queued reels, in batches. 2026-11-25.

Runs in .github/workflows/avatar.yml (hourly). tools/build.py leaves, for every reel it renders
while engine/config.json has presenter_mode "human":
    avatar/work/<job>/base.mp4        the reel without the coin
    avatar/work/<job>/voice.wav       the narration alone, on the reel's timeline
    avatar/work/<job>/presenter.json  where the presenter sits on every frame
    avatar/requests/<job>.json        {"backend": "presenter", "job": "queue/<job>.json", "status": "pending"}
and the normal coin reel as the job's media, so the post goes out as before if anything here fails.

This script picks pending requests, renders all of them in ONE Modal call (the ~7 min model download
is paid once per batch, not per reel), composites the presenter into each reel, switches the caption's
AI disclosure to cover the presenter, and marks the request done.

When it acts: a reel due within 36 hours, or 3+ waiting (so reels are batched without ever being
late). At most 4 per run. A request that fails twice is given up and the coin reel stays.
Cost guard: Modal's own $0 spend limit / $29 usage cap stop jobs before any card charge; a refused
job simply leaves the coin reels in place.
"""
from __future__ import annotations

import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQ = ROOT / "avatar" / "requests"
WORK = ROOT / "avatar" / "work"
CFG = json.loads((ROOT / "engine" / "config.json").read_text())
DISCLOSE_OLD = "Voiceover is AI-generated."
DISCLOSE_NEW = "Presenter and voiceover are AI-generated."
MAX_BATCH, MIN_BATCH, SOON_H = 4, 3, 36


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")


def disclose(caption: str) -> str:
    if DISCLOSE_NEW in caption:
        return caption
    if DISCLOSE_OLD in caption:
        return caption.replace(DISCLOSE_OLD, DISCLOSE_NEW)
    lines = caption.rstrip().split("\n")
    # before the keyword/hashtag tail if there is one
    cut = next((i for i in range(len(lines) - 1, -1, -1) if lines[i].startswith("[") or lines[i].startswith("#")), None)
    while cut is not None and cut > 0 and (lines[cut - 1].startswith("[") or lines[cut - 1].startswith("#")):
        cut -= 1
    if cut is None:
        return caption.rstrip() + "\n" + DISCLOSE_NEW
    return "\n".join(lines[:cut] + [DISCLOSE_NEW, ""] + lines[cut:])


def main() -> int:
    published = set(json.loads((ROOT / "published.json").read_text()).get("published", {}))
    soon = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=SOON_H)).strftime("%Y-%m-%dT%H:%M")
    pending = []
    for rp in sorted(REQ.glob("*.json")):
        req = json.loads(rp.read_text())
        if req.get("backend") != "presenter" or req.get("status", "pending") != "pending":
            continue
        jp = ROOT / req["job"]
        job = json.loads(jp.read_text()) if jp.exists() else None
        due = (job or {}).get("publish_at", "")
        if job is None or jp.stem in published or (due and due[:16] <= now_utc()):
            req["status"] = "expired"          # already out (with the coin) or gone: nothing to do
            rp.write_text(json.dumps(req, indent=2) + "\n")
            print(f"{rp.stem}: expired")
            continue
        w = WORK / jp.stem
        if not all((w / f).exists() for f in ("base.mp4", "voice.wav", "presenter.json")):
            print(f"{rp.stem}: work files missing, skipped")
            continue
        pending.append((due or "9999", rp, req, jp, job, w))
    pending.sort(key=lambda x: x[0])
    if not pending:
        print("presenter: nothing waiting")
        return 0
    if not any(d[:16] <= soon for d, *_ in pending) and len(pending) < MIN_BATCH:
        print(f"presenter: {len(pending)} waiting, none due within {SOON_H} h; batching later")
        return 0
    batch = pending[:MAX_BATCH]
    image = ROOT / CFG.get("presenter_image_local", "previews/out/presenter_src/closeup.png")
    manifest = [{"image": str(image), "audio": str(w / "voice.wav"), "out": str(w / "presenter.mp4")}
                for _, _, _, _, _, w in batch]
    for _, _, _, _, _, w in batch:
        (w / "presenter.mp4").unlink(missing_ok=True)
    mpath = WORK / "_manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2))
    print(f"presenter: rendering {len(batch)} on Modal: {[rp.stem for _, rp, *_ in batch]}", flush=True)
    log = WORK / "_last_batch.log"
    with open(log, "w") as fh:
        rc = subprocess.run(["modal", "run", "tools/avatar_infinitetalk.py", "--manifest", str(mpath)],
                            cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT, timeout=95 * 60).returncode
    print(log.read_text()[-3000:])
    mpath.unlink(missing_ok=True)
    done = 0
    for _, rp, req, jp, job, w in batch:
        clip = w / "presenter.mp4"
        ok = False
        if clip.exists():
            target = ROOT / job["media"][0]
            cover = ROOT / job["cover"] if job.get("cover") else w / "cover.png"
            tmp = w / "composed.mp4"
            res = subprocess.run([sys.executable, str(ROOT / "tools" / "compose_presenter.py"), str(w / "base.mp4"),
                                  str(clip), str(w / "presenter.json"), str(tmp), str(cover)],
                                 capture_output=True, text=True)
            print(res.stdout[-500:], res.stderr[-500:])
            if res.returncode == 0 and tmp.exists() and tmp.stat().st_size > 100_000:
                shutil.copy(tmp, target)
                tmp.unlink()
                job["caption"] = disclose(job["caption"])
                job["presenter"] = "human"
                jp.write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n")
                ok = True
        if ok:
            req["status"] = "done"
            req["done_at"] = now_utc()
            done += 1
        else:
            req["attempts"] = req.get("attempts", 0) + 1
            if req["attempts"] >= 2:
                req["status"] = "failed"   # give up: the coin reel goes out
        rp.write_text(json.dumps(req, indent=2) + "\n")
        print(f"{rp.stem}: {req['status']} (attempts {req.get('attempts', 0)})")
    print(f"presenter: {done}/{len(batch)} reels now have the presenter (modal exit {rc})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
