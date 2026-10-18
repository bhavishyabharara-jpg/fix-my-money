# Fix My Money (@fix_mymoney) — Operating Playbook

Faceless, education-only Instagram page that helps Indian investors fix their finances. Brand: "Fix My Money", handle @fix_mymoney. Independent brand: never mention any company, app, product, advisor or service. Organic only: no ads, no boosts, no paid collabs. No conversion CTAs.

## Audience
- **Portfolio Optimizer (32–40):** already invested, 5–20+ funds across apps, worried about overlap, risk, too many funds, "should I change anything?". Wants diagnosis and clarity. Priority audience for depth.
- **Goal Aware Wealth Builder (25–32):** small/simple portfolio, rising income, asking "how much do I need / invest / am I on track?". Wants simple explanations and goal maths. Biggest reach driver.
- Language: English, plain words, short sentences. Name the viewer in the first line (age, salary band, fund count).

## Folder layout (Mac: ~/Documents/Money X-Ray — folder name kept for the scheduled tasks)
- `engine/render.py`, `engine/config.json`, `engine/fonts/` — renderer
- `calendar.json` — 30-day topic plan (day → date, reel hook, carousel topic, audience)
- `posts/YYYY-MM-DD/post.json` — the day's content; `carousel/slide_NN.png`, `carousel/carousel_caption.txt`, `reel/reel.mp4`, `reel/reel_caption.txt`
- `log.csv` — one row per publish attempt: date,slot,topic,status,notes
- `learnings.md` — weekly review notes; read before writing any post

## Daily run (carousel 8:30 am IST, reel 7:30 pm IST)
0. If today's IST date is before `launch_date` in calendar.json, stop (log nothing). If post.json and rendered files for today already exist and pass the compliance check, skip to step 8.
1. Read this playbook, `learnings.md`, `calendar.json`, and the last 7 rows of `log.csv`. If today's slot is already `posted`, stop.
2. If `posts/<today>/post.json` doesn't exist, write it: take today's calendar topic. Check today's news with WebSearch (markets, AMFI data, SEBI/RBI/tax changes). If something big broke in the last 24 h and it's a flex day (Sat/Sun) or clearly bigger, use it instead and note the swap in log.csv.
3. Research facts: open (WebFetch) the source pages for every number used. No number without a source. Put the source on the slide (`"source"`) and in the caption.
4. Write content in the schema below. Carousel: 7–9 slides (cover → 5–7 value slides → end). Reel: 5–7 scenes, 18–28 s total, one idea.
5. Compliance self-check (all must pass, else rewrite):
   - No buy/sell/hold of any named fund, stock, ETF or AMC. Use categories ("Large-cap fund A").
   - No prices of specific securities less than 3 months old. Index levels and industry data from news are fine, with source.
   - Projections labelled "illustrative, assuming X% a year". No promised or implied returns.
   - No testimonials, no "our followers made...".
   - No company/app/product/brand mentions; no links; no "DM us", no comment keywords, no link in bio.
   - Caption ends with the data source(s) + "For education only. Not investment advice."
   - Only value prompts allowed: save, send/share, follow.
6. Render in the cloud workspace: stage `engine/` files and post.json from the Mac, `pip install numpy pillow --break-system-packages` if needed, then `python3 engine/render.py posts/<date>/post.json posts/<date> --only carousel|reel`. Look at the rendered PNGs / a few reel frames (ffmpeg -ss) and fix overflow or cramped text before continuing.
7. Commit the outputs back into `posts/<date>/` on the Mac.
7b. Copy the finished files into the cloud outputs folder too (`/mnt/user-data/outputs/<date>-<slot>/`). The browser upload tool cannot read Mac paths — only this copy is uploadable.
8. Publish on instagram.com in Chrome (Claude in Chrome). FIRST confirm the active account is **@fix_mymoney** (profile link / account switcher). Chrome is also logged in to the owner's PERSONAL account: never post from it. If @fix_mymoney is not active, switch via the account switcher only if it is already listed there; otherwise log `skipped: wrong account` and stop.
   Then: Create → Post → select files with file_upload on the hidden file input (never click the native picker) → for carousel select all slides in order; for reel upload reel.mp4 and choose 9:16 / original crop → Next → paste caption → Share. Confirm the post appears on the profile.
   **ONE ATTEMPT ONLY.** The upload goes through a permission check that refuses non-deterministically — same files, same action, different answer run to run. If it is refused, blocked, or the dialog does not advance, do NOT retry, do NOT try another file location, tool or path. Move straight to step 8b. Never bypass CAPTCHAs, logins or verification.
8b. HAND OVER. Whatever happened, finish with SendUserMessage — the owner reads it on his phone, so keep it to four lines. If it published, say so and name the topic. If it did not, say it is rendered and waiting, give the folder path on the Mac, the topic, and the one-line manual route: open Instagram → Create → drag the files → (reel: keep original crop) → paste the caption file → Share. The post is not "missed" — it is ready and waiting for a tap.
9. Append to log.csv: date,slot,topic,status,notes. Status is `posted` (live), `ready` (rendered, waiting for his tap) or `failed` (content could not be produced). A `ready` row is the next run's first priority.

## Weekly review (Sunday 11 am IST)
- In Chrome, open the profile and each post of the week; read visible likes, comments and, if available, Insights (reach, saves, shares, follows).
- Write 5–8 bullet learnings to `learnings.md` (top/bottom posts, hooks that worked, pillar performance).
- Update the next 7 days in `calendar.json` (keep pillars ~35% Optimizer X-rays, 30% goal maths, 20% news, 15% mistakes). After day 30, extend the calendar 7 days at a time.

## post.json schema
Rich text in any text field: `**mint accent**`, `[[red alert]]`, `\n` for line break.
```
{"date","day","topic","sources":[urls],
 "carousel":{"caption":"...","slides":[
   {"type":"cover","stamp?":"FLAT MARKET","kicker?":"","title":"","sub?":""},
   {"type":"point","n?":"01","title":"","body?":""},
   {"type":"stat","title?":"","big":"−2.9%","color?":"mint|red|amber","label?":"","note?":""},
   {"type":"bars","title":"","bars":[{"label","value":number,"display":"~46%","highlight?","alert?"}],"note?":""},
   {"type":"list","title":"","items":[...],"marks?":"check|num|cross"},
   {"type":"table","title":"","columns":[...],"rows":[[...]],"note?":""},
   {"type":"end","title":"","sub?":""}
   ] (any slide may have "source")},
 "reel":{"caption":"...","scenes":[
   {"type":"hook","dur":3,"text":"","sub?":""},
   {"type":"stat","dur":3.5,"title?":"","big":"","color?":"","label?":""},
   {"type":"bars","dur":4.5,"title":"","bars":[...],"note?":""},
   {"type":"list","dur":4.5,"title":"","items":[...],"marks?":"num|cross"},
   {"type":"text","dur":3.5,"text":"","sub?":""},
   {"type":"end","dur":4,"text":""}]}}
```
Keep carousel titles under ~12 words, bodies under ~45 words, list items under ~14 words, max 6 list items. Reel scene text under ~10 words.

## Caption style
Line 1 = the hook restated. 2–4 short paragraphs of value. One value prompt (save/send). Sources line. Disclaimer. 3–5 hashtags from: #mutualfunds #sipinvestment #personalfinanceindia #investingforbeginners #mutualfundsindia #financialplanning #moneytips #retirementplanning #assetallocation.

## Reels-first system (from 4 Oct 2026)

Cadence: 2 reels a day, publish_at 02:45 and 13:45 UTC (08:15 and 19:15 IST), with at most one carousel a week. Each reel runs 15–18 s in 5–6 scenes. The hook is on screen in the first second and fills half the frame. The end card asks for a save or a share.

Every job records its `hook_pattern`, so the daily review can score patterns against each other:

| hook_pattern | Example | Why it should work |
|---|---|---|
| news-stakes | "Your home loan EMI could go up this Wednesday" | The top format across all three competitors |
| news-list | "4 money rules changed this October" | Timely, and people save lists |
| big-question | "How much money do you need to retire?" | Sharan's best reel (8.4M views), and it works without a face |
| ranking | "Which govt savings scheme pays the most?" | Bars get saved and shared |
| contrarian-number | "PPF pays 7.1%. Your money grows less than that." | Overturns something people assume |
| audit | "12 funds. Same stocks 5 times?" | Our own best reel so far |
| relatable (red weeks only) | A light, rule-safe take on a bad market week | A meme reel did 5–10× a competitor's usual reach |

Decision rules, applied weekly:

- A pattern whose median views are 2× the account median gets an extra slot.
- A pattern below half the median for 2 weeks is dropped.
- A reel that beats 3× the median gets a follow-up within 48 hours (part 2 or the same idea from a new angle). The owner also re-posts it by hand with a trending sound.

## Weekly decisions — 2026-10-12

These override anything above until the next weekly review (18 Oct). The daily run must follow them.

1. **Hard 15-second reel.** The 12–16 s rule from 10 Oct never reached the screen: render.py stretches each scene to fit its `vo` line + 0.55 s, so reels came out 18–20 s with 44–69 spoken words. From now: 4 scenes (hook, number, payoff, end), **at most 30 spoken words in total**, hook `vo` at most 8 words. `voice_speed` is now 1.25 in engine/config.json. After rendering, ffprobe the reel: if it is over 15.5 s, cut words and re-render before queueing. Already-queued 13 Oct reels may go out as they are.
2. **Topic mix: "your own ₹ number" first.** All three winners this week (₹2L holiday 141 views, rule of 72 122, credit-card minimum due 59) put a rupee figure from the viewer's own spending, debt or savings in the first line. The losers were duty/protection topics (life cover 9, emergency fund 14), post-event macro (repo explainer 5) and relationship money (couples 50-50, 1.3 s watch). For 13–18 Oct: at least 2 of every 3 reels are everyday-money with a ₹ figure for the viewer (spending, cards, loans/EMIs, doubling, trips, small daily spends); the am slot always gets the strongest of these. Pause insurance/emergency-fund, post-event RBI/macro and couple-money reels this week. A fresh rule change that hits the viewer's wallet this week (like UPI 15 Oct) still counts as everyday-money.

## Weekly decisions — 2026-10-18

These override anything above until the next weekly review (25 Oct). The daily run must follow them. The 12 Oct decisions stay in force (15 s / ≤30 spoken words; "your own ₹ number" topics first), except where changed here.

1. **Back to 2 reels a day: drop the mid slot (07:45 UTC) from 21 Oct.** Mid was the weakest slot every way this week: 6 reels, median 6.5 views, 7% watch (1.1 s), 48 reach in total, and the day's last-place reel on 12, 13 and 14 Oct. am (median 20 views, 12% watch) and pm (median 30 views) both beat it. Already-rendered 19 and 20 Oct mid jobs go out as queued; write no new mid jobs. Put the freed research time into the am and pm topics: each must pass the "would a friend send this to someone in that exact situation?" test.
2. **Presenter off the hook frame's centre (engine/config.json `"hook_presenter": "corner"`).** Since the 10 Oct frame-0 layout (hook text fully shown + the coin presenter 340 px, centred under it), median hold on narrated reels fell from ~3.4 s (7–10 Oct am) to ~1.4 s, at every reel length. Keep the hook text on screen at frame 0; only the presenter moves back to its normal 300 px bottom-right spot, so the text owns the frame. Applies to every reel rendered from now on (already-rendered media is not re-rendered). Judge it on 25 Oct: if median hold stays under 1.8 s, set it back to `"centre"`.
