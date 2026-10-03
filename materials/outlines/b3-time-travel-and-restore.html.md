# b3-time-travel-and-restore.html · "Analyst session 3 of 8" · Time travel and restore
h1: `Time travel and <span class="accent">restore</span>` · 🟡 Core · chips "Analysts and engineers who write Python", "Laptop path needs no account"
Script: b3.py / b3.out.txt (after b1.py and b2.py on trips_delta).
Win: reading any version, restoring safely with a new commit, and knowing exactly which VACUUM ends which version's life.

Part 1 · covers time travel · "Time travel is the replay, stopped early" · 5 min live
- Figure (b3a): three readers on the same folder: VERSION AS OF 0 (1 file, 21,617 rows), 1 (2 files, 77,033), 2 (1 file, 76,103), each a different subset of files.
- Cards: (open, Live) delta-rs `DeltaTable(path, version=v)`; Databricks SQL `VERSION AS OF`, `TIMESTAMP AS OF`, `@v123` (docs). (Live) history: newest first; output 2 DELETE, 1 WRITE Append, 0 WRITE ErrorIfExists. (Self) time travel by timestamp needs commit timestamps; the In-Commit Timestamps feature exists in the protocol (mention only, PROTOCOL.md).
- Real world: the bench: slide v30 to v33 and the JFK answer stays 358 rows while the files change (no data change at v33).

Part 2 · covers RESTORE · "Undo is a new commit" · 5 min live
- Figure (b3b): log arrow v0 → v1 → v2 (DELETE) → v3 (RESTORE to 1): v3 re-adds v1's files and removes v2's; history keeps v2; RESTORE dataChange true (docs) so streaming readers may reprocess.
- Cards: (Live) output: after RESTORE: version 3 rows 77033. (Live) restore is "a data-changing operation" (docs) and can create duplicates downstream. (Self) the bench's v35 RESTORE commit: protocol, metaData, 8 remove, 8 add, dataChange true.

Part 3 · covers VACUUM and retention · "The command that ends history" · 5 min live
- Figure (b3c): files on a timeline with retention window; VACUUM deletes files no version inside the window needs; version 2's DELETE-output file becomes unreachable after retention 0. Real: dry run at default retention 0 files; retention 0 with check off deleted 1 file; time travel to version 2 fails FileNotFoundError; latest still 77,033.
- Cards: (Live) defaults 7 days file retention, 30 days log retention; safety check; DRY RUN up to 1,000 files; LITE vs FULL (docs). (Live) "If you run VACUUM on a Delta table, you lose the ability to time travel back to a version older than the specified data retention period." (Self) why the deleted file was the DELETE's output (version 2 added it, version 3 removed it, nothing live needs it). Make sure the explanation matches: after RESTORE to 1, the file added by v2 is a tombstone; VACUUM retention 0 deletes it; version 2 needs it, so reading version 2 fails.
- Real world (constructed): an engineer saving storage with RETAIN 0 HOURS on a shared table.

Build-along: b3.py in four parts: versions loop (3 output lines), history (3 lines), RESTORE (1 line), VACUUM dry run, forced VACUUM, failing time travel, latest read (4 lines). Free Edition step (not run): `DESCRIBE HISTORY ...; SELECT count(*) FROM ... VERSION AS OF 0; RESTORE TABLE ... TO VERSION AS OF 1; VACUUM ... DRY RUN;`. Figure (b3d): the folder before and after the forced VACUUM, with the one deleted file crossed in red.
Bad box: `dt.vacuum(retention_hours=0, enforce_retention_duration=False, dry_run=False)` on a shared table. Tip: run DRY RUN first and keep retention at least as long as the oldest version anyone may need.
Quiz: (1) what RESTORE writes (a new commit, dataChange true); (2) why version 2 fails after the forced VACUUM; (3) what the default VACUUM retention is (7 days).
Covered: Databricks "Work with table history" and "VACUUM" docs read at source; PROTOCOL.md; outputs run; story constructed.
Cheat: version=v / VERSION AS OF; history newest first; RESTORE = new commit; 7-day files, 30-day log; DRY RUN first; VACUUM past retention ends time travel.
Next: session 4: MERGE, where a single commit inserts, updates and deletes.
Footer: prev b2 "Reading the transaction log", next b4 "MERGE and change data".
