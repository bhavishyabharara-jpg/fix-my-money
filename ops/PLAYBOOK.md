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
