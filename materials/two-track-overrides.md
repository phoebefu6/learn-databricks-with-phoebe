# Overrides for two-track builds (win over course-lead-common.md)

- TWO-TRACK 6 + 8 = 14 pages, TOTAL_SESSIONS 14. Shape donor:
  /Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-data-observability-with-phoebe (a1-a6 / b1-b8).
  Track labels "Leader" and "Analyst": copy how
  /Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-product-analytics-with-phoebe (shipped 2026-10-01,
  same shape, cleanest recent example) handles app.js crumb regex, journey arrays and the Analyst label.
  Hand-drawn SVG grammar + real-rows/real-engine bench discipline from the RFM donor.
- Hand-author Leader 1, Analyst 1, the bench page (b8) and index.html first; gate them; then fan out,
  max 3 in flight.
- KNOWN HARNESS ISSUES: fan-out completion notices may NOT reach you, and session limits kill agents
  mid-file. Poll disk (ls + details/section/html tag balance), never wait on notifications. A killed
  agent can leave a PARTIAL file that "exists": tag-balance-check before trusting any page, delete a
  partial before relaunching. If a page has no balanced file ~10 min after launch, relaunch it or
  hand-author it.
- Gate with the REPO NAME, never an absolute path:
  `bash ~/Documents/claude_work/course-estate-audit/gate.sh <slug>` - an absolute path makes the layout
  probe scan 0 pages and still pass. Confirm "LAYOUT: 30 page-widths scanned" (14 pages + index, x2).
- Run pre-publish.py from inside ~/Documents/claude_work/github_repo (lowercase path); from another cwd
  its OGCOVER check false-positives on letter case.
- Donor stylesheet contrast: any rule with `--amber-ink` text on an `--amber` fill fails (1.5:1) - use
  white text on the warm fill; `.chip.audience` wash must be rgba(255,255,255,.08), not .16; lightbox
  scrim light. Measure painted contrast on every page (all text >= 4.5:1, large >= 3:1).
- Landing <title> must be "Learn <Name> with Phoebe" or "<Name> - Learn with Phoebe".
- Do NOT create og-cover.png. No git init, no push, no hub edit.
