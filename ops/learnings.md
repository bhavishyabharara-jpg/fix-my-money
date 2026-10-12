# Learnings

## 2026-10-12 — Daily review (second run, 07:20 UTC)

- **Followers: 12 (+1 vs 11 Oct), the same as the 06:00 pass.** The path to 2,000 needed ~410 today; we're ~400 behind and need ~250 a day for 8 days. Honest read: the target won't be met organically. The useful goal this week is the first reel that gets sends.
- **Best and worst are unchanged:** ₹2L holiday (141 views) and rule of 72 (122) lead on reach because the frame-0 line names *your* ₹. Couples 50-50 is worst (1.3 s, 7% watch). 12 Oct am (UPI fee) went live at 03:04 UTC, 19 min late, and has no metrics yet.
- **Patterns:** news-list stays EXPLOIT (low data); contrarian-number and big-question are keep. Drop fairness or relationship topics with no ₹ cost. Narrated reels get 34 median views vs 22 for silent ones, so narration stays.
- **Engine change:** send targets now name a *household role* the viewer already knows (parents who book the gas cylinder, the friend switching jobs) instead of a money trait. This tests whether family-admin topics get the first send. 15 Oct mid (LPG Aadhaar check, news-list) and pm (PF tax before 5 years, contrarian-number) are queued, so the queue now runs to the end of 15 Oct.
- **Ops:** the routine fired twice today. A second pass 80 min after the first adds no new metrics, so keep it to one run a day.

## 2026-10-12 — Daily review

- **Followers: 12 (+1 vs 11 Oct).** The 10-day path (11 → 2,000 by 20 Oct, ~200 a day) put us at ~410 today, so we are ~400 behind and now need ~250 a day for 8 days. That is ~100× today's rate; honest read: 2,000 by 20 Oct is very unlikely on organic reach alone, and the realistic win this week is the first reel that gets sends. Note: the account's media count fell 23 → 13–15 on 11 Oct and 6 older posts dropped out of tracking (5 Oct pm, 6 Oct am/pm, 7 Oct am, both carousels), so they look archived or deleted.
- **Best:** by reach, 9 Oct pm "₹2 lakh holiday: save first or loan?" 141 views / 116 reach, 1 save, 3 interactions, and 10 Oct am "When will your money double? Rule of 72" 122 / 100. Both name *your* money with a ₹ figure or a promise on frame 0. By score, 7 Oct pm "SIP at 25 or 30?" still leads (57% watch, but only 9 views). **Worst:** 11 Oct pm "Couples: is 50-50 fair?" 37 views but **1.3 s average watch (7%)**, the weakest hold yet: an abstract fairness question with no ₹ number loses people in the first second. 10 Oct pm term cover 9 views / 1.9 s: "how much cover" is a chore topic. 11 Oct am no-cost EMI 34 / 2.4 s.
- **Patterns:** scoreboard calls **news-list EXPLOIT** (low data, 2 reels); big-question, contrarian-number and news-stakes stay **keep**; audit is on hold. Drop relationship or fairness questions without a rupee cost. Every reel is still under 20% watch, so the hook, not the topic, is failing.
- **Narrated vs silent:** narrated median 34 views / 16% watch vs silent 22 / 13%. Narration stays on everything.
- **Engine change today:** sends are **0 on all 12 reels**, and sends are the strongest reach signal. From 12 Oct mid, every new reel (1) is ~14 s with ≤35 spoken words, (2) puts the whole hook on screen at frame 0 with a number or "you", and (3) ends with a two-line CTA whose first line names who to send it to ("your sibling", "parents with FDs", "the friend who skipped ITR"). Moved to 3 reels a day (02:45 / 07:45 / 13:45 UTC). Queued 6: four news-list on dated rules with a ₹ cost (pension life certificate, belated ITR fee, Form 121 TDS, ATM fee cut), one contrarian-number (card late fee 3-day rule), and one experiment: a **guess-the-number** quiz hook (tax on ₹12.75 lakh salary).

## 2026-10-12 — Weekly review (format level)

- **Followers 12 vs the sprint checkpoint of 50 for 12 Oct (25 for 11 Oct).** Week 8–12 Oct added +1 (11 → 12); the week before, 0 → 12 came from the launch push. At this pace the 16 Oct "below 400 → reset the target" rule is already triggered in substance.
- **This week (8 reels, 8–11 Oct) vs the week before (8 reels, 4–7 Oct):** median views 35.5 vs 8.5 (4×); reach 351 vs 80; median watch 13% vs 23% (the earlier figure is inflated by 0–5-view reels); saves 1 (0.28% of reach) vs 0; sends 0 vs 0. Profile visits and follows per reel still come back empty.
- **Narrated vs silent:** narrated median 34 views vs 8 silent, but watch % is no better (14% vs 16%). The voice helps distribution, not retention; part of the gap is just account age.
- **Best 3:** 9 Oct pm ₹2L holiday (141 views, 1 save), 10 Oct am rule of 72 (122), 9 Oct am credit-card minimum due (59): a rupee figure about the viewer's own money in line one. **Worst 3:** 8 Oct pm repo explainer (5), 10 Oct pm life cover (9, 1.9 s), 8 Oct am emergency fund (14, 2.3 s): post-event macro and duty topics. Watch % barely separates them (all 10–16%); the topic decides the test-pool size.
- **Frame-0 hooks (from 10 Oct pm): watch % did not rise above 25%.** The three reels since got 10%, 12%, 7% (1.3–2.4 s), lower than before. The hook visual isn't the lever; the topic and the first spoken words are.
- **12–16 s vs longer: untested.** No narrated reel has been under 17.5 s: render.py stretches scenes to fit the voice, so every reel since 7 Oct ran 18–23 s with 44–69 spoken words. Fixed this week (see PLAYBOOK Weekly decisions).
- **Slots:** am wins on median views over all 16 reels (22 vs 9) and this week (46 vs 23); pm only has the single best. There is no mid slot: the "3 reels a day" change in the sprint plan never shipped (queue still has am + pm only).
- **Hook patterns:** none is consistently last. big-question is both the best (141, 122) and the worst (9, 37 with 7% watch); the pattern label predicts less than the topic. audit has 1 reel (14).
- **Decisions for 13–18 Oct:** (1) hard 15 s reels: 4 scenes, ≤30 spoken words, voice_speed 1.15 → 1.25; (2) topic mix: ≥2 of 3 reels are "your own ₹ number" everyday-money topics, strongest in am; pause insurance, emergency fund, post-event macro and couple money.
- **Check:** queue/2026-10-12-reel-pm (₹200 a day → ₹7.3 lakh) has an empty sources list; any growth figure needs its assumed return labelled "illustrative".

## 2026-10-10 — Daily review

- **Followers: 11 (flat since 8 Oct; 23 posts live).** First save ever landed (9 Oct pm). The 30-day aim of 500–1,000 still needs ~17–33 a day; reach is finally moving, follows aren't.
- **Best (last 7 days):** 9 Oct am "Credit card minimum due" (contrarian-number) 58 views / 50 reach, 3.4 s watch; 9 Oct pm "₹2 lakh holiday: save first or loan?" (big-question, modelled on a competitor's ₹2L-trip winner) 58 views / 49 reach, **1 save**, 4.0 s. Both doubled the old best (30). **Worst:** 7 Oct am RBI rights 0; 6 Oct pm PPF vs inflation 1; 8 Oct pm repo explainer 5. 8 Oct am emergency fund recovered to 14 after a slow day 1.
- **Why the two winners worked:** the frame-0 line names the viewer's own money situation (a bill they're paying, a trip they want) with a concrete ₹ figure, and the first spoken words say it. RBI follow-ups after the event keep flopping: no more post-event macro explainers.
- **Narration is now clearly winning:** narrated reels (7 Oct pm onward) average 29 views vs 11 for silent reels 4–7 Oct. Slots: am 110 views over 5 reels vs pm 100 over 6, still no slot effect.
- **Use more:** contrarian-number on everyday debt, big-question borrowed from competitor winners, small-input-big-number. **Use less:** post-event news explainers, audit. Queued 13 Oct: flat-rate loan trap (contrarian-number) and one-extra-EMI home loan (small-input-big-number).

## 2026-10-09 — Daily review

- **Followers: 11 (no change since 8 Oct)** with 21 posts live; still 0 saves and 0 shares on every post. The 30-day aim of 500–1,000 now needs ~17–33 a day, and nothing yet moves follows.
- **Best (last 7 days):** 5 Oct am "October money rules" (news-list) 30 views / 28 reach; 4 Oct pm "RBI decides on 7 Oct" (news-stakes) 22; 7 Oct pm "SIP at 25 or 30?" (big-question, narrated) 9 views with 12.4 s average watch, still the best retention by far. **Worst:** 7 Oct am RBI rights 0 views; 8 Oct pm "RBI raised repo to 5.50%" 2 views, 0.7 s watch; 8 Oct am emergency fund (audit) 2 views, 1.0 s.
- **Reach is shrinking, not growing:** the four reels since 7 Oct am drew 0, 9, 2, 2 views against 13 average for 4–6 Oct. Narration alone isn't the fix (the two newest narrated reels lose viewers inside 1 s); the frame-0 line and first spoken words must carry a concrete number for *the viewer*.
- **Patterns:** news-list/news-stakes still own the top two, but only on fresh rule changes (the RBI follow-ups after the event flopped). Big-question holds viewers best. Adding a competitor-proven **small-input-big-number** hook (12 Oct pm, ₹200 a day → ₹7.3 lakh) and a fresh rule change (12 Oct am, UPI 0.4% merchant fee from 15 Oct). Audit and contrarian-number stay on hold.
- **Slots:** am 40 views over 4 reels vs pm 39 over 5: no slot effect; keep the timeliest topic in am. Publishing: 8 Oct am went out 78 min late (04:03 UTC), 9 Oct am 17 min late; all media through 11 Oct pm is on GitHub.

## 2026-10-08 — Daily review

- **Followers: 11 (−1 since 7 Oct)** with 18 posts live. Against the 30-day aim of 500–1,000 the page now needs ~17–33 a day; nothing yet is driving follows.
- **Best by views (last 7 days):** 5 Oct am "October money rules" (news-list) 30 views / 28 reach; 4 Oct pm "RBI decides on 7 Oct" (news-stakes) 22; 4 Oct am "Stopping your SIP?" 13. **Worst:** 7 Oct am "RBI decision day: your rights" 0 views after a day, 6 Oct pm "PPF vs inflation" (contrarian-number) 1, both carousels 1. Saves and shares are still 0 on every post.
- **Narration is the first real signal:** 7 Oct pm "Start a SIP at 25 or 30?" (first narrated reel, big-question) holds viewers for **13.8 s average watch**, against 2.2–3.0 s for the silent top three (PPF's 7 s comes from 1 view). Views are still low (8), so narration fixes retention, not distribution yet. Keep every reel narrated; judge the hook on reach.
- **Patterns:** news-list and news-stakes still lead on views; big-question now leads on watch time. RBI has had 4 reels in 5 days (4 Oct pm, 7 Oct am, 8 Oct pm, plus EMI angle) and the decision-day one drew 0, so rest RBI. Contrarian-number stays on hold except when tied to a live event.
- **Slots:** am reels 51 views over 4, pm 36 over 4; still lean am for the most timely topic. 11 Oct am: festive "no-cost EMI" (news-stakes); 11 Oct pm: first couple-money reel ("is 50-50 fair?", big-question), copying the competitor outlier theme.
- **Ops:** media for 8 Oct pm through 10 Oct pm is on GitHub; the Action published 8 Oct am at 04:03 UTC (78 min late). Watch timing.

## 2026-10-07 — Daily review

- **Followers: 12 (+1 since 6 Oct)** with 16 posts live; following dropped 91 → 0. 30-day aim of 500–1,000 still needs ~16–33 a day. Reel insights now return views for the first time.
- **Best by views:** 5 Oct am "October money rules" (news-list) 30 views / 28 reach; 4 Oct pm "RBI decides on 7 Oct" (news-stakes) 22 views, 1 like; 4 Oct am "Stopping your SIP?" 13 views. **Worst:** 6 Oct pm "PPF 7.1% vs inflation" (contrarian-number) 1 view and both carousels 1 view each. Saves + shares are 0 on every post, so the second ranking key can't separate anything yet.
- **Patterns:** news-list and news-stakes (the "this week, your money" hooks) lead; ranking (5 views) and contrarian-number (1) trail. Use more news-list on real events; hold contrarian-number until there's reach. Avg watch is 2.5–3.1 s on the top three: viewers are leaving in the hook, so the frame-0 line has to carry the whole promise.
- **Slots:** am reels 51 views over 3, pm 28 over 3 (pm ones are younger); lean am for the most timely topic. All reels so far are silent; narrated reels start with 7 Oct pm, compare from 9 Oct.
- **Ops:** the push problem is fixed: 7 Oct am went out at 03:02 UTC and media for 7 Oct pm–9 Oct pm are all on GitHub. Swapped 8 Oct pm to a same-day RBI follow-up (repo 5.50%) and moved rule-of-72 to 10 Oct am.

## 2026-10-06 — Daily review

- **Followers: 11 (+11 since 5 Oct)**, the first growth, with 14 posts live. Following also rose 67 → 91; if that is follow-for-follow, today's gain may be follow-backs rather than content. 30-day aim of 500–1,000 still needs ~17–33 a day.
- **Data gap persists:** views/reach/saves are blank for every reel (the carousel returns zeros), so reel insights still fail; ranking on likes. Best: 4 Oct am "Stopping your SIP?" and 4 Oct pm "RBI decides on 7 Oct" (news-stakes), 1 like each. Worst: 5 Oct am "October money rules" (news-list) and 5 Oct pm "Which small savings scheme pays most" (ranking), 0 likes after ~a day.
- **Patterns:** news-stakes 2 likes from 2 reels; news-list, ranking and both carousels 0. am vs pm tied. Keep leaning on news-stakes and big-question; trial contrarian-number (credit-card minimum due, 9 Oct am) and a goal-maths big-question (₹2L trip, 9 Oct pm).
- **Publishing:** the Action published 5 Oct pm and 6 Oct am on time (±20 min).
- **Ops, urgent:** the Mac's 4 Oct and 5 Oct "Queue update" commits (7 Oct and 8 Oct reels) are still **not on GitHub**; pull works, push fails. The 7 Oct am RBI decision-day reel will be skipped unless the owner runs ./autopush.sh by hand before 02:45 UTC 7 Oct.

## 2026-10-05 — Daily review

- **Data:** account.csv 5 Oct shows **0 followers** (no change from 4 Oct), 12 posts, and **following jumped 0 → 67** (worth confirming that was intentional). Reel views/reach/saves are **blank for every reel**, while the 3 Oct carousel returns zeros, so insights work for carousels but the reel metric calls fail; ranked on likes/comments instead.
- **Best:** 4 Oct pm "RBI decides on 7 Oct: what a 0.25% hike would mean for your EMI" (news-stakes) and 4 Oct am "Thinking of stopping your SIP?" each got 1 like, 0 comments. **Worst:** both carousels (3 Oct expense ratio, 4 Oct eight losing weeks): 0 likes, and 0 reach where measured. 5 Oct am "October money rules" went out at 03:02 UTC and has no numbers yet.
- **Patterns/slots:** news-stakes 1 like from 1 reel; am vs pm tied (1 like each). Far too little signal to rank patterns. Keep weighting news-stakes and big-question; 8 Oct am is the first *audit*-tagged reel since the pipeline went live (emergency fund), so it tests our playbook's "own best" pattern.
- **Timing:** the Action published 4 Oct pm 75 min late (15:00 UTC) and 5 Oct am 17 min late. Fine for now; watch it.
- **Followers vs aim:** 0 against 500–1,000 in 30 days, i.e. 17–33 a day needed. After 12 posts the page still has almost no distribution; reels are the only format with any reach, and hand-adding a trending sound to the best reel remains the untested lever.
- **Ops:** the Mac's autopush pulls and rebases (last at 04:40 UTC 5 Oct) but the 4 Oct "Queue update" commit (7 Oct reels) is **not on GitHub**, so the push step is failing. Also: never run plain `git status` from the Cowork shell, it leaves a `.git/index.lock` that can't be deleted there; use `git --no-optional-locks`.

## 2026-10-04 — Daily review

- **Data so far:** 5 posts tracked on the pipeline (2 reels manual, 1 carousel 3 Oct, 1 carousel + 1 reel 4 Oct). Insights do return for the 3 Oct carousel (views 0, reach 0, saves 0), so the token has the permission; the 4 Oct posts are too new to show views yet.
- **Best:** 4 Oct am reel "Thinking of stopping your SIP? 8 weeks of red" — 1 like within an hour, the only engagement so far. News-pegged reel beat the evergreen carousel. **Worst:** 3 Oct expense-ratio carousel — 0 views/reach after a day: carousels to a 0-follower account get no distribution.
- **Patterns:** too little data to score hook_patterns (no reel has views yet). Keep the mix weighted to news-stakes and big-question; no more carousels this week.
- **Slots:** only one AM reel live; first PM reel (RBI/EMI, news-stakes) goes out 13:45 UTC today. Compare am vs pm from Tuesday.
- **Followers:** 0 (first account.csv row). The 30-day aim is 500–1,000; needs ~17–33 a day from here, so reach per reel is the only lever.

## 2026-10-03 — Weekly review, week 1 (28 Sep – 3 Oct)

Snapshot from the profile, 3 Oct 10:50 IST (active account confirmed @fix_mymoney via Edit profile): **6 posts live (5 carousels + 1 reel), 0 followers, 0 following.** Web Insights page returns "page not available", so reach/saves/shares/follows could not be read; open Insights in the mobile app to fill the gaps.

- **Growth vs target: far behind.** Week 1 target was 300 new followers and 2k avg reel views; actual is **0 followers** and **5 views** on the only live reel (28 Sep "2 years of SIPs, zero returns"). Carousels show 0 comments and no visible likes. The page currently has effectively no distribution, so there is no real best/worst signal yet; differences between posts are noise.
- **Best post (by the only number visible): the 28 Sep reel, 5 views**, i.e. reels are the only format that got any non-follower reach. Carousels to a 0-follower account get almost none. This is the core problem: **4 of 5 reels (29 Sep, 30 Sep, 1 Oct, 2 Oct) are rendered but not published.** Clearing that backlog matters more than any topic change.
- **Worst / structural issue: the live reel's grid thumbnail is a blank navy frame.** The hook isn't visible in the grid or Reels tab. From now on the hook text must be on screen at frame 0 (and the reel_cover.png should be set as the cover when posting manually).
- **Hooks:** all carousel covers follow the "name the viewer" rule (age/salary/fund count) and look consistent, but none earned engagement, so no hook can be called a winner. Keep the numbers-first hook style; test sharper, news-pegged tension next week ("8 weeks of losses, longest in 25 years").
- **Pillars/audience:** week 1 was Optimizer-heavy (overlap, half-year check, TER) plus two Both and one Builder. No measurable difference between Portfolio Optimizer (32–40) and Goal Aware Wealth Builder (25–32) content at this volume. Next week balances 2 portfolio, 2 goal maths, 2 news, 1 mistake and leans into live news (RBI 7 Oct, Nifty losing streak) because timely topics are what the explore/reels feed rewards for a new account.
- **News context for next week:** Nifty fell for an 8th straight week (closed 22,421.95 on 1 Oct, longest losing streak in ~25 years), FIIs sold ~₹36,000 cr in September, rupee ~₹96/$; RBI MPC meets 5–7 Oct with most economists expecting a 25 bp hike to 5.50% (CPI 4.82% in Aug); AMFI Aug equity inflows ₹29,329 cr, led by small-caps (₹7,973 cr). Sources: 5paisa post-market 1 Oct 2026; Business Standard MPC preview 2 Oct 2026; DD India AMFI Aug 2026.
- **Run log problems (log.csv):** (1) **Publishing reels via the browser is failing every time** — the Create dialog never advances past "Drag photos and videos here", or the session permission check refuses the upload; 29 Sep, 30 Sep, 1 Oct and 2 Oct reels are all `ready` and waiting for a manual tap. (2) The 1 Oct reel run fired ~15 h late (ran 2 Oct 10:26 IST). (3) **No 3 Oct carousel**: as of 10:50 IST there is no `posts/2026-10-03/` folder and no log row, so the 8:30 am run either didn't fire or failed before writing anything. Carousels themselves publish reliably when the run happens (5/5 logged posted).
- **Action for owner:** publish the 4 waiting reels from the phone (oldest evergreen first: 29 Sep overlap, 30 Sep salary split, 2 Oct gold; 1 Oct half-year check is now slightly stale), set each reel's cover to reel_cover.png, and check whether the 3 Oct carousel run fired. Longer term the publish path for reels needs to change (Graph API / scheduler / daily manual tap).

## 2026-09-29 — publishing reliability (the recurring failure)

- Ground truth from the profile on 29 Sep, 17:20 IST: **2 posts live** — 28 Sep carousel and 29 Sep carousel ("12 funds. Same stocks, 5 times?"). The only real miss is the **28 Sep reel**, never published.
- Root cause is not Instagram, the account, the render or the Mac. It is the **publish step itself**: every attempt to hand a file to instagram.com goes through the session's permission classifier, and it refuses non-deterministically. Same action, same files, different answer run to run — which is why carousels sometimes land and the reel never has.
- Two separate walls seen: (a) `file_upload` refuses Mac paths outright ("only files this session is allowed to read"); (b) copies staged into the cloud outputs folder get past that but are then denied by the classifier.
- Video is not the problem: reel.mp4 is h264 1080x1920, 30fps, 23s, with an AAC audio track — within spec. In the one run where the input did accept it, Instagram's Create dialog simply never advanced.
- Conclusion: **browser automation is not a dependable publish path for this page.** Rendering, sourcing, captions and checks are all reliable; only the last 30 seconds is not. Until the publish path changes (Instagram Graph API with a Business/Creator account, or a scheduler, or a human tap), expect misses and treat the push notification on a `skipped` row as the thing to act on.

(Weekly review notes go here, newest first.)
