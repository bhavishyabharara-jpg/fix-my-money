#!/usr/bin/env python3
"""
Fix My Money — trial reel planner.

Instagram trial reels are shown to non-followers first and only reach followers if they
perform. That makes them a free second shot for reels that already proved themselves,
without crowding the main grid (the 1-reel-a-day test is about follower fatigue).

Every publish run, this keeps LEAD_DAYS days of trial jobs queued, one per date at
TRIAL_TIME UTC (12:15 IST):
  - candidate = a published single-video reel, at least MIN_AGE_DAYS old, not itself a
    trial, never re-posted as a trial before, whose video is still in the repo, and whose
    topic isn't seasonal (Diwali, Dhanteras, a budget, "this week"...);
  - best candidate = most views in the latest metrics snapshot;
  - the job copies the original's media and caption, and adds trial + repost_of.

Safety stop: if any trial that was due more than STALE_HOURS ago never published
(e.g. Instagram rejected trial_params), no new trials are planned until someone looks.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "queue"
STATE = ROOT / "published.json"
POSTS = ROOT / "metrics" / "posts.csv"

LEAD_DAYS = 3
TRIAL_TIME = "06:45"          # UTC = 12:15 IST, well away from the 19:15 IST main reel
MIN_AGE_DAYS = 5
STALE_HOURS = 6
SEASONAL = re.compile(r"diwali|dhanteras|holi|navratri|budget 20|this week|this month|"
                      r"deadline|last date|festive|rakhi|new year|tomorrow|today",
                      re.IGNORECASE)


def latest_views() -> dict[str, int]:
    views: dict[str, tuple[str, int]] = {}
    if not POSTS.exists():
        return {}
    with POSTS.open() as f:
        for row in csv.DictReader(f):
            try:
                v = int(row.get("views") or 0)
            except ValueError:
                continue
            key, day = row["key"], row["date"]
            if key not in views or day >= views[key][0]:
                views[key] = (day, v)
    return {k: v for k, (_, v) in views.items()}


def main() -> int:
    now = datetime.now(timezone.utc)
    published = json.loads(STATE.read_text())["published"] if STATE.exists() else {}
    jobs = {p.stem: json.loads(p.read_text()) for p in sorted(QUEUE.glob("*.json"))}
    trials = {k: j for k, j in jobs.items() if j.get("trial")}

    for key, job in trials.items():
        due = datetime.strptime(job["publish_at"][:16], "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
        if key not in published and now - due > timedelta(hours=STALE_HOURS):
            print(f"trials: STOPPED — {key} was due {job['publish_at']} UTC and never published. "
                  "Check the publish log; no new trials until it is fixed or removed.")
            return 0

    used = {j.get("repost_of") for j in trials.values()}
    views = latest_views()
    candidates = []
    for key, meta in published.items():
        job = jobs.get(key)
        if not job or job.get("trial") or job.get("slot") != "reel":
            continue
        media = job.get("media") or []
        if key in used or len(media) != 1 or not (ROOT / media[0]).exists():
            continue
        try:
            posted = datetime.strptime(str(meta.get("at", ""))[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if now - posted < timedelta(days=MIN_AGE_DAYS):
            continue
        if SEASONAL.search(job.get("topic", "") + " " + job.get("caption", "")[:200]):
            continue
        candidates.append((views.get(key, 0), key))
    candidates.sort(reverse=True)

    trial_dates = {j["date"] for j in trials.values()}
    added = 0
    for d in range(1, LEAD_DAYS + 1):
        day = (now + timedelta(days=d)).strftime("%Y-%m-%d")
        if day in trial_dates:
            continue
        if not candidates:
            print("trials: no eligible reel left to re-post as a trial")
            break
        v, src = candidates.pop(0)
        orig = jobs[src]
        job = {k: orig[k] for k in ("slot", "topic", "idea", "hook_pattern", "caption",
                                    "media", "cover", "sources", "duration_s") if k in orig}
        job.update({
            "date": day,
            "publish_at": f"{day}T{TRIAL_TIME}",
            "trial": "SS_PERFORMANCE",
            "repost_of": src,
            "experiment": (f"TRIAL REEL (auto): re-post of {src} ({v} views at last snapshot) as an "
                           "Instagram trial reel, shown to non-followers first; graduates to "
                           "followers only if it performs. Judge at 3 days on views vs the original."),
        })
        (QUEUE / f"{day}-trial.json").write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n")
        print(f"trials: queued {day}-trial <- {src} ({v} views)")
        added += 1
    if not added:
        print("trials: queue already full")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
