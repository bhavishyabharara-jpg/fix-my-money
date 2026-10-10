#!/usr/bin/env python3
"""
Fix My Money — daily scoreboard.

Turns the raw daily snapshots (metrics/posts.csv) plus what we know about each reel
(queue/*.json: hook_pattern, topic, slot, duration) into metrics/scoreboard.md: one table
the daily run reads before deciding what to make next.

The score for a reel is built from the signals Instagram uses to decide whether to show it
to more non-followers, in rough order of weight:
    sends (shares) per reach  >  watch time %  >  saves per reach  >  likes per reach
plus follows, which is the goal itself. Views alone mostly measure how big the test pool was.
"""
from __future__ import annotations

import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "metrics" / "posts.csv"
ACCT = ROOT / "metrics" / "account.csv"
OUT = ROOT / "metrics" / "scoreboard.md"


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def norm(p):
    p = (p or "untagged").split(" ")[0].split("(")[0].strip().lower()
    keys = ("big-question", "contrarian-number", "news-stakes", "news-list", "ranking", "audit", "relatable")
    for key in keys:
        if p.startswith(key):
            return key
    for key in keys:
        if key.startswith(p) or p.startswith(key.split("-")[0]) and "news" not in p:
            return key
    return p


def main() -> int:
    if not POSTS.exists():
        print("review: no metrics yet")
        return 0
    rows = list(csv.DictReader(POSTS.open()))
    latest = max(r["date"] for r in rows)
    snap = [r for r in rows if r["date"] == latest and "reel" in r["key"]]
    jobs = {p.stem: json.loads(p.read_text()) for p in (ROOT / "queue").glob("*.json")}

    reels = []
    for r in snap:
        j = jobs.get(r["key"], {})
        views, reach = num(r.get("views")), max(num(r.get("reach")), 1.0)
        dur = num(j.get("duration_s")) or 20.0
        watch = num(r.get("ig_reels_avg_watch_time")) / 1000.0
        shares, saves, likes = num(r.get("shares")), num(r.get("saved")), num(r.get("likes"))
        follows = num(r.get("follows"))
        watch_pct = min(1.0, watch / dur) if dur else 0.0
        score = (40 * shares / reach + 25 * watch_pct + 15 * saves / reach + 10 * likes / reach + 10 * follows / reach)
        reels.append(dict(key=r["key"], topic=r.get("topic", "")[:60], pattern=norm(j.get("hook_pattern")),
                          narrated=bool(j.get("spec")), views=views, reach=reach, watch=watch, dur=dur,
                          watch_pct=watch_pct, shares=shares, saves=saves, likes=likes, follows=follows,
                          score=round(score, 1)))
    reels.sort(key=lambda x: (-x["score"], -x["views"]))

    acct = list(csv.DictReader(ACCT.open())) if ACCT.exists() else []
    f_now = int(num(acct[-1]["followers"])) if acct else 0
    f_prev = int(num(acct[-2]["followers"])) if len(acct) > 1 else f_now
    med_views = st.median([x["views"] for x in reels]) if reels else 0

    by = defaultdict(list)
    for x in reels:
        by[x["pattern"]].append(x)

    L = [f"# Scoreboard — {latest}", "",
         f"Followers **{f_now}** ({f_now - f_prev:+d} vs previous day). Reels tracked: {len(reels)}. "
         f"Median views per reel: {med_views:.0f}.", "",
         "Score = 40·sends/reach + 25·watch% + 15·saves/reach + 10·likes/reach + 10·follows/reach (×100).", "",
         "## Reels, best first", "",
         "| Reel | Pattern | Voice | Views | Watch | Sends | Saves | Likes | Follows | Score |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for x in reels:
        L.append(f"| {x['key']} {x['topic']} | {x['pattern']} | {'yes' if x['narrated'] else 'no'} | {x['views']:.0f} | "
                 f"{x['watch']:.1f}s ({x['watch_pct']:.0%}) | {x['shares']:.0f} | {x['saves']:.0f} | {x['likes']:.0f} | "
                 f"{x['follows']:.0f} | {x['score']} |")
    L += ["", "## By hook pattern", "", "| Pattern | Reels | Median views | Median watch % | Mean score | Call |",
          "|---|---|---|---|---|---|"]
    stats = []
    for pat, xs in by.items():
        mv = st.median([x["views"] for x in xs])
        mw = st.median([x["watch_pct"] for x in xs])
        ms = st.mean([x["score"] for x in xs])
        stats.append((ms, pat, len(xs), mv, mw))
    stats.sort(reverse=True)
    for i, (ms, pat, n, mv, mw) in enumerate(stats):
        call = ("EXPLOIT" if i == 0 and n >= 1 else
                "keep" if mv >= med_views else
                "drop" if n >= 3 and mv < 0.5 * med_views else "test again")
        tot = sum(x["views"] for x in by[pat])
        L.append(f"| {pat} | {n} | {mv:.0f} | {mw:.0%} | {ms:.1f} | {call}{' (low data)' if tot < 50 else ''} |")
    narr = [x for x in reels if x["narrated"]]
    sil = [x for x in reels if not x["narrated"]]
    if narr and sil:
        L += ["", f"Narrated reels: median views {st.median([x['views'] for x in narr]):.0f}, "
                  f"watch {st.median([x['watch_pct'] for x in narr]):.0%} — silent reels: "
                  f"{st.median([x['views'] for x in sil]):.0f}, {st.median([x['watch_pct'] for x in sil]):.0%}."]
    L += ["", "## Rule for the next batch", "",
          "- About 60% of new reels use the EXPLOIT pattern, about 25% a 'keep' pattern, and about 15% test something new.",
          "- Never queue two reels of the same pattern back to back.",
          "- Watch % under 20%: the first 2 seconds failed. Rewrite hooks: shorter, a number in the first line, and a direct 'you'.",
          "- Zero sends across the board: topics need a 'send this to someone' reason (a mistake a friend is making, a rule that changed)."]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(L) + "\n")
    print(f"review: scoreboard written for {latest} ({len(reels)} reels)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
