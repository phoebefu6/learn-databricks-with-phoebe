# Analyst session 1: a Delta table by hand, no account needed
import os, shutil
import duckdb, polars as pl
from deltalake import write_deltalake, DeltaTable

shutil.rmtree("trips_delta", ignore_errors=True)
SQL = """
SELECT VendorID AS vendor_id, tpep_pickup_datetime AS pickup_ts,
       PULocationID AS pu_zone, DOLocationID AS do_zone,
       trip_distance, fare_amount, tip_amount, payment_type
FROM 'yellow_tripdata_2024-01.parquet'
WHERE tpep_pickup_datetime >= TIMESTAMP '{a}'
  AND tpep_pickup_datetime <  TIMESTAMP '{b}'
"""
morning = duckdb.sql(SQL.format(a="2024-01-15 00:00", b="2024-01-15 12:00")).arrow().read_all()
evening = duckdb.sql(SQL.format(a="2024-01-15 12:00", b="2024-01-16 00:00")).arrow().read_all()
print("morning rows:", morning.num_rows, " afternoon and evening rows:", evening.num_rows)

write_deltalake("trips_delta", morning)                  # creates the table: version 0
write_deltalake("trips_delta", evening, mode="append")   # version 1

dt = DeltaTable("trips_delta")
print("version:", dt.version())
print("data files:", len(dt.file_uris()))
print(sorted(os.listdir("trips_delta/_delta_log")))

# three engines, one table, no copy
print("DuckDB rows:", duckdb.sql("INSTALL delta; LOAD delta; SELECT count(*) FROM delta_scan('trips_delta')").fetchone()[0])
print("polars rows:", pl.read_delta("trips_delta").height)
print("pandas rows:", len(dt.to_pandas()))

# schema enforcement: a wrong type is refused, nothing is written
bad = pl.DataFrame({"vendor_id": [1], "fare_amount": ["twelve dollars"]}).to_arrow()
try:
    write_deltalake("trips_delta", bad, mode="append")
except Exception as e:
    print("refused:", type(e).__name__)
print("version after the refused write:", DeltaTable("trips_delta").version())
