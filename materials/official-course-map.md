# Official course map - learn-databricks-with-phoebe

"Databricks: Lakehouse for Data & AI". Bucket deng, diff 3, audience both, icon 🧱.
Two tracks: Leader a1-a6 (no code) and Analyst b1-b8 (Python + Free Edition), 45 min each, 14 sessions.
Built 2026-10-03. Fast-moving product: re-verify Free Edition limits, DBU list prices, liquid
clustering runtime versions and MLflow behaviour before every delivery.

Evidence tiers used below:
- **READ** = read at the primary source in this build (URL + date).
- **RUN** = produced by running code in this build; script and output saved under `materials/`.
- **REPORTED** = secondary source, or a claim made by an interested party; pages must say "reported" or name who claims it.
- **CONSTRUCTED** = invented for teaching, labelled on the page.

---

## 1. Pinned versions (actually installed and run, 2026-10-03)

Python 3.11.11 · deltalake (delta-rs) 1.6.6 · duckdb 1.5.6 (+ its `delta` extension, `INSTALL delta; LOAD delta`) ·
polars 1.44.2 · pyarrow 25.0.1 · pandas 3.0.6 · mlflow 3.16.1 · scikit-learn 1.9.1 · node v22.6.0 for the engine check.

Learner install line (exactly what was installed):
`pip install deltalake==1.6.6 duckdb==1.5.6 polars==1.44.2 pyarrow==25.0.1 pandas==3.0.6 mlflow==3.16.1 scikit-learn==1.9.1`

## 2. Data

NYC TLC yellow taxi trip records, January 2024: `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet`
(49,961,641 bytes, public, no login; NYC Taxi and Limousine Commission, "TLC Trip Record Data" page). RUN facts:
- 2,964,624 rows in the file; 2,964,606 with a pickup inside January 2024.
- Zone 132 = JFK Airport, 138 = LaGuardia Airport, 161 = Midtown Center (taxi_zone_lookup.csv, same CDN). JFK is the busiest pickup zone in the month: 145,240 trips.
- store_and_fwd_flag = 'Y' (trip held in the vehicle's memory because there was no server connection, sent later): 11,336 in the month.
- fare_amount < 0 (voided or refunded records): 37,448 in the month.
- 15 January 2024: 77,033 trips (21,617 before noon, 55,416 after); store_and_fwd N 73,893 · Y 275 · NULL 2,865; 930 with fare below 0.

## 3. The bench (analyst session 8) - canon numbers

Builder: `materials/build-delta-bench.py` (run from a scratch dir). Engine: `assets/dbx-bench.js`. Data: `assets/dbx-bench-data.js` (293,364 bytes, json.dumps).
Check: node replay vs Python reference (delta-rs's own `get_add_actions` per version + the same skipping logic + delta-rs full-table read as ground truth):
**370 checks, 0 mismatches** (live-file set for every version of every branch, with and without the checkpoint; files, bytes, rows found and full-scan truth for 4 presets x honest/broken).
Verifier tested against a failing engine (removes ignored): 47 mismatches reported. RUN.

Sample: 8,000 real trips, seed 20240101, uniform over January pickups, trip_id 1..8,000 in pickup order.
31 store-and-forward trips held back as late; 270 trips of 12 January re-sent (CONSTRUCTED uploader retry).
File target 28,672 bytes (28 KB, scaled down; set as `delta.targetFileSize` and as the OPTIMIZE target).

Commit sequence (log facts read from the JSON delta-rs wrote):
| Version | Operation | Log actions | Live files after |
|---|---|---|---|
| v0 | WRITE (creates; protocol 3/7 with timestampNtz; CDF on) | commitInfo, protocol, metaData, 1 add | 1 (225 rows) |
| v1-v30 | WRITE append, one per pickup day | commitInfo + 1 add each | 31 at v30 (7,969 rows, 331,246 bytes) |
| v31 | MERGE on trip_id: 31 late inserted, 270 re-sent matched and updated | 1 remove, 1 add, 1 cdc | 31 (8,000 rows) |
| v32 | DELETE WHERE fare_amount < 0: 113 rows | 30 remove, 8 add, 1 cdc | 9 (7,887 rows, 165,920 bytes) |
| checkpoint | `00000000000000000032.checkpoint.parquet` written by `create_checkpoint()`; `_last_checkpoint` says version 32, 9 add files | | |
| v33 | OPTIMIZE (compact), dataChange false | 2 remove, 1 add | 8 (159,756 bytes) |
| v34 zone branch | OPTIMIZE ZORDER BY (pu_zone), dataChange false | 8 remove, 8 add | 8 (171,361 bytes) |
| v34 vendor branch | OPTIMIZE ZORDER BY (vendor_id), dataChange false | 8 remove, 8 add | 8 (162,652 bytes) |
| v35 vendor branch | RESTORE to version 33, dataChange TRUE | protocol, metaData, 8 remove, 8 add | 8, same files as v33 |

delta-rs did NOT write a checkpoint on its own in 33 commits; the one at v32 was written by hand. The OPTIMIZE ZORDER commit's
`operationParameters` records only predicate and targetSize, not the z-order columns.

Files read (honest stats) per preset, "files read / live files (share of bytes)", rows found = full-scan truth in every honest case:
| Layout | JFK (pu_zone = 132) | 15 January | trip_distance > 20 | JFK, 22-28 January |
|---|---|---|---|---|
| v30, 31 daily files | 31/31 (100.0%) · 371 rows | 1/31 (2.7%) · 189 | 27/31 (86.6%) · 76 | 7/31 (23.3%) · 66 |
| v33, after MERGE, DELETE, OPTIMIZE | 8/8 (100.0%) · 358 | 2/8 (25.7%) · 186 | 8/8 (100.0%) · 74 | 3/8 (38.5%) · 64 |
| v34 ZORDER BY pu_zone | **2/8 (26.5%)** · 358 | **8/8 (100.0%)** · 186 | 7/8 (90.1%) · 74 | 2/8 (26.5%) · 64 |
| v34 ZORDER BY vendor_id (anti-lever) | **8/8 (100.0%)** · 358 | **8/8 (100.0%)** · 186 | 8/8 (100.0%) · 74 | 8/8 (100.0%) · 64 |
| v35 RESTORE to 33 | 8/8 · 358 | 2/8 (25.7%) · 186 | 8/8 · 74 | 3/8 (38.5%) · 64 |

Anti-lever verified on the data: clustering on vendor_id leaves the JFK query at 8 of 8 files (no drop from v33) AND
makes the 15 January query worse, 2/8 to 8/8, because the rewrite scatters the time order the daily loads had given.
Clustering on pu_zone also costs the date query (2/8 to 8/8): clustering is a choice of which question gets cheap.

Break button (stats dealt to the wrong files by a fixed derangement, mulberry32 seed 7, same in Python and JS):
- v34 zone, JFK: reads 2 files, finds **0 of 358** rows. 15 January at v33: 0 of 186. JFK 22-28 Jan at v33: 0 of 64.
- v30, 15 January: 1 file read, 0 of 189. v30 JFK 22-28 Jan: 16 of 66. trip_distance > 20 at v30: 68 of 76.
- Where skipping already reads every file (JFK at v30/v33, everything on the vendor branch) the shuffle changes nothing:
  the break can only hurt where skipping is doing work. The page must say this rather than hide it.

## 4. Analyst build-along canon (local path RUN; scripts and outputs in `materials/build-alongs/`)

Every script runs in an empty scratch folder next to the downloaded parquet file. Free Edition outputs are NOT run in this
build: pages label them "what Free Edition would show" and give the SQL, never invented output.

- **b1** (`b1.py`): morning 21,617 + afternoon 55,416 = 77,033 rows; version 1; 2 data files; `_delta_log` holds
  00000000000000000000.json and 00000000000000000001.json; DuckDB, polars and pandas all read 77,033; a string fare is
  refused with `SchemaMismatchError` and the version stays 1.
- **b1 log, version 1 `add` stats** (read from the JSON delta-rs wrote): numRecords 55,416; pickup_ts min "2024-01-15 12:00:02", max "2024-01-15 23:59:58"; fare_amount min -380.0, max 577.0; pu_zone 1 to 265; protocol minReaderVersion 3, minWriterVersion 7, feature timestampNtz.
- **b2** (`b2.py`): v0 actions commitInfo, protocol, metaData, add; v1 commitInfo, add. DELETE fare < 0 removes 930 rows,
  2 files removed, 1 added. Hand replay: v0 1 file 21,617 rows; v1 2 files 77,033; v2 1 file 76,103; agrees with delta-rs
  at every version. Checkpoint at v2; `_last_checkpoint` = {"version":2,"size":5,"sizeInBytes":15132,"numOfAddFiles":1}.
- **b3** (`b3.py`): VERSION AS OF 0/1/2 = 21,617 / 77,033 / 76,103 rows. History newest first: 2 DELETE, 1 WRITE Append,
  0 WRITE ErrorIfExists. RESTORE to 1 makes version 3 with 77,033 rows. VACUUM dry run at default retention: 0 files.
  VACUUM retention 0 with the check off deleted 1 file; time travel to version 2 then fails with FileNotFoundError;
  latest still reads 77,033.
- **b4** (`b4.py`): 76,758 trips loaded, 275 late held back (null flags count as on time: 2,865 trips on 15 Jan have a NULL
  flag, and `!= 'Y'` silently drops them). Constructed change feed: 5 tip corrections (U), 3 cancellations (D), 275 late (I).
  MERGE: 275 inserted, 5 updated, 3 deleted. CDF from version 1: delete 3, insert 275, update_postimage 5, update_preimage 5.
  A source with two rows for one target row is refused (DeltaError); version stays 1.
- **b5** (`b5.py`, the whole month, 2,964,606 rows, 31 daily appends): JFK 31/31 files (100.0% of bytes), 15 Jan 1/31 (2.7%).
  OPTIMIZE compact at 4 MB: JFK 8/8 (100.0%), 15 Jan 1/8 (12.9%). ZORDER BY pu_zone at 4 MB: JFK 1/6 (17.9%),
  15 Jan 6/6 (100.0%). JFK trips 145,240.
- **b6** (`b6.py`, a LOCAL MODEL of the documented rule, not Unity Catalog): SELECT alone denied (missing USE CATALOG,
  USE SCHEMA); all three grants: can read; schema-level SELECT reaches a table created later; another group without it is
  denied, missing SELECT.
- **b7** (`b7.py`, local MLflow, sqlite backend): 61,260 card trips on 15 Jan with fare above 0; test MAE linear $1.387,
  random forest (100 trees, depth 8) $1.331; forest registered as taxi_tip_model version 1, alias @champion; on a real JFK
  test trip: fare $85.60, 21.66 miles, predicted tip $14.93, actual $21.77. MLflow 3.16 refused to save the forest until
  `skops_trusted_types=["sklearn.tree._tree.Tree"]` was passed; the signature refused an int64 pu_zone against the logged int32.

## 5. Leader canon

**DBU arithmetic** (`materials/dbu-numbers.py`, RUN on READ prices): Azure Databricks Premium, East US, USD, pay as you go,
Azure retail prices API read 2026-10-03 (saved in `materials/sources/`): All-purpose $0.55/DBU-hour, Jobs $0.30, Jobs Light
$0.22, SQL classic $0.22, SQL Pro $0.55, Serverless SQL $0.70, Interactive serverless $0.95, Automated serverless $0.45.
DS3 v2 (4 vCPU, 14 GiB) = 0.75 DBU per hour on all-purpose and jobs compute (Azure pricing page instance table); DS3 v2
Linux VM $0.293/hour. A 5-node DS3 v2 cluster: 3.75 DBU/h; all-purpose $2.0625 DBU + $1.465 VMs = $3.5275/h; jobs
$1.125 + $1.465 = $2.59/h. A 2-hour nightly job: $7.06 vs $5.18; 30 nights $211.65 vs $155.40. An all-purpose cluster left on
for 14 idle hours: $49.39. Serverless SQL warehouse 2X-Small = 4 DBU/h = $2.80/h. Warehouse sizes in DBU/h (Azure page):
2X-Small 4, X-Small 6, Small 12, Medium 24, Large 40, X-Large 80, 2X-Large 144, 3X-Large 272, 4X-Large 528.
DBU rate ratio all-purpose to jobs: 1.83x. AWS and GCP rates differ: secondary pricing guides REPORT about $0.15/DBU jobs
and $0.55 all-purpose on AWS (eesel.ai, cloudforecast.io, 2026); databricks.com price tables load by script and could not be read.

## 6. Verified facts by source (with tier)

**Delta Lake transaction log protocol** (github.com/delta-io/delta, PROTOCOL.md at commit 52fc23eb, READ 2026-10-03):
- Log entries are JSON files in `_delta_log`, named by version zero-padded to 20 digits; newline-delimited, one action per line; "Delta files are the unit of atomicity for a table".
- Writers "optimistically write out new data files", then commit by adding a new log entry; "Writers MUST never overwrite an existing log entry."
- Snapshot = replay in ascending version: latest protocol wins, latest metaData wins, newest action per logical file `(path, deletionVector.uniqueId)` wins; `add` = present, `remove` = tombstone kept only for VACUUM.
- `add` fields: path, partitionValues, size, modificationTime, dataChange, stats (optional), tags, deletionVector, baseRowId, defaultRowCommitVersion, clusteringProvider.
- `dataChange: false` = the commit "only rearranges existing data or adds new statistics".
- Per-file statistics: numRecords, minValues, maxValues, nullCount, tightBounds; "These statistics can be used for eliminating files based on query predicates". String stats cut to a prefix; timestamps truncated to milliseconds.
- Checkpoints contain "the complete replay of all actions" up to a version; readers should prefer the newest checkpoint; "For time travel, the checkpoint used must not be newer than the time travel version"; readers "SHOULD NOT make any assumptions about the existence or frequency of checkpoints". `_last_checkpoint` points at the newest.
- VACUUM deletes unreferenced files "after a user-specified retention period (default 7 days)".
- Change data files in `_change_data`, `_change_type` values insert, update_preimage, update_postimage, delete; `cdc` actions have dataChange false; checkpoints never keep cdc or commitInfo.
- Clustered tables: writer feature `clustering`, clustering columns recorded in `domainMetadata` domain `delta.clustering`, `clusteringProvider` e.g. "liquid" on clustered files; cannot be both clustered and partitioned.

**Armbrust, Ghodsi, Xin, Zaharia. "Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics." CIDR 2021** (READ, cidrdb.org PDF):
- Lakehouse = "a data management system based on low-cost and directly-accessible storage that also provides traditional analytical DBMS management and performance features such as ACID transactions, data versioning, auditing, indexing, caching, and query optimization".
- Three generations: warehouse; two-tier data lake + warehouse ("used at virtually all Fortune 500 enterprises" in the authors' experience); lakehouse.
- Four problems of two-tier: reliability, data staleness, limited support for advanced analytics, total cost of ownership (double storage, lock-in).
- Staleness survey: "86% of analysts use out-of-date data and 62% report waiting on engineering resources numerous times per month" (Dimensional Research and Fivetran survey cited by the paper: REPORTED, the survey itself was not read).
- Delta Lake "is now used in about half of Databricks' workload" (authors' claim).
- Three performance ideas: caching, auxiliary data (min-max statistics "which enables data skipping optimizations when the base data is clustered"), data layout (Z-order, Hilbert curves).
- TPC-DS at scale factor 30,000, 960 vCPUs each: Delta Engine 3,302 s / $104 on-demand, 3,252 s / $56 spot; four unnamed cloud warehouses 2,996 to 37,283 s and $153 to $570. A VENDOR benchmark by the platform's authors; pages must say so. Footnote: all systems started with data cached on SSD where applicable; "Delta Engine was only 18% slower when starting with a cold cache".
- Open questions the authors name: the log in the object store limits transactions per second; Delta, Iceberg and Hudi transact on one table at a time.

**Armbrust et al. "Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores." PVLDB 13(12), 2020** (READ, vldb.org PDF):
- "By default, our clients write checkpoints every 10 transactions" (the 2020 reference client; delta-rs 1.6.6 did not auto-checkpoint in 33 commits in this build).
- Read protocol: read `_last_checkpoint`, LIST after it, replay checkpoint + later records.
- Z-order (Figure 5, 100 Parquet objects, 4 uniformly random fields): a global sort skips 99% for sourceIP and 0% for the other three; Z-order by all four skips 67%, 60%, 47%, 44% (at least 43% per dimension, 54% on average vs 25% for the single sort). A 500 TB network-traffic table Z-ordered on several fields skipped 93% (customer case, as reported by the authors).
- Metadata: a 1-million-partition table listed in 108 s with Delta, 17 s with the log cached; Hive over an hour at 10,000 partitions.

**Databricks docs** (docs.databricks.com/aws/en/..., READ 2026-10-03; "last updated" dates as shown on each page):
- Data skipping (Sep 11, 2026): per-file min, max, null counts, total records; stats on "the first 32 columns" by default for Unity Catalog external tables; managed tables use predictive optimization; `delta.dataSkippingNumIndexedCols`, `delta.dataSkippingStatsColumns` (DBR 13.3 LTS+); "Long strings are truncated".
- Liquid clustering (Sep 25, 2026): "Databricks recommends liquid clustering for all new tables, including streaming tables and materialized views"; replaces partitioning and ZORDER; `CLUSTER BY (col)`, `ALTER TABLE ... CLUSTER BY`; `CLUSTER BY AUTO` (UC managed, DBR 15.4 LTS+); `OPTIMIZE` clusters incrementally, `OPTIMIZE ... FULL` reclusters all (DBR 16.4 LTS+); at most four clustering keys; not compatible with partitioning or ZORDER.
- OPTIMIZE (Sep 11, 2026): bin-packing is idempotent; "Databricks recommends using liquid clustering instead of partitions, ZORDER, or other data layout approaches"; predictive optimization runs OPTIMIZE on UC managed tables.
- History and time travel (Sep 11, 2026): `DESCRIBE HISTORY`; `VERSION AS OF`, `TIMESTAMP AS OF`, `@v123`; `delta.logRetentionDuration` default 30 days; `delta.deletedFileRetentionDuration` default 7 days; RESTORE is "a data-changing operation" (dataChange true) so streaming readers may reprocess.
- VACUUM (Sep 11, 2026): default retention 7 days; `spark.databricks.delta.retentionDurationCheck.enabled` safety check; DRY RUN lists up to 1,000 files; LITE (log-driven) vs FULL (default); "you lose the ability to time travel back to a version older than the specified data retention period".
- MERGE (Sep 11, 2026): WHEN MATCHED / WHEN NOT MATCHED / WHEN NOT MATCHED BY SOURCE; "A merge operation can fail if multiple rows of the source dataset match and the merge attempts to update the same rows of the target"; deduplicate the source first.
- Change data feed (Sep 16, 2026): `delta.enableChangeDataFeed = true`; not on by default; records only changes after enabling; `_change_type`, `_commit_version`, `_commit_timestamp`; `table_changes('t', 0, 10)`; VACUUM deletes change data files.
- Unity Catalog privileges (Sep 25, 2026): `catalog.schema.table`; reading needs SELECT on the table, USE CATALOG on its catalog, USE SCHEMA on its schema; privileges on a catalog or schema apply to "all current and future objects" inside; MANAGE lets a non-owner manage privileges, transfer ownership, rename, drop; ALL PRIVILEGES excludes EXTERNAL USE SCHEMA, EXTERNAL USE LOCATION, MANAGE, READ METADATA; metastore admins oversee the metastore.
- Models in Unity Catalog (Sep 11, 2026): `<catalog>.<schema>.<model>`; `mlflow.set_registry_uri("databricks-uc")` is the default in MLflow 3; "stages are not supported" - use aliases (`@Champion`); CREATE MODEL + USE SCHEMA to create, EXECUTE to load, CREATE MODEL VERSION to add versions; load `models:/cat.sch.model@Champion`.
- MLflow (Sep 15, 2026): Databricks-managed MLflow; MLflow 3 covers agents/LLMs and classic ML; experiment tracking of parameters, metrics, artifacts, code versions.
- DESCRIBE DETAIL ("Review Delta Lake table details", Sep 11, 2026): one row with format, id, name, description, location, createdAt, lastModified, partitionColumns, numFiles ("Number of files in the latest version of the table"), sizeInBytes, properties, minReaderVersion, minWriterVersion, statistics, tableFeatures, clusteringColumns.
- Compute (Sep 11, 2026): serverless for notebooks, serverless for jobs, classic, SQL warehouses; serverless "run in the serverless compute plane, which is managed by Databricks"; "For most new workloads, Databricks recommends using serverless compute" (classic config best practices page).
- Lakeflow Jobs (Sep 11, 2026): jobs coordinate tasks as a DAG; triggers time-based or event-based; a job holds up to 1,000 tasks; a workspace runs up to 2,000 concurrent task runs; 12,000 saved jobs.
- Free Edition (limitations page Sep 29, 2026; overview Sep 11, 2026): replaced Community Edition (retired 2025); serverless only, no custom compute; one SQL warehouse limited to 2X-Small; max 5 concurrent job tasks per account; outbound internet limited to trusted domains; one active pipeline per type; no GPU model serving; up to 3 apps; one workspace and one metastore per account; non-commercial use only; no SLA; quota overrun shuts compute "for the rest of the day (and in extreme cases, the rest of the month)"; R and Scala unsupported. "perpetually free" (databricks.com/learn/free-edition). No credit card at sign-up: REPORTED (Phoebe's account; no page read states it).
- DBU definition: "A Databricks Unit (DBU) is a normalized unit of processing power ... used for measurement and pricing purposes"; "per second granularity" (databricks.com/product/pricing, READ). Azure: "Azure Databricks bills you for virtual machines (VMs) provisioned in clusters and Databricks Units (DBUs) based on the VM instance selected. A DBU is a unit of processing capability, billed on a per-second usage." (azure.microsoft.com pricing page, READ). Photon raises the DBU count (Azure page: DS3 v2 1.50 all-purpose Photon, 1.88 jobs Photon).

## 7. Per-session coverage

### Leader (no code; Free Edition clicks optional, never required)
- **a1 What a lakehouse is** · the three generations and the two-tier pain (CIDR paper); the definition; metadata layer over open files in an object store; one copy read by BI and ML. Real-world: the paper's two-tier pipeline (ETL into lake, ELT again into warehouse). Build-along: draw your own data path, count copies and hops (paper Figure 1 shapes). Figures: three-generation stack; the metadata layer over files; the copy-count map.
- **a2 Delta: a table that remembers** · the log as a numbered list of commits; versions and time travel; DESCRIBE HISTORY as audit; retention defaults 30 / 7 days; VACUUM ends time travel; RESTORE is a new commit. Real numbers from the bench (34 versions, the DELETE of 113 voided trips rewrote 30 of 31 files). Build-along: write your table's retention policy and the "who can VACUUM" rule.
- **a3 Unity Catalog governance** · three-level namespace; the three-key read rule; inheritance including future objects; ownership and MANAGE; models governed in the same tree. Seam: concepts of RBAC/ABAC, RLS, masking live in learn-data-access-control. Build-along: catalog layout and a grant matrix for three teams.
- **a4 Notebooks vs jobs** · interactive vs automated work; compute types; Lakeflow Jobs (tasks, DAG, triggers, limits); all-purpose vs jobs DBU rate (0.55 vs 0.30); serverless recommendation; Free Edition 5 concurrent job tasks. Seam: scheduling, retries, backfills in learn-data-orchestration. Build-along: promote-a-notebook checklist.
- **a5 What DBUs cost** · DBU definition; the two bills (classic: VMs + DBUs); the arithmetic above; warehouse sizes; idle cost; Photon raises DBU count; Free Edition quota. Seam: the cloud bill itself in learn-aws-with-phoebe. Build-along: one-page monthly estimate from your own workload list.
- **a6 Lakehouse or warehouse?** · the paper's case and its own open questions; the vendor benchmark read honestly; Delta paper results; decision tree. Seam: dimensional modelling and warehouse internals in learn-data-warehouse. Build-along: a decision memo.

### Analyst (local path always; Free Edition path labelled)
- **b1 Delta tables by hand** · b1.py; Free Edition: notebook `CREATE TABLE ... AS SELECT` / `df.write.saveAsTable`, `DESCRIBE DETAIL`.
- **b2 The transaction log** · b2.py; action types; reconciliation; checkpoints and `_last_checkpoint`; stats live in the log.
- **b3 Time travel and restore** · b3.py; history; VERSION AS OF; RESTORE; VACUUM and retention.
- **b4 MERGE and change data** · b4.py; upsert, conditional delete; CDF; duplicate-source refusal; the NULL-flag trap. Seam: streaming CDC in learn-streaming-data; pipelines in learn-data-engineering.
- **b5 Data skipping, OPTIMIZE and clustering** · b5.py; per-file stats; Z-order; liquid clustering recommended for new tables (Databricks only path: `CLUSTER BY`); Delta paper Figure 5.
- **b6 Unity Catalog grants** · b6.py model + real SQL (`GRANT ... ON CATALOG/SCHEMA/TABLE`, `SHOW GRANTS`); Free Edition path: run the SQL on your own catalog.
- **b7 MLflow on Databricks** · b7.py; on Databricks: tracking is built in, models registered as `catalog.schema.model`, aliases not stages, EXECUTE to load. Seam: MLOps tooling in general in learn-dataops.
- **b8 The Delta log bench** · section 3.

## 8. Seams (link, never teach)
| Topic | Owner |
|---|---|
| Warehouse modelling, star schemas, SCD | https://phoebefu6.github.io/learn-data-warehouse-with-phoebe/ |
| Pipelines and ingestion | https://phoebefu6.github.io/learn-data-engineering-with-phoebe/ |
| Orchestration: schedules, retries, backfills | https://phoebefu6.github.io/learn-data-orchestration-with-phoebe/ |
| Streaming | https://phoebefu6.github.io/learn-streaming-data-with-phoebe/ |
| Access-control concepts (RBAC, RLS, masking) | https://phoebefu6.github.io/learn-data-access-control-with-phoebe/ |
| MLOps tooling in general | https://phoebefu6.github.io/learn-dataops-with-phoebe/ |
| AWS services and the cloud bill | https://phoebefu6.github.io/learn-aws-with-phoebe/ (sibling built in parallel) |
| The generic lakehouse thesis across vendors | https://phoebefu6.github.io/learn-ai-infra-with-phoebe/ (b5) |

## 9. Not covered (honest list)
Photon internals; Delta Live Tables / Lakeflow Declarative Pipelines; Auto Loader; Structured Streaming; Databricks SQL dashboards and Genie;
Mosaic AI model serving, vector search and agents; Delta Sharing; Iceberg and UniForm interoperability; deletion vectors in depth
(delta-rs 1.6.6 wrote none in this build); row tracking; Unity Catalog lineage and audit system tables; row filters and column masks
(concepts in learn-data-access-control); account console, SCIM, networking; certification exams (official Databricks Academy).
Liquid clustering is taught but cannot be run locally: delta-rs 1.6.6 offers Z-order, not CLUSTER BY.

## 10. Open issue found in a sibling (not fixed here)
`learn-ai-infra-with-phoebe/courses/b5-lakehouse-engine.html` lists the CIDR 2021 authors as "Zaharia, Ghodsi, Xin and Armbrust"; the paper's
order is Armbrust, Ghodsi, Xin, Zaharia.

## 11. Citation appendix (form pages use)
- Delta Lake. "Delta Transaction Log Protocol" (PROTOCOL.md). github.com/delta-io/delta, read 3 October 2026.
- Armbrust, M., Ghodsi, A., Xin, R., Zaharia, M. (2021). "Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics." CIDR 2021.
- Armbrust, M., Das, T., Sun, L., et al. (2020). "Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores." PVLDB 13(12): 3411-3424.
- Databricks documentation, docs.databricks.com (pages named in section 6), read 3 October 2026.
- Databricks, "Pricing" (databricks.com/product/pricing) and Microsoft, "Azure Databricks pricing" + Azure retail prices API, read 3 October 2026.
- NYC Taxi and Limousine Commission, "TLC Trip Record Data", yellow taxi trips January 2024.
- delta-rs (`deltalake` 1.6.6), DuckDB 1.5.6, MLflow 3.16.1 as installed.

## 12. Palette (checked 2026-10-03)
Lava red `#E00F00` (Databricks `#FF3621` family, deepened: white text 4.96:1) · deep `#9E0B00` · mid `#B80C00` · soft `#FFB4A9` · tint `#FFF5F3` ·
navy ink `#1B3139` · muted `#4D6169` · faint `#C4CFD3` · hairline `#E2E8EA` · amber `#FFAB00` with ink `#4D3200` · amber tint `#FFF5DC` · paper `#FCFAF7`.
CIELAB distance (CIE76) of `#E00F00` to every `--indigo` in github_repo/learn-*/assets/style.css: nearest learn-anomaly-detection `#DC2626` at 14.9,
then learn-html `#E34F26` 19.0; to the AWS sibling's `--indigo` `#183177` and its orange family well above 20. All >= 12.
Text pairs checked before authoring (all >= 4.5): white on lava 4.96, deep 8.39, mid 6.79; lava on white 4.96, on tint 4.63; ink on soft 8.00, on amber 7.17;
amber ink on amber 6.25; muted on white 6.50, on tint 6.07. White on amber fails (1.90): never used. Painted contrast measured on every page with
a Playwright walk over all HTML text and SVG text (tested against a known-bad page first).
