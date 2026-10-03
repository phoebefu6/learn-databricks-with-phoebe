# b5-data-skipping-and-clustering.html · "Analyst session 5 of 8" · Data skipping, OPTIMIZE and clustering
h1: `Data skipping, OPTIMIZE and <span class="accent">clustering</span>` · 🟠 Hands-on · chips "Analysts and engineers who write Python", "Laptop path needs no account"
Script: b5.py / b5.out.txt (the whole month, 2,964,606 rows, 31 daily appends, 4 MB target).
Win: skipping computed by hand from the log's min/max, the before-and-after of OPTIMIZE and Z-order on the full month, and the honest version of "Databricks recommends liquid clustering for new tables".

Part 1 · covers per-file statistics · "Min and max decide what a query reads" · 5 min live
- Figure (b5a): files as boxes with [min, max] for pu_zone and pickup_ts; predicate pu_zone = 132 reads a file only if 132 is inside its range. Real full-month numbers: 31 daily files: JFK 31/31 files (100.0% of bytes), 15 Jan 1/31 (2.7%).
- Cards: (open, Live) stats per file: numRecords, minValues, maxValues, nullCount (PROTOCOL.md); Databricks collects them on the first 32 columns by default for UC external tables, managed tables use predictive optimization; `delta.dataSkippingNumIndexedCols`, `delta.dataSkippingStatsColumns`; long strings truncated (docs). (Live) the CIDR paper: min-max statistics enable skipping "when the base data is clustered". (Self) wide vs tight bounds and nullCount rules (PROTOCOL.md).

Part 2 · covers OPTIMIZE and Z-order · "Fewer files, then the right files" · 6 min live
- Figure (b5b): three layouts of the same month: 31 daily files; OPTIMIZE compact to 8 files (JFK 8/8 100.0%, 15 Jan 1/8 12.9%); ZORDER BY pu_zone to 6 files (JFK 1/6 17.9%, 15 Jan 6/6 100.0%).
- Cards: (Live) OPTIMIZE bin-packing is idempotent (docs); compaction alone does not help JFK. (Live) Z-order sorts along a space-filling curve so each file covers a narrow range of the chosen columns; Delta paper Figure 5: single sort skips 99% on one column and 0% on the others; Z-order on four columns skips 44% to 67% on each, 54% on average vs 25%. (Self) the trade: the date query went from 1 of 8 to 6 of 6; same pattern on the bench (session 8).
- Real world: the Delta paper's 500 TB network-traffic table that skipped 93% (authors' customer report).

Part 3 · covers liquid clustering · "What Databricks recommends now" · 4 min live
- Figure (b5c): side by side: ZORDER (choose columns per OPTIMIZE, full rewrite) vs liquid clustering (CLUSTER BY up to 4 keys declared on the table, OPTIMIZE clusters incrementally, OPTIMIZE FULL reclusters all, CLUSTER BY AUTO picks keys from query patterns on UC managed tables). PROTOCOL: clustered tables record keys in domainMetadata "delta.clustering" and clusteringProvider "liquid" on files.
- Cards: (Live) "Databricks recommends liquid clustering for all new tables, including streaming tables and materialized views"; incompatible with partitioning or ZORDER; max four keys; runtime 15.4 LTS+, CLUSTER BY AUTO 15.4 LTS+, OPTIMIZE FULL 16.4 LTS+ (docs). (Live) honest limit: delta-rs 1.6.6 offers Z-order, not CLUSTER BY, so the laptop path stays with Z-order; the skipping mechanism is the same min/max check. (Self) predictive optimization runs OPTIMIZE on UC managed tables (docs).

Build-along: b5.py in four parts: daily appends (31 writes); files_read function using get_add_actions(flatten=True) min/max (show code); report before; compact at 4 MB; z_order on pu_zone; JFK count 145,240 (output 4 lines + rows line). Free Edition step (not run): `CREATE TABLE your_catalog.your_schema.trips_month CLUSTER BY (pu_zone) AS SELECT ...; OPTIMIZE your_catalog.your_schema.trips_month;` and `ALTER TABLE ... CLUSTER BY AUTO` (UC managed tables). Figure (b5d): the files_read predicate drawn as interval-overlap: read if not (max < lo or min > hi).
Bad box: ZORDER BY a column no query filters (link the bench's vendor branch: 8 of 8 files). Tip: cluster on the columns your heaviest queries filter, and measure files read before and after.
Quiz: (1) when a file can be skipped for pu_zone = 132; (2) why compaction alone left JFK at 8 of 8; (3) what Databricks recommends for new tables and why the laptop uses Z-order.
Covered: PROTOCOL.md stats and clustered tables; Databricks data skipping, OPTIMIZE and liquid clustering docs; Delta Lake paper Figure 5 and 500 TB case (authors' report); outputs run.
Cheat: read iff ranges overlap; 32 columns by default; compaction is not clustering; Z-order trades questions; liquid for new tables (max 4 keys, AUTO on managed); measure files read.
Next: session 6: who may read these files at all.
Footer: prev b4 "MERGE and change data", next b6 "Unity Catalog grants".
