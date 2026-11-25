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

## Weekly decisions — 2026-10-25

These override anything above until the next weekly review (1 Nov). The daily run must follow them. The 12 Oct and 18 Oct decisions stay in force (2 reels a day, no mid; "your own ₹ number" topics; presenter `"corner"`), except where changed here. The 18 Oct presenter check passed: median hold this week was 2.0 s (corner-rendered reels 21–24 Oct: 1.9 s, median 45 views), above the 1.8 s revert line, so `"hook_presenter": "corner"` stays.

1. **Hard 12-second reel (was 15 s).** Viewers leave at the same ~1.7–2.0 s whatever the length, so a shorter reel only raises watch %, the one signal we can still move. The three reels under 13 s since 10 Oct (21 Oct pm gold exchange 11.1 s, 21 Oct am Diwali bonus 11.9 s, 22 Oct am card fraud 12.2 s) have median 70 views and 15% watch; the 13–16 s reels have median 17–24 views and 11–12%. From the next job written: 4 scenes (hook, number, payoff, end), **at most 22 spoken words in total**, hook `vo` at most 6 words, list scenes at most 2 items. After rendering, ffprobe the reel: over 12.5 s → cut words and re-render before queueing. Jobs already in the queue (to 28 Oct) go out as rendered. Judge on 1 Nov: if the ≤12.5 s reels' median watch % is not above 15%, go back to 15 s.
2. **Topic mix: both slots carry a money event the viewer is in this month; no rules, rights or warnings.** Every reel above 60 views this week was a ₹ answer to a decision the viewer is making now (EPF payslip 112, gratuity on a job switch 110, gold exchange 109, Diwali bonus 70). The bottom five were rules or warnings for a situation the viewer isn't in (recovery-agent calls 4, deepfake ads 7, Section 45 claims 10, card fraud 15, card cash withdrawal 16). Until Diwali (8 Nov) the am slot takes a festive money event (gold, bonus, gifts, sales, travel) and the pm slot stays the payslip slot (salary, job switch, PF, tax). Not allowed: legal rights, defaulter problems, fraud / scam warnings, chores (KYC, certificates), unless the hook names a ₹ the viewer gains or loses this month. Pattern choice still follows the scoreboard (contrarian-number EXPLOIT ~60%, a 'keep' ~25%, a test ~15%).

## Weekly decisions — 2026-11-01

These override anything above until the next weekly review (8 Nov). The daily run must follow them. The 12, 18 and 25 Oct decisions stay in force (2 reels a day, no mid; presenter `"corner"`; "your own ₹ number" topics; no rights, warnings or chores), except where changed here. The 25 Oct 12 s check passed: reels at or under 12.5 s (29–31 Oct) held a median 22% (above the 15% line) and the week's median hold rose to 24% / 3.35 s from 13% / 2.0 s, so the **hard 12 s / ≤22 spoken words rule stays**.

1. **Both slots open on one ₹ bill the viewer is paying this month; the payslip-only pm slot ends.** This week's spend-led reels reached 110–129 views (dinner bill 129, no-cost EMI 125, minimum due 121, gold bill 117, home loan 110); the payslip/insurance-mechanics reels reached 5–21 (motor insurance 8, job-switch tax 11, employer NPS 5, CTC 13, leave encashment 21) with holds of 17–56%. pm median views fell to 13 vs am 52. From the next job written, every hook's first line names a single purchase, bill, loan or booking the viewer is making now (festive shopping, gold, travel, a car, cards, EMIs, rent), and any salary or tax rule appears only as the payoff (the 31 Oct LTA-trip shape). Until Diwali (8 Nov) both slots may be festive. Already-rendered jobs (to 3 Nov) go out as queued. Judge on 8 Nov: pm median views should be at or above am's.
2. **Judge a reel on its day-3 numbers, not day 1.** Reach arrives 1–2 days late (27 Oct pm went 25 → 110 views). The daily run must not call a reel a loser, re-cut it or change a pattern call on a reel less than 48 h old; it reports day-1 holds only as an early read.

## Weekly decisions — 2026-11-08

These override anything above until the next weekly review (15 Nov). The daily run must follow them. The 12, 18, 25 Oct and 1 Nov decisions stay in force (2 reels a day, no mid; presenter `"corner"`; hard 12 s / ≤22 spoken words; hooks open on one ₹ bill the viewer is paying now; no verdicts under 48 h), except where changed here. The 1 Nov pm check passed: pm median views 132.5 vs am 117 (1–4 Nov), so the bill-led pm slot stays. Jobs already written (to 9 Nov) go out as rendered; these apply from the 10 Nov jobs.

1. **Post-Diwali topic mix (from 10 Nov; the festive window closed 8 Nov).** am slot: the after-Diwali bill the viewer is now holding (credit-card statement, no-cost EMI, BNPL, gold loan, festive personal loan) until 20 Nov, then wedding-season money (gifts, shagun, jewellery, travel). pm slot: an everyday ₹ bill, except **every other day the pm reel is an investing ₹ number** (SIP, FD, RD, a down-market day) in the red-day-relatable or contrarian-number shape. Reason: 4 Nov pm red-day SIP reached 126 views at 33% watch, level with the bill-reveal median and the first investing reel to reach since 10 Oct; one test isn't a pattern, so it gets 3–4 more this week, not a slot. Still not allowed: rights, warnings, chores, acronym hooks (except GST, EMI, PF).
2. **Spoken end line: am reels ask for the follow, pm reels keep the send ask.** 69 reels have spoken a send ask and earned 0 sends and 0 follows on ~3,500 reach. On am reels, the end scene's `vo` becomes a follow ask of ≤6 words (e.g. "रोज़ एक bill decode — follow करो।") and the first `cta` line becomes "Follow for a money fix every day"; the send line moves to the caption. pm reels are unchanged. Judge on 15 Nov (day-3 numbers only): profile visits and follows per reach on am vs pm reels. If am beats pm, all reels speak the follow ask; if both are 0, revert.

## Weekly decisions — 2026-11-15

These override anything above until the next weekly review (22 Nov). The daily run must follow them. The 12, 18, 25 Oct, 1 Nov and 8 Nov decisions stay in force (2 reels a day, no mid; presenter `"corner"`; voice `sarvam:amit`; hooks open on one ₹ the viewer pays; no verdicts under 48 h; am topic mix to 20 Nov then wedding money), except where changed here. The 8 Nov follow-ask test is closed: am (follow ask) and pm (send ask) both earned 0 follows and 0 profile visits, so it reverts; every reel speaks the send ask (already the case from the 17 Nov jobs). Jobs already rendered to 17 Nov go out as they are, except rule 2.

1. **pm slot = an investing ₹ number every day (from the 18 Nov jobs), not every other day.** This week the three investing pm reels (10 Nov SIP step-up 124 views / 39%, 12 Nov FD after tax 170 / 34%, 14 Nov fee drag 147 / 46%) beat the three everyday-bill pm reels (9 Nov clubbing 113 / 29%, 11 Nov NCB 28 / 20%, 13 Nov FASTag 121 / 38%), and 2 of the week's 3 saves came from them. Shape: contrarian-number or red-day-relatable; SIP, FD, RD, expense ratio, tax on returns, a down-market day; one illustrative ₹ result the viewer can compare, "returns not guaranteed" where relevant. The am slot keeps the bill the viewer is paying now (after-Diwali bills to 20 Nov, then wedding money); group-callout (scoreboard EXPLOIT) can carry either slot. Judge on 22 Nov: pm median views and saves per reach vs am.
2. **Hard 12 s cap restored, with the send ask inside it.** The 17 Nov jobs went to 35 spoken words and 13.4 s / 12.4 s when the send ask was added. Since 10 Oct, reels ≤12.6 s: 26 reels, median 121 views / 30% watch; 12.6–16.5 s: 36 reels, 20.5 views / 13%; >16.5 s: 9 reels, 37 / 9%. Rule: ≤24 spoken words in total including the send ask (end `vo` ≤6 words), `duration_s` ≤12.0; if a render comes out above 12.4 s, cut a stat scene's `vo`, never the hook. Before 17 Nov am publishes, the daily run re-renders it under this cap (it is 13.4 s today); 17 Nov pm (12.4 s) may go as is.

## Weekly decisions — 2026-11-22

These override anything above until the next weekly review (29 Nov). The daily run must follow them. The 12, 18, 25 Oct, 1, 8 and 15 Nov decisions stay in force (2 reels a day, no mid; presenter `"corner"`; voice `sarvam:amit`; hard 12 s cap with the send ask inside it, ≤24 spoken words; hooks put a ₹ on the viewer's choice; no verdicts under 48 h; pm = investing ₹ number every day), except where changed here. The 15 Nov pm-investing check passed (16–21 Nov: pm 128.5 median views / 29.5% / 3 saves on 637 reach vs am 109.5 / 27% / 0 saves on 548). Jobs already rendered (to 24 Nov) go out as they are; these apply from the 25 Nov jobs.

1. **contrarian-number is the exploit pattern; the am slot carries an investing or tax ₹ number on alternate days (25, 27, 29 Nov).** Since 9 Nov the am bill-reveal / group-callout was the day's lowest-view reel on 8 of 13 days; contrarian-number leads (7 reels, median 145 views / 34%) over bill-reveal (121 / 31.5%) and group-callout (113.5 / 28.5%; this week's am callouts 105 / 26%). On 26 and 28 Nov the am reel stays wedding-season money, but only a decision the viewer hasn't made yet (what to gift, how to fund it, when to buy gold), never a callout to someone past it (late ITR, a loan already taken: 68–70 views). Pattern split: ~60% contrarian-number, ~25% bill-reveal / group-callout / future-bill, ~15% a test. This overrides the scoreboard's all-time EXPLOIT label for this week. Judge on 29 Nov (day-3 numbers): am investing reels vs am wedding reels on median views, watch % and saves per reach.
2. **Numbered series tag for follows (on screen only, no spoken words).** Every reel gets a small top-left tag on the hook frame, "₹ Fix #N" (N counts up from #1 on 25 Nov am, one number per reel, am then pm), and the end card's second line becomes "Fix #N+1 tomorrow · follow" (the send line stays first and spoken). Reason: 0 follows on ~5,400 reach; the spoken follow ask (8–15 Nov) didn't convert, and a running series gives a reason to follow that a one-off reel lacks. The tag must not cover the hook text or the ₹ number, and must not push the hook past 2 lines; check it in the frame check. Judge on 29 Nov: any profile visit or follow on a tagged reel; if both stay 0, drop the tag at the 29 Nov review.

## Owner reset — 2026-11-22 (supersedes the 22 Nov weekly decision 1 and the "2 reels a day" line)

Set by the owner after reviewing (a) the Silly Money newsletter post "How I used AI to get 25 million views in 7 weeks" and (b) @simply.kaasu, a Tamil finance page about a month old with reels at 241K, 238K, 67.8K and 30.5K views. These rules stay in force until the owner changes them; weekly reviews may tune details but not drop them. The 22 Nov weekly decision 2 (numbered "₹ Fix #N" series tag) stays in force.

**Correction to earlier reviews:** per-reel `follows` and `profile_visits` have never been measured. The API leaves them blank for reels, so "0 profile visits" in earlier entries means "unknown", not zero. From 23 Nov, `tools/metrics.py` writes account-level `profile_views`, `follows_and_unfollows`, `accounts_engaged` and `reach` daily to `metrics/account_insights.csv`; judge follow-conversion from that file and the daily follower count.

1. **One reel a day (2-week test, 23 Nov – 6 Dec), at 13:45 UTC (19:15 IST).** Evidence: reels on 1-post days median 114 views, 2-post days 46, 3-post days 26 (confounded with account age, so it is a test, not proof); the write-up saw the same fatigue on every network. The am jobs already queued for 23–25 Nov are moved to `held/` for reuse; their pm partners go out as planned. Queue keeps 3 days ahead = 3 jobs, never more than 1 job per date.

2. **Judge every reel as a multiple of a frozen yardstick: 122 views** (median of reels posted 1–15 Nov), read once at 3 days old, never updated after. 3×+ = hit (study why), 2×+ = win (repeat), 0.5–2× = normal, under 0.5× = miss (usually the first line). Never compare against this week's median: a falling median makes every week look normal. `tools/review.py` now prints this in `metrics/scoreboard.md`.

3. **Winners are ideas, not wordings.** Every queue job carries an `idea` slug (short, reusable: "sip-delay-cost", "fd-after-tax"). `metrics/ideas.md` lists proven ideas (2× twice or 3× once). A proven idea rests ≥30 days, then is re-run with the hook almost word for word and every number updated; at most one re-run a day; never "freshen it up" by adding a second idea.

4. **Cold start: borrow proof from other accounts.** We have no proven idea yet (best reel 237 views = 1.9×). Until we do, at least every other reel adapts an idea that is an outlier on a comparable account: ≥3× that account's own typical reel among its last 12. Check @simply.kaasu, @financewithsharan, @ca_rachanaranade, @anushkarathod98 and one rotating creator. Adapt the idea (topic + angle + the question it answers), never copy wording, visuals or audio; re-research every number. Log the source account and its multiple in the job's `experiment` note.

5. **Patterns are hints, not rules.** The scoreboard labels the leading pattern "leading", not EXPLOIT. At least 1 new reel in 3 deliberately goes against the leading pattern. No reel opens the same way (same first words / same hook shape) as either of the two before it. This replaces the 60/25/15 split.

6. **What @simply.kaasu does that we adopt now:**
   - **Mass, evergreen, "save this" explainers** over niche bill callouts: their hits are SWP explained (241K), WhatsApp formatting tricks (238K, not even finance), 5 post office schemes with rates (67.8K), car loan in wife's name (30.5K). Prefer topics a parent, sibling or colleague would ask about (post office / small-savings schemes, SWP, FD vs RD, PF withdrawal, UPI and banking how-tos, gold buying rules, loan tricks), with one concrete ₹ example.
   - **Searchable title line as caption line 1:** "Question in plain words? | Topic Explained" (e.g. "Can one investment pay you every month? | SWP Explained"), then the explanation, then a keyword line in brackets [SWP, Systematic Withdrawal Plan, Mutual Fund Tips Hindi, Fix My Money] before the hashtags.
   - **Proof on screen:** the lower part of key scenes shows the actual table, rate list or calculator-style result (our own render, no brand names or third-party screenshots), so the number is seen, not just said.
   - **Save + send close:** "Save this for later" plus a send line naming who needs it.
   - Not adopted (owner decision pending): a "comment <KEYWORD>" ask (their SWP reel drew 393 comments with it; our compliance rules forbid comment keywords), and a human presenter (see 8).

7. **Critic pass before queuing.** After writing each spec, re-read it as a critic against this playbook and `metrics/ideas.md`: is the idea proven here or elsewhere, is the hook ≤9 words with a ₹ or "you", does it open differently from the last two reels, is every number sourced? Fix or replace a reel that fails. Record the critic's predicted multiple in `experiment`; it's for catching weak reels, not forecasting hits.

8. **Presenter (owner decision, 25 Nov).** The realistic AI human presenter is live from the 26 Nov reel: InfiniteTalk (open source) on Modal, the v2 test clip the owner approved. The daily run changes nothing: keep writing specs with the usual scenes and `vo` lines; tools/build.py renders the coin reel as before plus a presenter-free base, and avatar.yml (tools/avatar_batch.py, hourly) swaps the human in as a rounded facecam card with an "AI" tag, in the coin's spots. Captions keep the line "Voiceover is AI-generated." — the batch step rewrites it to "Presenter and voiceover are AI-generated." once the presenter is in; never remove it. The presenter never claims credentials, a real person's name, or personal experiences. Cost rule: ₹0 — Modal runs only on its free $30/month credit (spend limit $0, usage cap $29); when the cap is reached, reels go out with the coin until the 1st. Turn the human off with engine/config.json "presenter_mode": "sikka". Turn Instagram's "AI info" label on when posting manually; the API path relies on the caption disclosure and the on-screen tag.
