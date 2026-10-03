# Analyst session 5: data skipping before and after OPTIMIZE and Z-order (no account needed)
import json, shutil
import duckdb, pyarrow as pa
from deltalake import write_deltalake, DeltaTable

shutil.rmtree("trips_month", ignore_errors=True)
for d in range(1, 32):                     # one append per day: 31 small files
    day = duckdb.sql(f"""
      SELECT tpep_pickup_datetime AS pickup_ts, VendorID AS vendor_id, PULocationID AS pu_zone,
             trip_distance, fare_amount
      FROM 'yellow_tripdata_2024-01.parquet'
      WHERE tpep_pickup_datetime >= TIMESTAMP '2024-01-{d:02d}'
        AND tpep_pickup_datetime <  TIMESTAMP '2024-01-{d:02d}' + INTERVAL 1 DAY
    """).arrow().read_all()
    write_deltalake("trips_month", day, mode="append")

def files_read(path, col, lo, hi):
    """Data skipping by hand: read a file only if [min, max] can overlap [lo, hi]."""
    acts = pa.table(DeltaTable(path).get_add_actions(flatten=True)).to_pylist()
    read = [a for a in acts if not (a[f"max.{col}"] < lo or a[f"min.{col}"] > hi)]
    return len(read), len(acts), sum(a["size_bytes"] for a in read), sum(a["size_bytes"] for a in acts)

def report(tag):
    j = files_read("trips_month", "pu_zone", 132, 132)
    import datetime as dt
    d = files_read("trips_month", "pickup_ts", dt.datetime(2024, 1, 15), dt.datetime(2024, 1, 15, 23, 59, 59))
    print(f"{tag:22s} JFK: {j[0]}/{j[1]} files, {100*j[2]/j[3]:.1f}% of bytes | 15 Jan: {d[0]}/{d[1]} files, {100*d[2]/d[3]:.1f}% of bytes")

print("rows:", DeltaTable("trips_month").count() if hasattr(DeltaTable, "count") else "")
report("31 daily appends")
DeltaTable("trips_month").optimize.compact(target_size=4 * 1024 * 1024)
report("OPTIMIZE (compact)")
DeltaTable("trips_month").optimize.z_order(["pu_zone"], target_size=4 * 1024 * 1024)
report("ZORDER BY (pu_zone)")
print("JFK trips:", duckdb.sql("INSTALL delta; LOAD delta; SELECT count(*) FROM delta_scan('trips_month') WHERE pu_zone = 132").fetchone()[0])
