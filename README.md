# Fix My Money — auto-publisher

This repository publishes @fix_mymoney. It does two jobs:

1. **Hosts the media.** GitHub Pages serves `media/` over public URLs, which is the only
   way Instagram's API will accept a video or image — it fetches the file itself.
2. **Publishes the post.** A GitHub Action calls the Instagram Content Publishing API.

Nothing here depends on a browser, a laptop being awake, or anyone tapping Share.

## How a post gets published

Claude writes the day's post, renders it, and commits two things:

- the media, to `media/<date>/<slot>/`
- a job file, to `queue/<date>-<slot>.json`

That push triggers `.github/workflows/publish.yml`, which runs `tools/publish.py`:
it waits for Pages to serve the media, creates the Instagram container, polls until
Instagram has ingested it, publishes, and appends the result to `published.json`.

A job that fails stays in the queue. The workflow also runs hourly, so a transient
failure fixes itself on the next pass without anyone intervening.

### Job file shape

```json
{
  "date": "2026-10-03",
  "slot": "reel",
  "topic": "Gold is up ~28% in a year. How much belongs in a portfolio?",
  "caption": "Full caption, already compliance-checked, ending with sources and\nFor education only. Not investment advice.",
  "media": ["media/2026-10-03/reel/reel.mp4"],
  "cover": "media/2026-10-03/reel/reel_cover.png"
}
```

`slot` is `reel` or `carousel`. A carousel lists its slides in `media`, in order, 2–10 of
them, and takes no `cover`.

## One-time setup

Three steps, once. There is no Facebook Page in this setup and no OAuth flow to build —
this uses **Instagram API with Instagram Login**, where the account authorises itself and
the dashboard hands you a long-lived token directly.

### 1. Make the Instagram account eligible

Instagram only allows API publishing from a **Business** or **Creator** account.

On the phone, in the @fix_mymoney app: **Settings → Account type and tools →
Switch to professional account → Creator**. Free, keeps the handle and the posts, and
turns on Insights — which the weekly review currently can't read.

### 2. Create the Meta app and click one button

1. developers.facebook.com → **My Apps → Create app** → app type **Business** → name it
   `fix-my-money`.
2. **Add product → Instagram → Set up**.
3. Open **Instagram → API setup with Instagram business login**.
   - **Add account**, and sign in as @fix_mymoney when asked.
   - Next to the account, click **Generate token**. Copy it.
   - That token is long-lived: **valid 60 days**, no debugger, no extending, no
     `/me/accounts` hunt.
4. The same panel shows the **Instagram account ID** next to the connected account.
   Copy it. (If you'd rather confirm it: `GET https://graph.instagram.com/v21.0/me
   ?fields=user_id,username&access_token=<token>`.)

### 3. Put the credentials where only the Action can see them

In this repo: **Settings → Secrets and variables → Actions**.

Under **Secrets** → *New repository secret*:

| Name | Value |
|---|---|
| `IG_ACCESS_TOKEN` | the token from step 2.3 |
| `IG_USER_ID` | the Instagram account id from step 2.4 |

Under **Variables** → *New repository variable*:

| Name | Value |
|---|---|
| `PAGES_BASE` | `https://<your-github-username>.github.io/fix-my-money` |

And enable Pages: **Settings → Pages → Source: Deploy from a branch → `main` / `root`**.

Paste the token into GitHub directly. It should not be sent through chat, committed to a
file, or pasted anywhere else — it can post as the account until it is revoked.

**The token expires every 60 days.** A scheduled reminder asks for a fresh one before it
lapses; regenerating is the same **Generate token** button and a paste into the secret.
If it ever does lapse first, the workflow turns red, GitHub emails you, and nothing is
lost — the queue just waits and goes out once the secret is updated.

## Checking on it

- **Actions** tab shows every publish attempt and why anything failed.
- `published.json` is the record of what actually went live, with Instagram's media id.
- To retry something by hand: **Actions → Publish to Instagram → Run workflow**.
- To re-publish a post deliberately, delete its entry from `published.json`.

## Limits worth knowing

- 100 API posts per rolling 24 hours. Two a day is nowhere near it.
- Reels: MP4/MOV, H.264, AAC audio, 9:16, 5–90 seconds, under 100 MB.
- Carousels: 2–10 images, JPEG or PNG.
- Captions: 2,200 characters, 30 hashtags.
