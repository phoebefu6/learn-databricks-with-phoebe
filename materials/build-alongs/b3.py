# Analyst session 3: time travel, restore, and what VACUUM takes away (run b1.py and b2.py first)
import duckdb
from deltalake import DeltaTable

for v in range(DeltaTable("trips_delta").version() + 1):
    print(f"VERSION AS OF {v}:", len(DeltaTable("trips_delta", version=v).to_pyarrow_table()), "rows")

for h in DeltaTable("trips_delta").history():
    print("history:", h["version"], h["operation"], h.get("operationParameters", {}))

dt = DeltaTable("trips_delta")
dt.restore(1)                                   # undo the DELETE with a NEW commit
dt = DeltaTable("trips_delta")
print("after RESTORE: version", dt.version(), "rows", len(dt.to_pyarrow_table()))

# VACUUM: default retention protects recent files, so a dry run finds nothing to delete
print("vacuum dry run, default retention:", len(dt.vacuum()), "files")
# force retention to zero (never do this on a shared table): files no live version needs are deleted
gone = dt.vacuum(retention_hours=0, enforce_retention_duration=False, dry_run=False)
print("vacuum with retention 0 deleted:", len(gone), "files")
try:
    print(len(DeltaTable("trips_delta", version=2).to_pyarrow_table()))
except Exception as e:
    print("time travel to version 2 now fails:", type(e).__name__)
print("latest still reads:", duckdb.sql("INSTALL delta; LOAD delta; SELECT count(*) FROM delta_scan('trips_delta')").fetchone()[0], "rows")
