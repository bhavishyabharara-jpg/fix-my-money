#!/usr/bin/env python3
"""
Fix My Money — Instagram publisher.

Reads every unpublished job in queue/, publishes it to Instagram through the Content
Publishing API, and records the result. Designed to run in GitHub Actions, where the
media it publishes is served by this same repository's GitHub Pages site, so Instagram
can fetch it over a public URL.

A job is queue/<date>-<slot>.json:

    {
      "date": "2026-10-03",
      "slot": "reel",                      # "reel" or "carousel"
      "topic": "...",                      # for the log only
      "caption": "...",                    # full caption, already compliance-checked
      "media": ["media/2026-10-03/reel/reel.mp4"],      # repo-relative, in Pages order
      "cover": "media/2026-10-03/reel/reel_cover.png"   # reels only, optional
    }

Published jobs are appended to published.json and never retried. Nothing here writes
content: if a job is malformed the publisher refuses it rather than guessing.

Environment:
    IG_ACCESS_TOKEN   long-lived token, generated in the Meta app dashboard (Actions secret)
    IG_USER_ID        the Instagram account's numeric id                    (Actions secret)
    PAGES_BASE        e.g. https://<user>.github.io/<repo>                  (Actions variable)

The token is good for 60 days. When it lapses, every call here fails with an auth error
and the workflow goes red, which GitHub emails about — and a scheduled reminder asks for
a fresh one before that happens.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Instagram API with Instagram Login: the account talks for itself, so there is no
# Facebook Page in the path and no page token to derive.
GRAPH = "https://graph.instagram.com/v21.0"

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "queue"
STATE = ROOT / "published.json"

TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
IG_USER = os.environ.get("IG_USER_ID", "")
PAGES = os.environ.get("PAGES_BASE", "").rstrip("/")

# Instagram gives a container up to 24h, but a 23s reel is normally FINISHED well
# inside a minute. Back off gently rather than hammering the endpoint.
POLL_DELAYS = [5, 5, 10, 10, 15, 15, 20, 20, 30, 30, 30, 60, 60, 60]


class PublishError(RuntimeError):
    """Something went wrong that a retry on the next run will not fix by itself."""


# ---------------------------------------------------------------- Graph API plumbing
def _call(method: str, path: str, params: dict) -> dict:
    """One Graph API call. The token travels in the POST body / query, never in a log line."""
    payload = dict(params, access_token=TOKEN)
    url = f"{GRAPH}/{path}"
    if method == "GET":
        url = f"{url}?{urllib.parse.urlencode(payload)}"
        req = urllib.request.Request(url, method="GET")
    else:
        req = urllib.request.Request(
            url, data=urllib.parse.urlencode(payload).encode(), method="POST"
        )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        # Meta labels almost every 4xx an "OAuthException", including permission and media
        # errors, so only subcode 190 actually means the token is dead. Everything else gets
        # reported as Meta worded it — guessing here hides the real problem.
        if exc.code in (400, 401):
            try:
                err = json.loads(body).get("error", {})
            except Exception:
                err = {}
            if err.get("code") == 190:
                raise PublishError(
                    "the Instagram token has expired or been revoked. Generate a fresh one "
                    "(Meta app dashboard -> Instagram -> API setup with Instagram business "
                    "login -> Generate token) and update the IG_ACCESS_TOKEN secret."
                ) from None
            detail = err.get("error_user_msg") or err.get("message") or _redact(body)
            raise PublishError(
                f"{method} {path} -> {detail}"
                f" [code={err.get('code')} subcode={err.get('error_subcode')}]"
            ) from None
        # Never echo the token back out, whatever the API decided to quote at us.
        raise PublishError(f"{method} {path} -> HTTP {exc.code}: {_redact(body)}") from None
    except urllib.error.URLError as exc:
        raise PublishError(f"{method} {path} -> {exc.reason}") from None


def _redact(text: str) -> str:
    return text.replace(TOKEN, "***") if TOKEN else text


def container(**params) -> str:
    """Create a media container and return its id."""
    return _call("POST", f"{IG_USER}/media", params)["id"]


def wait_ready(container_id: str, what: str) -> None:
    """Poll until Instagram has finished ingesting the media, or give up loudly."""
    for delay in POLL_DELAYS:
        time.sleep(delay)
        info = _call("GET", container_id, {"fields": "status_code,status"})
        code = info.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise PublishError(f"{what}: Instagram rejected the media ({code}) — {info.get('status', '')}")
    raise PublishError(f"{what}: still processing after {sum(POLL_DELAYS)}s; left for the next run")


def publish(container_id: str) -> str:
    return _call("POST", f"{IG_USER}/media_publish", {"creation_id": container_id})["id"]


# ---------------------------------------------------------------- the two post shapes
def publish_reel(job: dict) -> str:
    media = job["media"]
    if len(media) != 1:
        raise PublishError("a reel job must carry exactly one video")
    params = {
        "media_type": "REELS",
        "video_url": url_for(media[0]),
        "caption": job["caption"],
        "share_to_feed": "true",
    }
    if job.get("cover"):
        params["cover_url"] = url_for(job["cover"])
    cid = container(**params)
    wait_ready(cid, "reel")
    return publish(cid)


def publish_carousel(job: dict) -> str:
    media = job["media"]
    if not 2 <= len(media) <= 10:
        raise PublishError(f"a carousel needs 2–10 slides, got {len(media)}")
    children = []
    for i, rel in enumerate(media, 1):
        cid = container(image_url=url_for(rel), is_carousel_item="true")
        children.append(cid)
        wait_ready(cid, f"slide {i}")
    parent = container(
        media_type="CAROUSEL", children=",".join(children), caption=job["caption"]
    )
    wait_ready(parent, "carousel")
    return publish(parent)


def url_for(repo_path: str) -> str:
    """A repo-relative media path as the public URL Instagram will fetch."""
    return f"{PAGES}/{urllib.parse.quote(repo_path.lstrip('/'))}"


# ---------------------------------------------------------------- job bookkeeping
def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"published": {}}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def pending(state: dict) -> list[Path]:
    done = state["published"]
    jobs = [p for p in sorted(QUEUE.glob("*.json")) if p.stem not in done]
    return jobs


def check_reachable(job: dict) -> None:
    """Pages can lag a push by a minute. Confirm the media is actually live before
    asking Instagram to fetch it, so a 404 doesn't come back as an opaque media error."""
    for rel in list(job["media"]) + ([job["cover"]] if job.get("cover") else []):
        url = url_for(rel)
        for attempt in range(10):
            try:
                req = urllib.request.Request(url, method="HEAD")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if resp.status == 200:
                        break
            except Exception:
                pass
            time.sleep(15)
        else:
            raise PublishError(f"media not reachable at {url} — is GitHub Pages enabled and built?")


def validate(job: dict, path: Path) -> None:
    for field in ("date", "slot", "caption", "media"):
        if not job.get(field):
            raise PublishError(f"{path.name}: missing '{field}'")
    if job["slot"] not in ("reel", "carousel"):
        raise PublishError(f"{path.name}: slot must be 'reel' or 'carousel'")
    if len(job["caption"]) > 2200:
        raise PublishError(f"{path.name}: caption is {len(job['caption'])} chars, limit is 2200")
    for rel in job["media"]:
        if not (ROOT / rel).exists():
            raise PublishError(f"{path.name}: {rel} is not in the repo")


def main() -> int:
    missing = [n for n, v in (("IG_ACCESS_TOKEN", TOKEN), ("IG_USER_ID", IG_USER), ("PAGES_BASE", PAGES)) if not v]
    if missing:
        print(f"Not configured yet: {', '.join(missing)}. Nothing published.")
        return 0

    state = load_state()
    jobs = pending(state)
    if not jobs:
        print("Nothing pending.")
        return 0

    failures = 0
    for path in jobs:
        job = json.loads(path.read_text())
        label = f"{job.get('date', '?')} {job.get('slot', '?')}"
        try:
            validate(job, path)
            check_reachable(job)
            media_id = publish_reel(job) if job["slot"] == "reel" else publish_carousel(job)
        except PublishError as exc:
            # Leave it in the queue. The next run tries again; a genuinely broken job
            # keeps saying so in the log until someone looks.
            print(f"FAILED  {label}: {exc}")
            failures += 1
            continue
        state["published"][path.stem] = {
            "media_id": media_id,
            "topic": job.get("topic", ""),
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        save_state(state)
        print(f"PUBLISHED  {label}  -> {media_id}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
