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

2026-11-22 additions (from "How I used AI to get 25 million views in 7 weeks"):
- Every reel is also scored as a MULTIPLE of a frozen yardstick (YARDSTICK views, the median
  of 1-15 Nov 2026), read once at a fixed age (READ_AGE_DAYS) and never updated after.
  3x+ = hit, 2x+ = win, 0.5-2x = normal, <0.5x = miss (usually the hook).
- Winners are IDEAS, not wordings. Each queue job carries an `idea` slug (falls back to the
  topic). An idea is PROVEN once it has beaten 2x twice or 3x once. Proven ideas rested
  >= REST_DAYS are listed as due for a re-run (hook kept almost word for word, numbers updated).
- Patterns are hints, not rules: the leading pattern is labelled "leading", not EXPLOIT.
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
IDEAS = ROOT / "metrics" / "ideas.md"

YARDSTICK = 122.0      # frozen 2026-11-22: median views of reels posted 1-15 Nov 2026. Never change.
READ_AGE_DAYS = 3      # read each reel once, at the first daily snapshot >= 3 days after posting
REST_DAYS = 30         # a proven idea rests at least this long before it is re-run


def band(m):
    if m is None:
        return "pending"
    return "HIT" if m >= 3 else "win" if m >= 2 else "normal" if m >= 0.5 else "miss"


def fixed_age_views(rows):
    """key -> views from the first snapshot taken >= READ_AGE_DAYS after posting (None if too young)."""
    from datetime import date, timedelta
    out = {}
    by_key = defaultdict(list)
    for r in rows:
        by_key[r["key"]].append(r)
    for key, rs in by_key.items():
        posted = next((r["posted_at"][:10] for r in rs if r.get("posted_at")), key[:10])
        try:
            due = (date.fromisoformat(posted) + timedelta(days=READ_AGE_DAYS)).isoformat()
        except ValueError:
            continue
        ok = sorted((r for r in rs if r["date"] >= due and r.get("views") not in ("", None, "<100")),
                    key=lambda r: r["date"])
        out[key] = num(ok[0]["views"]) if ok else None
    return out


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

    at_age = fixed_age_views([r for r in rows if "reel" in r["key"]])
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
                          score=round(score, 1),
                          idea=(j.get("idea") or r.get("topic", "")[:50]).strip().lower(),
                          multiple=(None if at_age.get(r["key"]) is None else at_age[r["key"]] / YARDSTICK)))
    reels.sort(key=lambda x: (-x["score"], -x["views"]))

    acct = list(csv.DictReader(ACCT.open())) if ACCT.exists() else []
    f_now = int(num(acct[-1]["followers"])) if acct else 0
    f_prev = int(num(acct[-2]["followers"])) if len(acct) > 1 else f_now
    med_views = st.median([x["views"] for x in reels]) if reels else 0

    by = defaultdict(list)
    zero = [x for x in reels if x["views"] <= 0]
    for x in reels:
        if x["views"] > 0:  # a 0-view reel wasn't distributed; its watch % is noise
            by[x["pattern"]].append(x)

    L = [f"# Scoreboard — {latest}", "",
         f"Followers **{f_now}** ({f_now - f_prev:+d} vs previous day). Reels tracked: {len(reels)}. "
         f"Median views per reel: {med_views:.0f}. Frozen yardstick: {YARDSTICK:.0f} views "
         f"(multiples read once at {READ_AGE_DAYS} days old).", "",
         "Score = 40·sends/reach + 25·watch% + 15·saves/reach + 10·likes/reach + 10·follows/reach (×100).", "",
         "## Reels, best first", "",
         "| Reel | Pattern | Voice | Views | ×Yardstick | Watch | Sends | Saves | Likes | Follows | Score |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in reels:
        L.append(f"| {x['key']} {x['topic']} | {x['pattern']} | {'yes' if x['narrated'] else 'no'} | {x['views']:.0f} | "
                 f"{'—' if x['multiple'] is None else format(x['multiple'], '.1f') + '× ' + band(x['multiple'])} | "
                 f"{x['watch']:.1f}s ({x['watch_pct']:.0%}) | {x['shares']:.0f} | {x['saves']:.0f} | {x['likes']:.0f} | "
                 f"{x['follows']:.0f} | {x['score']} |")
    L += ["", "## By hook pattern", "", "| Pattern | Reels | Median views | Median watch % | Median score | Call |",
          "|---|---|---|---|---|---|"]
    stats = []
    for pat, xs in by.items():
        mv = st.median([x["views"] for x in xs])
        mw = st.median([x["watch_pct"] for x in xs])
        ms = st.median([x["score"] for x in xs])  # 2026-10-21: median, so one outlier reel (7 Oct, 9 views, 15.7) cannot crown a pattern
        stats.append((ms, pat, len(xs), mv, mw))
    stats.sort(reverse=True)
    exploit = next((p for ms_, p, n_, *_ in stats if n_ >= 3), stats[0][1] if stats else None)
    for i, (ms, pat, n, mv, mw) in enumerate(stats):
        call = ("leading (a hint, not a rule)" if pat == exploit else
                "keep" if mv >= med_views else
                "drop" if n >= 3 and mv < 0.5 * med_views else "test again")
        tot = sum(x["views"] for x in by[pat])
        L.append(f"| {pat} | {n} | {mv:.0f} | {mw:.0%} | {ms:.1f} | {call}{' (low data)' if tot < 50 else ''} |")
    if zero:
        L += ["", "Left out of pattern stats (0 views, not distributed — check the post): "
              + ", ".join(x["key"] for x in zero) + "."]
    narr = [x for x in reels if x["narrated"]]
    sil = [x for x in reels if not x["narrated"]]
    if narr and sil:
        L += ["", f"Narrated reels: median views {st.median([x['views'] for x in narr]):.0f}, "
                  f"watch {st.median([x['watch_pct'] for x in narr]):.0%} — silent reels: "
                  f"{st.median([x['views'] for x in sil]):.0f}, {st.median([x['watch_pct'] for x in sil]):.0%}."]
    L += ["", "## Rule for the next batch", "",
          "- Patterns are hints, not rules. At least 1 new reel in 3 deliberately goes AGAINST the leading pattern.",
          "- No reel opens the same way (same first words / same hook shape) as either of the two before it.",
          "- One re-run of a proven idea per day at most (see metrics/ideas.md); keep its hook almost word for word, update every number.",
          "- Judge against the frozen yardstick, never this week's median: a falling median makes every week look normal.",
          "- Watch % under 20%: the first 2 seconds failed. Rewrite hooks: shorter, a number in the first line, and a direct 'you'.",
          "- Zero sends across the board: topics need a 'send this to someone' reason (a mistake a friend is making, a rule that changed)."]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(L) + "\n")
    write_ideas(reels, latest)
    print(f"review: scoreboard written for {latest} ({len(reels)} reels)")
    return 0


def write_ideas(reels, latest):
    """Idea ledger: proven ideas and when each is next due for a re-run."""
    from datetime import date
    ideas = defaultdict(list)
    for x in reels:
        ideas[x["idea"]].append(x)
    L = [f"# Idea ledger — {latest}", "",
         f"Proven = beat 2× the {YARDSTICK:.0f}-view yardstick twice, or 3× once (read at {READ_AGE_DAYS} days). "
         f"A proven idea rests {REST_DAYS}+ days, then is re-run with its hook almost word for word and every number updated. "
         "At most one re-run a day.", "",
         "| Idea | Runs | Best ×Yardstick | Wins (2×+) | Hits (3×+) | Status | Last run | Due |",
         "|---|---|---|---|---|---|---|---|"]
    rows = []
    for idea, xs in ideas.items():
        ms = [x["multiple"] for x in xs if x["multiple"] is not None]
        wins = sum(m >= 2 for m in ms)
        hits = sum(m >= 3 for m in ms)
        proven = hits >= 1 or wins >= 2
        last = max(x["key"][:10] for x in xs)
        rested = (date.fromisoformat(latest) - date.fromisoformat(last)).days
        status = "PROVEN" if proven else ("promising" if wins == 1 else "")
        due = ("DUE NOW" if rested >= REST_DAYS else f"in {REST_DAYS - rested} d") if proven else ""
        rows.append((not proven, -(max(ms) if ms else 0), idea, len(xs), max(ms) if ms else None, wins, hits, status, last, due))
    rows.sort()
    for _, _, idea, n, best, wins, hits, status, last, due in rows:
        if not status:
            continue
        L.append(f"| {idea[:60]} | {n} | {best:.1f}× | {wins} | {hits} | {status} | {last} | {due} |")
    if len(L) == 6:
        L.append("| (none yet) | | | | | | | |")
    IDEAS.write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
