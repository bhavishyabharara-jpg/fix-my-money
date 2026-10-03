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

These four steps need a human. Do them once, in order.

### 1. Make the Instagram account eligible

Instagram only allows API publishing from a **Business** or **Creator** account.

On the phone, in the @fix_mymoney app: **Settings → Account type and tools →
Switch to professional account → Creator** (Business is fine too). Free, keeps the
handle and the posts, and turns on Insights — which the weekly review currently
can't read.

### 2. Link a Facebook Page

The publishing API reaches Instagram through a Page. A brand-new empty Page is fine;
nothing is ever posted to it.

- facebook.com/pages/create → name it **Fix My Money** → create.
- Then in the Instagram app: **Settings → Account type and tools → Sharing to other
  apps → Facebook** → connect that Page.

### 3. Create the Meta app and get a token

1. developers.facebook.com → **My Apps → Create App** → use case **Other** → type
   **Business** → name it `fix-my-money`.
2. In the app, **Add product → Instagram → Set up** (the "Instagram Graph API" /
   API setup with Facebook login path).
3. Open the **Graph API Explorer** (developers.facebook.com/tools/explorer):
   - Pick your app, top right.
   - **Add permissions**: `instagram_basic`, `instagram_content_publish`,
     `pages_show_list`, `pages_read_engagement`, `business_management`.
   - **Generate Access Token**, and allow the Page and Instagram account when asked.
4. That token lasts an hour. Make it permanent:
   - **Access Token Debugger** (developers.facebook.com/tools/debug/accesstoken) →
     paste it → **Extend Access Token**. You now have a 60-day user token.
   - Back in the Explorer with the extended token, call `GET /me/accounts`. Find your
     Page and copy its `access_token` — **a Page token derived from a long-lived user
     token does not expire.** That is the one to keep.
5. Get the Instagram account id: in the Explorer, call
   `GET /<page-id>?fields=instagram_business_account`. Copy the id it returns.

### 4. Put the credentials where only the Action can see them

In this repo: **Settings → Secrets and variables → Actions**.

Under **Secrets** → *New repository secret*:

| Name | Value |
|---|---|
| `IG_ACCESS_TOKEN` | the non-expiring Page token from step 3.4 |
| `IG_USER_ID` | the Instagram account id from step 3.5 |

Under **Variables** → *New repository variable*:

| Name | Value |
|---|---|
| `PAGES_BASE` | `https://<your-github-username>.github.io/fix-my-money` |

And enable Pages: **Settings → Pages → Source: Deploy from a branch → `main` / `root`**.

Paste the token into GitHub directly. It should not be sent through chat, committed to
a file, or pasted anywhere else — a Page token with `instagram_content_publish` can post
as the account until it is revoked.

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
