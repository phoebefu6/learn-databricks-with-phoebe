# Agent brief - shared by every fan-out page of learn-databricks-with-phoebe

You are writing ONE static HTML session page. No servers, no npm. **If your target file already
exists on disk, do not write it; report that and stop.** Write the file, return its path and one
line of coverage. No HTML in your reply.

## Read first, in this order

1. The template page for YOUR track. Copy its structure, classes, SVG grammar and quiz markup
   EXACTLY, including how many options each question has (4: A to D):
   - Leader track (a1-a6, no code): `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-databricks-with-phoebe/courses/a1-what-a-lakehouse-is.html`
   - Analyst track (b1-b8, Python): `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-databricks-with-phoebe/courses/b1-delta-tables-by-hand.html` (the bench page `courses/b8-the-delta-log-bench.html` is also a model for tables of canon numbers)
2. The source map: every verified number, its evidence tier, per-session coverage, the seams. Use
   ONLY its numbers; never invent a statistic; if a fact is missing, teach the uncertainty.
   `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-databricks-with-phoebe/materials/official-course-map.md`
3. Your page's outline: `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-databricks-with-phoebe/materials/outlines/<your file name>.md`
4. Analyst pages only: the script and its real output for your session in
   `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-databricks-with-phoebe/materials/build-alongs/` (`bN.py` and `bN.out.txt`). Code on the page is copied from `bN.py` (split into steps, comments may be shortened); every printed output is copied EXACTLY from `bN.out.txt`.
5. The stylesheet `:root` block for the palette tokens: `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-databricks-with-phoebe/assets/style.css` (first 30 lines are enough).

## Page skeleton (keep every component)

toolbar (crumb EXACTLY "learn-databricks-with-phoebe / Leader session N of 6" or "learn-databricks-with-phoebe / Analyst session N of 8", #toggle-all, #zoom-toggle) · masthead (eyebrow
"Learn Databricks with Phoebe · Leader track · Session N of 6" or "Learn Databricks with Phoebe · Analyst track · Session N of 8", h1 with one `<span class="accent">`, .sub, .chip-row with the level chip
from your outline (🟡 Core or 🟠 Hands-on), audience chips, time chip "45 min", .agenda a1-a4 with flex weights like the template) · main.wrap · section#intro (Part 0: kicker, .lede, .legend pills,
.callout.win "★ What you walk out with tonight.") · 3 Parts, each `section.section#part-N` with
section-kicker (klabel "Part N · covers ...", h2, `.tag.concept "N min live"`), a `.lede`, ONE
figure, `details.card` accordions (summary: `.mode.live` or `.mode.self`, title, `.mini`,
`.caret ▶`), at least one `.callout.example` with `span.ex-pill` "Real world" on the page ·
section#demo-1 Build-along (kicker `.tag.demo "★ 22 min · everyone builds"`, .lede, ONE figure,
`.steps > .step`, each with a `.prompt-box.good` carrying a `span.label`. Leader pages: a no-code artifact the leader writes (a policy, a matrix, a checklist, an estimate, a memo), and the prompt-boxes hold the written artifact, like a1. Analyst pages: like b1: code boxes labelled "★ bN.py, part K", then output boxes labelled EXACTLY "Output · laptop path, deltalake 1.6.6", then one last step for the Free Edition path labelled "★ Free Edition, SQL cell (not run in this build)" or "★ Free Edition, notebook cell (not run in this build)", whose box contains code only and never an invented output)
· one `.prompt-box.bad` after the steps and one `.callout.tip` · section#exercise Homework (ol, 4 items) · section#quiz (3 x `.quiz-q data-answer="0-based"`,
`p.qtext`, 4 x `button.qopt` "A · ...", `p.qwhy`; one `p.quiz-score` after the
last; spread the right answers across positions) · section#official, h2 EXACTLY "What this session teaches, and where it came from",
`.covered > .covered-row` (pill solid ✓ / light ◐ + name + note), then the `.mono` line EXACTLY
"Every fact on this page, and its verification tier, is recorded in the course's source map." ·
section.cheat#cheatsheet (h3 "Leader session N cheat sheet" or "Analyst session N cheat sheet", then ` <span>· pin this</span>`, .grid-2 of six
.cheat-item) · `.callout.next` with `.nx-pill` "Next session" · footer.pagefoot ·
`<script src="../assets/app.js?v=1"></script>`.

Head: the template's social meta block with this page's own title/description/url (og:url
`https://phoebefu6.github.io/learn-databricks-with-phoebe/courses/<file>`, og:image the course og-cover.png as in the template);
`<title>Leader session N · <Title> - learn databricks with phoebe</title>` (or Analyst session N);
`<link rel="stylesheet" href="../assets/style.css?v=1">`. Nothing else external.

First `details.card` in the FIRST Part is `open`; no other. Sentence case headings. Warm
practitioner voice, concrete, never dry. Inside prompt-boxes escape `&` `<` `>` (`&amp;` `&lt;` `&gt;`). 450 to 650 lines
is guidance about depth, never a target: never collapse whitespace, dissolve a list into a
paragraph, or drop a component to fit.

## Hard rules (a violation is rework)

- NEVER an em dash or en dash, anywhere (prose, code, aria-labels, comments). Hyphen only. Use "to" for ranges ("2 to 8").
- No meta text: never "this course", "in this course", "the course teaches", "banned here". State
  the professional norm directly with its reason. The two exact estate phrases above are the only
  self-references; "session 5" or "analyst session 8" cross-references are fine.
- Attribution "by Phoebe Fu". Never "built with" a tool.
- Every number comes from the map or is labelled constructed. For constructed data print "your
  numbers will differ", never invented outputs as if run.
- Contested or missing evidence: teach the disagreement; never resolve what the literature has not.
  Vendor claims (Databricks' own benchmarks, survey figures quoted by Databricks authors) are taught as claims and named as such.
- Citations in the exact form of the map's appendix; anything marked REPORTED is "reported" on the page.
- NEVER "lottery" or "lotteries"; say the mechanism ("decided by row order", "arbitrary", "a
  random draw"). A verbatim quoted title in curly quotes is the only exception.
- Default to English words; no Chinese on these pages.
- Titles, widget ids and class names must not collide with siblings: do not use the h1 or title "The lakehouse engine", "Lakehouse and the modern stack", "File and table formats", "Why a warehouse", "The warehouse in the AI era"; do not invent new CSS classes or widget ids (use only classes present in the template pages); figure ids and classes use only your page prefix.
- COURSE-SPECIFIC:
  - Free Edition: say "free", "non-commercial", "serverless only"; NEVER claim "no credit card" (not read at source). Quote limits only from the map; tell the reader to re-check the limitations page because limits change.
  - Free Edition steps are never run in this build: label them, give code only, no outputs, and use placeholders `your_catalog.your_schema...` for names (the catalog name in a Free Edition workspace was not verified).
  - DBU prices are Azure Databricks Premium, East US, pay as you go, read 3 October 2026. Always say that and that AWS and GCP list prices differ.
  - Liquid clustering is what Databricks recommends for new tables; delta-rs 1.6.6 offers Z-order, not CLUSTER BY. Say both honestly whenever clustering comes up.
  - Pinned install line (when installing): `pip install deltalake==1.6.6 duckdb==1.5.6 polars==1.44.2 pyarrow==25.0.1 pandas==3.0.6` (add `mlflow==3.16.1 scikit-learn==1.9.1` in session 7).
  - Seams: link, never teach (absolute URLs below). Teach only the Databricks-specific side.

## Figure grammar (hand-drawn, every figure)

Palette, ONLY these hexes (no invented greys): lava `#E00F00` · deep `#9E0B00` · mid `#B80C00` · soft `#FFB4A9` · tint `#FFF5F3` · ink (navy) `#1B3139` · muted `#4D6169` · faint `#C4CFD3` · hairline `#E2E8EA` · amber `#FFAB00` · amber ink `#4D3200` · amber tint `#FFF5DC` · paper `#FCFAF7` · `#FFFFFF` · universal reds
`#991B1B` `#FEF2F2` `#FCA5A5` only for a wrong-way panel or a wrong-way mark.
Text colour pairs that pass AA (use only these): ink, muted, deep, `#4D3200` or `#991B1B` on white/tint/paper/amber-tint/soft/hachure-with-white-backing; white text ONLY on `#E00F00`, `#9E0B00`, `#B80C00` or `#1B3139` fills; `#4D3200` or ink on `#FFAB00`. Never lava `#E00F00` text (use deep `#9E0B00`). Never white text on amber.

- `<figure class="zoomable">` > `<svg viewBox="0 0 880 H" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="the data, not the
  shape">` > `<defs>` + `<style>` + content, then `<figcaption>🔍 Click to zoom - takeaway</figcaption>`.
  Grow H, never W.
- Prefix unique per figure, used for every class and id: page code + letter, e.g. `a2a`, `a2b`, `a2c`, `a2d` (figure ids `a2aSk`, `a2aHc`, `a2aAr`; classes `.a2aH` ...). Never reuse another figure's prefix.
- `<defs>` holds three things with the figure prefix P: a wobble filter `id="PSk"`
(`feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="<int>"` +
`feDisplacementMap scale="2.4" xChannelSelector="R" yChannelSelector="G"`, `x="-3%" y="-3%"
width="106%" height="106%"`), a hachure pattern `id="PHc"` (7x7 userSpaceOnUse, rotate(-38), one
`#E00F00` line, opacity .5), an open arrowhead `id="PAr"` (path `M1 1 L9 5 L1 9`, fill none, stroke `#1B3139`
1.6). ALL shapes sit inside ONE `<g filter="url(#PSk)" fill="none" stroke="#1B3139" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">`; rects carry a tiny rotation (-4 to 4 degrees for
hand-placed items, under 1 for panels). Fills: white, tint, the hachure for "the pile" or "the
data" (put a plain white rect OUTSIDE the filtered group behind any text that sits on hachure, as a1 and b1 do), and amber ONLY for the one thing the figure is about. One doodle anchor per
figure, simple strokes, never a mascot. Text classes: `.PH` 800 12px ink heading · `.PL` 600 12px
ink label · `.PS` 400 11px muted · `.PB` 800 11px `#4D3200` · `.PV` 800 16-20px `#9E0B00` value · `.PW` 800 12px white on a dark fill · `.PC` 600 11px monospace `#9E0B00` code · `.PN` 400 12px muted note. Hand-stacked items must not overlap as painted rects (the gate flags a pile).
- ALL `<text>` outside any filtered group, sans stack, never below 10.5px.
- Fit: max chars ≈ (box width - 20) / 7 at 12px, 6.4px/char at 11px; full-width note under 110 chars; 40px between neighbouring point labels; bottom
  note 22px below the last row, H clears it by 8px. No arrow or line may pass through a text label (the gate flags line-through-text). When in doubt, shorten.
- Floor: one figure per Part plus one in the build-along (4 figures). Draw the MECHANISM (which files a commit adds and removes, how a grant chain is evaluated, two bills adding up, a DAG of tasks, an alias pointing at a model version), never a metaphor literally, never decoration.

## Voice and honesty

Every Part gets a real-world story from the map's cases or a constructed one that says "constructed" on the page. Stories from the Delta paper or the CIDR paper are the authors' own reports: say so.

## Cross-links (absolute URLs)

- Warehouse modelling: https://phoebefu6.github.io/learn-data-warehouse-with-phoebe/
- Pipelines: https://phoebefu6.github.io/learn-data-engineering-with-phoebe/
- Orchestration (schedules, retries, backfills): https://phoebefu6.github.io/learn-data-orchestration-with-phoebe/
- Streaming: https://phoebefu6.github.io/learn-streaming-data-with-phoebe/
- Access-control concepts (RBAC, row filters, masking): https://phoebefu6.github.io/learn-data-access-control-with-phoebe/
- MLOps tooling in general: https://phoebefu6.github.io/learn-dataops-with-phoebe/
- AWS services and the cloud bill: https://phoebefu6.github.io/learn-aws-with-phoebe/
- The bench: `b8-the-delta-log-bench.html` (relative, same folder)
- Hub: https://phoebefu6.github.io/learn-with-phoebe/

## Footer chain(s) and session titles

Leader: a1-what-a-lakehouse-is.html "What a lakehouse is" → a2-a-table-that-remembers.html "Delta: a table that remembers" → a3-unity-catalog-governance.html "Unity Catalog: who may see what" → a4-notebooks-vs-jobs.html "Notebooks versus jobs" → a5-what-dbus-cost.html "What a DBU costs" → a6-lakehouse-or-warehouse.html "Lakehouse or warehouse?"
Analyst: b1-delta-tables-by-hand.html "Delta tables by hand" → b2-the-transaction-log.html "Reading the transaction log" → b3-time-travel-and-restore.html "Time travel and restore" → b4-merge-and-change-data.html "MERGE and change data" → b5-data-skipping-and-clustering.html "Data skipping, OPTIMIZE and clustering" → b6-unity-catalog-grants.html "Unity Catalog grants" → b7-mlflow-on-databricks.html "MLflow on Databricks" → b8-the-delta-log-bench.html "The Delta log bench"
Footer left: "Leader session N of 6 · learn-databricks-with-phoebe · by Phoebe Fu &nbsp;·&nbsp; 📚 <a href="https://phoebefu6.github.io/learn-with-phoebe/">Learn with Phoebe ↗</a>" (or Analyst session N of 8)
Footer right: `<a href="PREV">← Prev: <title></a> &nbsp;·&nbsp; <a href="NEXT">Next: <title> →</a>`; a6 ends with `<a href="../index.html">Course home</a>` as its second link.

Session titles (exact, sentence case, one accent span in h1): as listed above; the h1 text must equal the title (the accent span wraps one or two words of it).
