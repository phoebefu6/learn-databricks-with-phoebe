# Course-lead brief (shared by the three ds builds, 2026-09-29)

You are the course lead for ONE learn-*-with-phoebe course. You build the WHOLE course locally, end
to end, through both gates. You do NOT git init, commit, push, create a repo, or touch the hub
(`learn-with-phoebe/`). The main thread publishes after re-verifying your work.

## The skill you are executing

Read `/Users/phoebe.fu/.claude/skills/course-builder/SKILL.md` first (Phases 2-5 and the Iron
rules are binding; Phase 1 grill is DONE and the skeleton below is Phoebe-approved - do not re-scope).
Then read, as each phase needs it, from `/Users/phoebe.fu/.claude/skills/course-builder/references/`:
page-template.md, agent-brief.template.md, diagram-kit.md, simulator-patterns.md, retheme-recipe.md,
mindmap-layer.md, verification.md, estate-checks.md. Grep (never read whole) field-notes-archive.md
for keywords you hit.

## Fixed decisions (Phoebe-approved)

- Bucket `ds`, single-track 6 sessions, 45 min each, public course (published later by main thread).
- Donor: `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-rfm-modeling-with-phoebe`
  (single-track 6, hand-drawn SVG grammar, real-rows bench). Copy its assets/ structure, page
  anatomy, quiz markup (same option count), crumb/title formats, landing layout + knowledge map.
  Replace its data/engine files (rfm-live.js, rfm-sample.js) with your course's own.
- File names `courses/01-<slug>.html` ... `06-<slug>.html`; session 4 is the bench page.
- Hand-drawn SVG grammar (default grammar in agent-brief.template.md) on every figure; every major
  concept draws the MECHANISM. Light surfaces only (Phoebe: never dark backgrounds on new surfaces
  you add; the donor's existing code-box style may stay as the donor has it).
- Bench: computed for real in the browser from REAL public rows, shipped as a compact seeded sample
  (json.dumps-generated JS, integer/quantised arrays where possible, target < 300 KB). A Python
  reference script in `materials/` must produce the same numbers as the node/browser engine to the
  stated precision before ANY page quotes a number. The bench must be able to report a WORSE
  number (include the anti-lever or a break button). Label anything modelled, on the widget.
- Retheme per retheme-recipe.md to the palette given below; build the full ramp yourself (deep,
  primary, mid, soft, 50-tint, ink, muted, faint, hairline, one warm contrast); check every
  text-on-fill pair for WCAG AA 4.5:1 BEFORE authoring pages. Grep `rgba(` in style.css and hex in
  index.html after the swap; no donor colour may survive.
- Run `python3 ~/.claude/skills/course-builder/scripts/pre-publish.py <repo> --fix-journey` right
  after scaffolding; give the course its own PASSPORT_KEY; TOTAL_SESSIONS = 6.
- Do not generate og-cover.png (main thread does it after hub registration); delete the donor's
  copy so no identity leaks, and note that in your report.

## Build order

1. Phase 2: fetch the REAL primary sources (WebFetch/WebSearch). Write
   `materials/official-course-map.md` FIRST: per-session coverage, verified facts with evidence
   tiers (read-at-source vs reported), the seams below, an honest "not covered" list, citation
   appendix. Never invent a statistic; a fact you could not read at source is "reported" or cut.
   Before correcting any famous claim, grep `github_repo/learn-*/courses/` for it.
2. Build the data sample + engine + Python reference; run the WHOLE ladder in node and record canon
   numbers in the course map.
3. Hand-author session 1, the session-4 bench page and index.html (knowledge map below cards). Run
   both gates on them and pass before writing sessions 2, 3, 5, 6.
4. Sessions 2, 3, 5, 6: fill agent-brief.template.md into `materials/agent-brief.md` and, if you
   have the Agent tool, fan out per subagent-spec.md (max 3 in flight, each gets the brief path +
   its one-file outline). If you have no Agent tool, hand-author them yourself. Either way you own
   their correctness: re-read every page against the course map.
5. Phase 5 checks on EVERY page: both gates with exit status read WITHOUT a pipe
   (`bash ~/Documents/claude_work/course-estate-audit/gate.sh <repo> > <scratch>/gate.log 2>&1; echo $?`
   and `python3 ~/.claude/skills/course-builder/scripts/pre-publish.py <repo> > <scratch>/pp.log; echo $?`).
   Then browser checks: serve with Bash `python3 -m http.server <port>` from the repo (pick a port
   8801-8803 given below), and use the mcp__Claude_Browser__* tools if you have them: bench ladder
   in the served page matches canon, one quiz click, computed fill on figure text, layout at 1280
   and 390. Use a scratch dir for logs, never the repo.
6. README.md in the repo (short, what it is, no hub banner - main thread adds it).

## Iron rules you must not break (from SKILL.md, repeated because they cause rework)

No em/en dashes anywhere. No meta text ("this course", "in this course"). "by Phoebe Fu", never
"built with". Never "lottery"/"lotteries". English words by default; any Chinese term carries its
English in brackets. Contested evidence: teach the disagreement. Bump `?v=` after css/js change.
Every page number must be one the widget actually prints. No `materials/` or "source map" wording
on the landing page. Titles/ids/classes must not collide with ds siblings (grep
`github_repo/learn-*/courses/*.html` headings before locking titles).

## Report back (short, plain text, no HTML)

Repo path; the 6 session titles; bench canon numbers (python vs node agreement); final gate and
pre-publish exit codes with log paths; browser checks done and anything you could NOT check;
sources read at source vs reported; open issues. Under 40 lines.

---
# COURSE-SPECIFIC ASSIGNMENT (verbatim from main thread, 2026-10-03)

COURSE: learn-databricks-with-phoebe (flips an existing planned hub card; keep slug). Repo: /Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-databricks-with-phoebe. Title "Databricks: Lakehouse for Data & AI". Bucket deng, diff 3, audience both, icon 🧱, serve port 8807.
Palette: Databricks lava red (#FF3621 family, deepened for AA on white) with navy (#1B3139 family) as ink/secondary. Compute CIELAB distance of your primary against every `--indigo` in github_repo/learn-*/assets/style.css, and against the AWS course being built in parallel (navy #232F3E family with orange); stay >= 12 from all.
ACCOUNTS (Phoebe-approved): Databricks Free Edition (no card) for the analyst build-alongs, AND every build-along also has a local path using the `deltalake` (delta-rs) Python package + DuckDB/polars so it runs without any account. Verify every local path in a scratch dir and paste real outputs; label which outputs came from local delta-rs vs what Free Edition would show. Pin versions you actually installed. Re-verify current Free Edition limits at source.
SEAMS (link, never teach): warehouse modelling = learn-data-warehouse; pipelines/orchestration = learn-data-engineering, learn-data-orchestration; streaming = learn-streaming-data; access-control concepts = learn-data-access-control (teach Unity Catalog grants as Databricks implements them); MLOps tooling generally = learn-dataops (teach MLflow-on-Databricks specifics only); AWS services = learn-aws-with-phoebe (sibling built in parallel - link its landing page). Grep sibling titles/ids before locking yours.
SOURCES read at source: Delta Lake PROTOCOL.md, Databricks docs (Delta, OPTIMIZE, Z-order, liquid clustering, data skipping stats, time travel/VACUUM retention, MERGE, CDF, Unity Catalog privileges, MLflow, DBU pricing, Free Edition), Armbrust et al. 2021 CIDR Lakehouse, Armbrust et al. 2020 VLDB Delta Lake. Liquid clustering now recommended over Z-order for new tables - teach honestly.
LEADER a1-a6: what a lakehouse is / Delta: a table that remembers / Unity Catalog governance / notebooks vs jobs / what DBUs cost / lakehouse vs warehouse decision.
ANALYST b1-b8: Delta tables by hand / the transaction log / time travel and restore / MERGE and CDC / data skipping and OPTIMIZE/Z-order / Unity Catalog grants / MLflow on Databricks / the Delta log bench.
BENCH b8: real Delta table via delta-rs from real public sample (NYC TLC trips), declared commit sequence (appends, update/MERGE, delete, OPTIMIZE, Z-order/clustering rewrite); ship _delta_log JSON (+checkpoint) and per-file stats as JS. Browser engine replays log per PROTOCOL (add/remove, version N snapshot, min/max stats): live files at version N; files/bytes scanned for learner predicate. Python reference (delta-rs file listing per version + skipping logic) and node agree on every version's live-file set and every preset query. Anti-lever: Z-order on a column nobody filters (verify). Break button: shuffle min/max stats; bench detects via full-scan ground-truth row count.
Scratch dir for this course: scratchpad/dbx/
