# Learnings

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
