#!/usr/bin/env python3
"""
Fix My Money — daily performance snapshot.

Once per UTC day, records how every published post is doing, so the daily review can
look at numbers instead of guessing. Writes:

    metrics/posts.csv      one row per post per day: views, reach, saves, shares, ...
    metrics/account.csv    one row per day: followers, total posts

Basic fields (likes, comments, followers) work with the publishing token as it is.
Reach, views, saves, shares and watch time need the `instagram_business_manage_insights`
permission on the token; without it those columns stay blank and the script says so once,
rather than failing the publish run.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GRAPH = "https://graph.instagram.com/v21.0"
ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "published.json"
OUT = ROOT / "metrics"
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()

# Asked for one at a time: Instagram rejects the whole request if any single metric
# doesn't apply to that media type, and a reel and a carousel accept different sets.
INSIGHTS = ["views", "reach", "saved", "shares", "total_interactions", "ig_reels_avg_watch_time",
            "profile_visits", "follows"]
POST_COLS = ["date", "key", "slot", "media_id", "posted_at", "likes", "comments"] + INSIGHTS + ["topic", "permalink"]


def get(path: str, params: dict) -> dict:
    url = f"{GRAPH}/{path}?{urllib.parse.urlencode(dict(params, access_token=TOKEN))}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read().decode())


def insight(media_id: str, metric: str):
    """One metric for one post. Returns "" when Instagram won't give a number for it.

    Instagram answers code 10 both for "your token lacks the permission" and for
    "not enough viewers for this media to show insights" (any post under ~100 views).
    Only the first means stop asking; the second is normal for a new account.
    """
    try:
        data = get(f"{media_id}/insights", {"metric": metric}).get("data", [])
        return data[0]["values"][0]["value"] if data else ""
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        try:
            msg = json.loads(body).get("error", {}).get("message", "")
        except Exception:
            msg = body
        low = msg.lower()
        if "not enough viewers" in low:
            return "<100"
        if "permission" in low and "insights" in low or "instagram_business_manage_insights" in low:
            raise PermissionError(msg) from None
        NOTES.add(f"{metric}: {msg[:120]}")
        return ""
    except Exception:
        return ""


NOTES: set = set()


def main() -> int:
    if not TOKEN:
        print("metrics: no token, skipped")
        return 0
    today = time.strftime("%Y-%m-%d", time.gmtime())
    OUT.mkdir(exist_ok=True)
    acct_file, posts_file = OUT / "account.csv", OUT / "posts.csv"

    if acct_file.exists() and any(r.get("date") == today for r in csv.DictReader(acct_file.open())):
        print(f"metrics: snapshot for {today} already taken")
        return 0

    try:
        me = get("me", {"fields": "username,followers_count,follows_count,media_count"})
    except Exception as exc:
        print(f"metrics: account lookup failed ({type(exc).__name__}); skipped")
        return 0
    new = not acct_file.exists()
    with acct_file.open("a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["date", "followers", "following", "posts"])
        w.writerow([today, me.get("followers_count", ""), me.get("follows_count", ""), me.get("media_count", "")])
    print(f"metrics: @{me.get('username')} followers={me.get('followers_count')} posts={me.get('media_count')}")

    published = json.loads(STATE.read_text())["published"] if STATE.exists() else {}
    have_insights = True
    rows = []
    for key, rec in sorted(published.items()):
        mid = rec.get("media_id")
        if not mid:
            continue
        try:
            basic = get(mid, {"fields": "like_count,comments_count,timestamp,permalink,media_type"})
        except Exception:
            continue
        row = {
            "date": today, "key": key, "slot": key.split("-")[3] if key.count("-") >= 3 else "",
            "media_id": mid, "posted_at": basic.get("timestamp", ""),
            "likes": basic.get("like_count", ""), "comments": basic.get("comments_count", ""),
            "topic": rec.get("topic", ""), "permalink": basic.get("permalink", ""),
        }
        for m in INSIGHTS:
            if not have_insights:
                row[m] = ""
                continue
            try:
                row[m] = insight(mid, m)
            except PermissionError as exc:
                have_insights = False
                NOTES.add(f"permission: {str(exc)[:120]}")
                row[m] = ""
        rows.append(row)

    # If the column set grew since the file was started, rewrite it with the new header
    # (old rows keep blanks in the new columns) so the CSV stays readable.
    if posts_file.exists():
        with posts_file.open() as fh:
            old_rows = list(csv.DictReader(fh))
            old_cols = old_rows and list(old_rows[0].keys())
        if old_rows and old_cols != POST_COLS:
            with posts_file.open("w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=POST_COLS, extrasaction="ignore")
                w.writeheader()
                w.writerows(old_rows)
    new = not posts_file.exists()
    with posts_file.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=POST_COLS)
        if new:
            w.writeheader()
        w.writerows(rows)
    print(f"metrics: {len(rows)} posts recorded")
    for n in sorted(NOTES):
        print(f"metrics note: {n}")
    if not have_insights:
        print("metrics: reach/views/saves/shares need the instagram_business_manage_insights "
              "permission on the token — those columns are blank until it is added.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
