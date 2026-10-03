# b4-merge-and-change-data.html · "Analyst session 4 of 8" · MERGE and change data
h1: `MERGE and <span class="accent">change data</span>` · 🟠 Hands-on · chips "Analysts and engineers who write Python", "Laptop path needs no account"
Script: b4.py / b4.out.txt (stand-alone; builds trips_cdf).
Win: one MERGE that applies inserts, updates and deletes in one commit, the change data feed that reports them, and two traps found on purpose.

Part 1 · covers MERGE · "Insert, update and delete in one commit" · 6 min live
- Figure (b4a): source rows tagged U (5 tip corrections), D (3 cancellations), I (275 late store-and-forward trips) meeting target rows matched on trip_id; clauses WHEN MATCHED AND op='D' DELETE, WHEN MATCHED AND op='U' UPDATE, WHEN NOT MATCHED AND op='I' INSERT; result counts 275 inserted, 5 updated, 3 deleted.
- Cards: (open, Live) MERGE clauses WHEN MATCHED / WHEN NOT MATCHED / WHEN NOT MATCHED BY SOURCE (docs); delta-rs builder: when_matched_delete, when_matched_update, when_not_matched_insert_all. (Live) the feed is constructed on real rows (say so): the late trips are real store_and_fwd 'Y' trips, the corrections and cancellations are made up. (Self) MERGE rewrites the files holding matched rows; on the bench a MERGE of 31 late + 270 re-sent trips removed 1 file and added 1 plus a cdc file.
- Real world: the bench's re-sent 12 January batch (constructed retry) matched on trip_id added no duplicates.

Part 2 · covers the change data feed · "The table tells you what changed" · 5 min live
- Figure (b4b): CDF rows: delete 3, insert 275, update_preimage 5, update_postimage 5, with _commit_version 1; drawn as a ledger next to the table.
- Cards: (Live) enable with `delta.enableChangeDataFeed = true`; not on by default; records only changes after enabling; columns _change_type, _commit_version, _commit_timestamp; `table_changes('t', 0, 10)` (docs). (Live) PROTOCOL: change data files in _change_data, cdc actions with dataChange false; readers use cdc files when present, otherwise treat adds as inserts and removes as deletes. (Self) VACUUM deletes change data files too (docs); seam: consuming changes continuously is streaming (learn-streaming-data link); pipelines (learn-data-engineering link).

Part 3 · covers two traps · "The duplicate and the NULL" · 4 min live
- Figure (b4c): before-after: left, a source with two rows for trip_id X both matching one target row → refused (DeltaError; docs: "A merge operation can fail if multiple rows of the source dataset match and the merge attempts to update the same rows of the target"); right, the NULL trap: on 15 January store_and_fwd is N 73,893, Y 275, NULL 2,865; filtering with != 'Y' silently drops the 2,865 NULL rows (in SQL, NULL != 'Y' is not true).
- Cards: (Live) deduplicate the source first (docs). (Live) the NULL trap and the fix: treat NULL as on time explicitly (the script's fill_null). (Self) why both traps matter more in CDC: a feed retried twice contains duplicates by design.
- Real world: the first draft of b4.py in this build loaded 73,893 trips instead of 76,758 because of the NULL filter; caught by a total that did not match 77,033 (true story of this build; say so).

Build-along: b4.py in five parts: load and split (output: loaded: 76758 trips; held back as late: 275); build the feed; MERGE (output merge dict); read CDF (output change rows by type); duplicate source (output: duplicate source refused: DeltaError / version now: 1). Free Edition step (not run): `ALTER TABLE ... SET TBLPROPERTIES (delta.enableChangeDataFeed = true)`, a SQL MERGE INTO with the three clauses, `SELECT _change_type, count(*) FROM table_changes('your_catalog.your_schema.trips_cdf', 1) GROUP BY 1`. Figure (b4d): the build-along pipeline from the parquet file to the CDF counts.
Bad box: MERGE straight from a raw feed without dedup. Tip: check that totals reconcile (76,758 + 275 = 77,033) before trusting a MERGE.
Quiz: (1) what update_preimage is; (2) why a duplicated source row is refused; (3) why != 'Y' lost 2,865 trips.
Covered: Databricks MERGE and change data feed docs read at source; PROTOCOL.md cdc read at source; outputs run; feed constructed on real rows.
Cheat: one MERGE, one commit; clauses; enable CDF first; four change types; dedupe the source; NULL is not "not Y".
Next: session 5: why a query on these tables reads some files and skips others.
Footer: prev b3 "Time travel and restore", next b5 "Data skipping, OPTIMIZE and clustering".
