# Analyst session 4: MERGE a change feed, then read the change data feed (no account needed)
import shutil
import duckdb, pyarrow as pa, pyarrow.compute as pc
from deltalake import write_deltalake, DeltaTable

shutil.rmtree("trips_cdf", ignore_errors=True)
base = duckdb.sql("""
  SELECT row_number() OVER (ORDER BY tpep_pickup_datetime, tpep_dropoff_datetime, PULocationID,
                            DOLocationID, fare_amount, trip_distance, VendorID, tip_amount) AS trip_id,
         tpep_pickup_datetime AS pickup_ts, PULocationID AS pu_zone, fare_amount, tip_amount,
         store_and_fwd_flag AS store_and_fwd
  FROM 'yellow_tripdata_2024-01.parquet'
  WHERE tpep_pickup_datetime >= TIMESTAMP '2024-01-15' AND tpep_pickup_datetime < TIMESTAMP '2024-01-16'
""").arrow().read_all()
late = base.filter(pc.equal(base["store_and_fwd"], "Y"))          # sent late by the cab: real
ontime = base.filter(pc.invert(pc.fill_null(pc.equal(base["store_and_fwd"], "Y"), False)))  # null flag = on time
write_deltalake("trips_cdf", ontime, configuration={"delta.enableChangeDataFeed": "true"})
print("loaded:", ontime.num_rows, "trips; held back as late:", late.num_rows)

# the change feed (constructed on real rows): 5 tip corrections, 3 cancellations, the late trips
fix = ontime.slice(100, 5).to_pylist()
for r in fix:
    r["tip_amount"] = round(r["tip_amount"] + 1.0, 2); r["op"] = "U"
cancel = ontime.slice(200, 3).to_pylist()
for r in cancel:
    r["op"] = "D"
ins = late.to_pylist()
for r in ins:
    r["op"] = "I"
feed = pa.Table.from_pylist(fix + cancel + ins)

m = (DeltaTable("trips_cdf").merge(feed, "t.trip_id = s.trip_id", source_alias="s", target_alias="t")
     .when_matched_delete(predicate="s.op = 'D'")
     .when_matched_update(updates={"tip_amount": "s.tip_amount"}, predicate="s.op = 'U'")
     .when_not_matched_insert_all(predicate="s.op = 'I'")
     .execute())
print("merge:", {k: m[k] for k in ("num_target_rows_inserted", "num_target_rows_updated", "num_target_rows_deleted")})

cdf = pa.table(DeltaTable("trips_cdf").load_cdf(starting_version=1))
print("change rows by type:", duckdb.sql("SELECT _change_type, count(*) n FROM cdf GROUP BY 1 ORDER BY 1").fetchall())

# a source with two rows for one target row is refused, not guessed at
dup = pa.Table.from_pylist([dict(fix[0]), dict(fix[0], tip_amount=99.0)])
try:
    (DeltaTable("trips_cdf").merge(dup, "t.trip_id = s.trip_id", source_alias="s", target_alias="t")
     .when_matched_update(updates={"tip_amount": "s.tip_amount"}).execute())
    print("duplicate source merged without error")
except Exception as e:
    print("duplicate source refused:", type(e).__name__)
print("version now:", DeltaTable("trips_cdf").version())
