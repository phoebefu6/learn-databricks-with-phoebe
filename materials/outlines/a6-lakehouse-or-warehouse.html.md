# a6-lakehouse-or-warehouse.html · "Leader session 6 of 6" · Lakehouse or warehouse?
h1: `Lakehouse or <span class="accent">warehouse</span>?` · 🟠 Hands-on · chips "Data leaders and architects", "Bring your copy map and estimate"
Win: a one-page decision memo for your organisation, with the evidence you trust and the evidence you discount, and a decision tree you can reuse.

Part 1 · covers the case for the lakehouse · "What one copy buys" · 5 min live
- Figure (a6a): the four two-tier problems from the CIDR paper (reliability, staleness, limited advanced analytics, total cost of ownership) each matched to the lakehouse mechanism that addresses it (one copy so no lake-to-warehouse ETL; direct file access for ML; open format against lock-in; the metadata layer for transactions and versions).
- Cards: (open, Live) the paper's claim and who makes it; (Live) Delta paper evidence: metadata at scale (a 1-million-partition table listed in 108 s with Delta, 17 s with the log cached; Hive took over an hour at 10,000 partitions); (Self) Delta used in "about half of Databricks' workload" (authors' claim).

Part 2 · covers reading the evidence · "A vendor benchmark, read honestly" · 6 min live
- Figure (a6b): TPC-DS at scale factor 30,000, 960 vCPUs: bars for duration and cost: Delta Engine 3,302 s / $104 on demand, 3,252 s / $56 spot; four unnamed cloud warehouses 2,996 to 37,283 s and $153 to $570 (Figure 3 of the CIDR paper). Annotate: run by the authors, competitors unnamed, settings chosen by the winner, data cached on SSD first (the paper notes Delta Engine was 18% slower from a cold cache).
- Cards: (Live) how to read it (claim to test, not to quote as fact); note one unnamed warehouse (2,996 s) was faster than Delta Engine on duration; (Live) the paper's own open questions (log in the object store limits transactions per second; single-table transactions); (Self) the 86 percent staleness figure is a reported survey.

Part 3 · covers the decision · "When each one wins" · 5 min live
- Figure (a6c): a decision tree: Does ML or Python need the same data as BI? → Do several engines need to read it? → Is most of the data semi-structured or unstructured? → Is the team SQL-only with an existing warehouse that meets its needs? Outcomes: lakehouse; warehouse; both for now with a migration test. Keep it a decision tree with 3 levels max, 4 outcomes max.
- Cards: (Live) where a warehouse stays the better answer (pure BI, SQL-only team, warehouse already paid for and fresh enough); (Live) what to test on your own workload (one real query set, cost per run from session 5, freshness from the copy map); (Self) seam: dimensional modelling and warehouse internals in learn-data-warehouse (link); measured skipping trade-off from the bench (JFK 8 of 8 → 2 of 8 by zone; date query 2 of 8 → 8 of 8): layout is a design decision either way.
- Real world (constructed): two companies with the same data volume and opposite right answers.

Build-along (no code): "The decision memo" · figure (a6d): a memo template: context (copy map tally), options, evidence trusted, evidence discounted, test to run, decision, review date.
Steps: paste your copy-map tally (session 1); paste your monthly estimate (session 5); list the evidence you trust (your measurements) and discount (vendor benchmarks, vendor surveys) and say why; define a two-week test (one query set on both); write the decision and a review date. Bad box: "We chose X because the benchmark says it is 2x faster." Tip: a decision that names the evidence it discounted survives the next vendor pitch.
Quiz: (1) the TPC-DS figure is a vendor-run benchmark (how to use it); (2) one open question the authors themselves raised (log in object store limits transaction rate); (3) a case where a warehouse is the better answer.
Covered: CIDR 2021 paper read at source; Delta Lake paper PVLDB 2020 read at source; bench numbers measured; survey REPORTED; stories constructed.
Cheat: four two-tier problems; vendor benchmark = claim to test; Delta Engine $104 vs $153 to $570 (authors' run); log in object store limits transactions/s; single-table transactions; decide with your own copy map and estimate.
Next: that is the end of the leader track; suggest analyst session 1 (Delta tables by hand) or the bench (analyst session 8) to see the mechanics.
Footer: prev a5 "What a DBU costs", then `<a href="../index.html">Course home</a>`.
