"""Build the Delta log bench for learn-databricks-with-phoebe (analyst session 8).

Real rows: NYC TLC yellow taxi trip records, January 2024
  https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
  (public, no login; NYC Taxi and Limousine Commission, "TLC Trip Record Data" page)

A seeded sample of N real trips goes through a declared commit sequence, written by the
open-source `deltalake` (delta-rs) package:
  v0..v30  one append per pickup day (the first creates the table, change data feed on)
           store-and-forward trips (store_and_fwd = 'Y': held in the cab's memory, sent late)
           are held back from the daily loads
  v31      MERGE on trip_id: the held-back late trips are inserted, and a re-sent copy of every
           12 January trip is matched and updated (the re-send is constructed: an uploader retry)
  v32      DELETE WHERE fare_amount < 0 (real voided or refunded trips)
           a checkpoint is written at v32
  v33      OPTIMIZE (bin-packing compaction)
  then two branches copied from v33, each with its own v34:
     zone:    OPTIMIZE ZORDER BY (pu_zone)       the column the preset queries filter on
     vendor:  OPTIMIZE ZORDER BY (vendor_id)     the anti-lever: no query filters on vendor
              v35 RESTORE TABLE TO VERSION 33

File sizes are scaled down with the table (TARGET bytes per file, set as delta.targetFileSize
and as the OPTIMIZE target) so that 8,000 rows make a realistic number of files.

Outputs:
  argv[1]  work dir (scratch; the tables are written here, never into the repo)
  argv[2]  JS file for the browser (json.dumps, never string interpolation)
  argv[3]  reference JSON: delta-rs's own live-file list per version + the Python skipping run
"""
import json, os, random, shutil, sys, glob
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
from deltalake import write_deltalake, DeltaTable

WORK, JS_OUT, REF_OUT = sys.argv[1], sys.argv[2], sys.argv[3]
SRC = os.path.join(WORK, "src", "yellow_2024-01.parquet")
N = int(os.environ.get("DBX_N", 8000))
TARGET = int(os.environ.get("DBX_TARGET", 28 * 1024))
SEED = 20240101
RESEND_DAY = 12
SHUFFLE_SEED = 7

# ---------- 1. the seeded sample of real rows ----------
con = duckdb.connect()
full = con.sql(f"""
  SELECT tpep_pickup_datetime AS pickup_ts, VendorID AS vendor_id, PULocationID AS pu_zone,
         DOLocationID AS do_zone, passenger_count, trip_distance, fare_amount, tip_amount,
         payment_type, store_and_fwd_flag AS store_and_fwd, tpep_dropoff_datetime AS d
  FROM '{SRC}'
  WHERE tpep_pickup_datetime >= TIMESTAMP '2024-01-01' AND tpep_pickup_datetime < TIMESTAMP '2024-02-01'
  ORDER BY pickup_ts, d, pu_zone, do_zone, fare_amount, trip_distance, vendor_id, tip_amount
""").fetchall()
idx = sorted(random.Random(SEED).sample(range(len(full)), N))
rows = []
for i, k in enumerate(idx):
    r = full[k]
    rows.append({"trip_id": i + 1, "pickup_ts": r[0], "vendor_id": r[1], "pu_zone": r[2],
                 "do_zone": r[3], "passenger_count": r[4], "trip_distance": r[5],
                 "fare_amount": r[6], "tip_amount": r[7], "payment_type": r[8],
                 "store_and_fwd": r[9]})
SCHEMA = pa.schema([("trip_id", pa.int64()), ("pickup_ts", pa.timestamp("us")),
                    ("vendor_id", pa.int32()), ("pu_zone", pa.int32()), ("do_zone", pa.int32()),
                    ("passenger_count", pa.int64()), ("trip_distance", pa.float64()),
                    ("fare_amount", pa.float64()), ("tip_amount", pa.float64()),
                    ("payment_type", pa.int64()), ("store_and_fwd", pa.string())])

def tbl(rs):
    return pa.Table.from_pylist(rs, schema=SCHEMA)

late = [r for r in rows if r["store_and_fwd"] == "Y"]
ontime = [r for r in rows if r["store_and_fwd"] != "Y"]

# ---------- 2. the declared commit sequence ----------
base = os.path.join(WORK, "bench_tables")
shutil.rmtree(base, ignore_errors=True)
os.makedirs(base)
main = os.path.join(base, "trips_main")
CFG = {"delta.enableChangeDataFeed": "true", "delta.targetFileSize": str(TARGET)}
steps = []
for d in range(1, 32):
    day = [r for r in ontime if r["pickup_ts"].day == d]
    write_deltalake(main, tbl(day), mode="append", configuration=CFG if d == 1 else None)
    steps.append({"op": "WRITE", "label": f"Append 2024-01-{d:02d}", "rows": len(day)})

resend = [r for r in ontime if r["pickup_ts"].day == RESEND_DAY]
m = (DeltaTable(main).merge(tbl(late + resend), "t.trip_id = s.trip_id", source_alias="s", target_alias="t")
     .when_matched_update_all().when_not_matched_insert_all().execute())
steps.append({"op": "MERGE", "label": "Late trips in, a re-sent day matched",
              "rows": len(late) + len(resend), "late": len(late), "resent": len(resend),
              "inserted": m.get("num_target_rows_inserted"), "updated": m.get("num_target_rows_updated"),
              "filesAdded": m.get("num_target_files_added"), "filesRemoved": m.get("num_target_files_removed")})
dm = DeltaTable(main).delete("fare_amount < 0")
steps.append({"op": "DELETE", "label": "Delete voided trips (fare below 0)",
              "deleted": dm.get("num_deleted_rows"), "filesAdded": dm.get("num_added_files"),
              "filesRemoved": dm.get("num_removed_files")})
DeltaTable(main).create_checkpoint()
CKPT_VERSION = DeltaTable(main).version()
om = DeltaTable(main).optimize.compact(target_size=TARGET)
steps.append({"op": "OPTIMIZE", "label": "Compact small files",
              "filesAdded": om.get("numFilesAdded"), "filesRemoved": om.get("numFilesRemoved")})
BASE_V = DeltaTable(main).version()
assert BASE_V == 33, BASE_V

branches = {"zone": ["pu_zone"], "vendor": ["vendor_id"]}
branch_steps = {}
for name, cols in branches.items():
    p = os.path.join(base, "trips_" + name)
    shutil.copytree(main, p)
    zm = DeltaTable(p).optimize.z_order(cols, target_size=TARGET)
    branch_steps[name] = [{"op": "OPTIMIZE ZORDER", "label": "Z-order by " + ", ".join(cols),
                           "filesAdded": zm.get("numFilesAdded"), "filesRemoved": zm.get("numFilesRemoved")}]
    if name == "vendor":
        DeltaTable(p).restore(BASE_V)
        branch_steps[name].append({"op": "RESTORE", "label": f"Restore to version {BASE_V}"})

# ---------- 3. read the log exactly as written ----------
def read_log(p):
    out = {}
    for f in sorted(glob.glob(os.path.join(p, "_delta_log", "*.json"))):
        v = int(os.path.basename(f).split(".")[0])
        out[v] = [json.loads(line) for line in open(f) if line.strip()]
    return out

def slim(action):
    """Every field the replay and the pages use is kept; only the long schemaString is shortened."""
    a = json.loads(json.dumps(action))
    if "metaData" in a:
        a["metaData"]["schemaString"] = "(the table schema: 11 columns)"
    return a

logs = {"main": read_log(main)}
for name in branches:
    full_log = read_log(os.path.join(base, "trips_" + name))
    logs[name] = {v: acts for v, acts in full_log.items() if v > BASE_V}

ck_file = glob.glob(os.path.join(main, "_delta_log", f"{CKPT_VERSION:020d}.checkpoint*.parquet"))[0]
ck_slim = []
for r in pq.read_table(ck_file).to_pylist():
    if r.get("add"):
        a = r["add"]
        ck_slim.append({"add": {"path": a["path"], "size": a["size"], "dataChange": a.get("dataChange"),
                                "stats": a.get("stats")}})
    elif r.get("remove"):
        ck_slim.append({"remove": {"path": r["remove"]["path"],
                                   "deletionTimestamp": r["remove"].get("deletionTimestamp")}})
    elif r.get("protocol"):
        ck_slim.append({"protocol": {k: v for k, v in r["protocol"].items() if v is not None}})
    elif r.get("metaData"):
        ck_slim.append({"metaData": {"id": r["metaData"]["id"]}})

# ---------- 4. row data: one row per trip_id, and the trips inside every data file ever written ----------
def minute_of_jan(ts):
    return (ts.day - 1) * 1440 + ts.hour * 60 + ts.minute

def rowkey(r):
    return (minute_of_jan(r["pickup_ts"]), r["pu_zone"], round(r["trip_distance"] * 100),
            round(r["fare_amount"] * 100))

by_id = {}
file_rows = {}
for p in [main] + [os.path.join(base, "trips_" + n) for n in branches]:
    for fpath in sorted(glob.glob(os.path.join(p, "*.parquet"))):
        fn = os.path.basename(fpath)
        if fn in file_rows:
            continue
        ids = []
        for r in pq.read_table(fpath).to_pylist():
            k = rowkey(r)
            assert by_id.setdefault(r["trip_id"], k) == k, "a trip_id with two different values"
            ids.append(r["trip_id"])
        file_rows[fn] = sorted(ids)
assert sorted(by_id) == list(range(1, N + 1))
pick = [by_id[i][0] for i in range(1, N + 1)]
assert pick == sorted(pick)

def delta_encode(xs):
    out, prev = [], 0
    for x in xs:
        out.append(x - prev)
        prev = x
    return out

# ---------- 5. Python reference: delta-rs's own live files + the skipping logic ----------
PRESETS = [
    {"id": "jfk", "label": "Picked up at JFK Airport (zone 132)",
     "conds": [{"col": "pu_zone", "op": "=", "a": 132}]},
    {"id": "day15", "label": "Picked up on 15 January",
     "conds": [{"col": "pickup_ts", "op": "between", "a": "2024-01-15 00:00", "b": "2024-01-15 23:59"}]},
    {"id": "long", "label": "Trips over 20 miles",
     "conds": [{"col": "trip_distance", "op": ">", "a": 20}]},
    {"id": "jfkwk", "label": "JFK pickups, 22 to 28 January",
     "conds": [{"col": "pu_zone", "op": "=", "a": 132},
               {"col": "pickup_ts", "op": "between", "a": "2024-01-22 00:00", "b": "2024-01-28 23:59"}]},
]

def mulberry32(seed):
    s = seed & 0xFFFFFFFF
    def nxt():
        nonlocal s
        s = (s + 0x6D2B79F5) & 0xFFFFFFFF
        t = s
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return nxt

def derangement(n, seed):
    """Fisher-Yates driven by mulberry32, re-drawn until no file keeps its own stats."""
    r = mulberry32(seed)
    while True:
        p = list(range(n))
        for i in range(n - 1, 0, -1):
            j = int(r() * (i + 1))
            p[i], p[j] = p[j], p[i]
        if n < 2 or all(p[i] != i for i in range(n)):
            return p

def ts_minute(s):
    day = int(s[8:10]); hh = int(s[11:13]); mm = int(s[14:16])
    return (day - 1) * 1440 + hh * 60 + mm

def to_num(col, v):
    return ts_minute(v) if col == "pickup_ts" else v

def file_may_match(stats, conds):
    for c in conds:
        col = c["col"]
        mn, mx = stats["minValues"].get(col), stats["maxValues"].get(col)
        if mn is None or mx is None:
            continue
        mn, mx = to_num(col, mn), to_num(col, mx)
        a = to_num(col, c["a"])
        if c["op"] == "=":
            ok = mn <= a <= mx
        elif c["op"] == ">":
            ok = mx > a
        elif c["op"] == "<":
            ok = mn < a
        else:
            ok = mx >= a and mn <= to_num(col, c["b"])
        if not ok:
            return False
    return True

COLI = {"pickup_ts": 0, "pu_zone": 1, "trip_distance": 2, "fare_amount": 3}

def row_matches(k, conds):
    for c in conds:
        v = k[COLI[c["col"]]]
        if c["col"] in ("trip_distance", "fare_amount"):
            a = round(c["a"] * 100)
            b = round(c["b"] * 100) if "b" in c else None
        else:
            a = to_num(c["col"], c["a"])
            b = to_num(c["col"], c["b"]) if "b" in c else None
        if c["op"] == "=":
            ok = v == a
        elif c["op"] == ">":
            ok = v > a
        elif c["op"] == "<":
            ok = v < a
        else:
            ok = a <= v <= b
        if not ok:
            return False
    return True

def stats_upto(bname, v):
    out = {}
    for vv in range(0, v + 1):
        src = logs["main"] if vv <= BASE_V else logs[bname]
        for a in src.get(vv, []):
            if "add" in a:
                out[a["add"]["path"]] = (json.loads(a["add"]["stats"]), a["add"]["size"])
    return out

ref = {"versions": {}, "presets": PRESETS, "N": N, "target": TARGET}
branch_dirs = {"main": main, "zone": os.path.join(base, "trips_zone"),
               "vendor": os.path.join(base, "trips_vendor")}
for bname, bdir in branch_dirs.items():
    last = DeltaTable(bdir).version()
    first = 0 if bname == "main" else BASE_V + 1
    for v in range(first, last + 1):
        d = DeltaTable(bdir, version=v)
        paths = sorted(pa.table(d.get_add_actions(flatten=False)).column("path").to_pylist())
        sb = stats_upto(bname, v)
        gt = [rowkey(r) for r in d.to_pyarrow_table().to_pylist()]
        perm = derangement(len(paths), SHUFFLE_SEED)
        q = {}
        for pr in PRESETS:
            truth = sum(1 for k in gt if row_matches(k, pr["conds"]))
            for mode in ("honest", "broken"):
                files = nbytes = found = 0
                for i, pth in enumerate(paths):
                    st = sb[pth][0] if mode == "honest" else sb[paths[perm[i]]][0]
                    if file_may_match(st, pr["conds"]):
                        files += 1
                        nbytes += sb[pth][1]
                        found += sum(1 for t in file_rows[pth] if row_matches(by_id[t], pr["conds"]))
                q[pr["id"] + ":" + mode] = {"files": files, "bytes": nbytes, "rows": found, "truth": truth}
        ref["versions"][f"{bname}:{v}"] = {"live": paths, "nfiles": len(paths), "rows": len(gt),
                                           "bytes": sum(sb[p][1] for p in paths), "q": q}

# ---------- 6. ship ----------
data = {
    "source": "NYC TLC yellow taxi trip records, January 2024",
    "sample": {"rows": N, "seed": SEED, "late": len(late), "resent": len(resend),
               "resendDay": RESEND_DAY, "targetBytes": TARGET},
    "baseVersion": BASE_V,
    "checkpointVersion": CKPT_VERSION,
    "steps": steps,
    "branchSteps": branch_steps,
    "branches": branches,
    "log": {b: {str(v): [slim(a) for a in acts] for v, acts in lg.items()} for b, lg in logs.items()},
    "checkpoint": ck_slim,
    "cols": {"pickupMinuteDelta": delta_encode(pick),
             "puZone": [by_id[i][1] for i in range(1, N + 1)],
             "distX100": [by_id[i][2] for i in range(1, N + 1)],
             "fareX100": [by_id[i][3] for i in range(1, N + 1)]},
    "fileTrips": {p: delta_encode(ids) for p, ids in file_rows.items()},
    "presets": PRESETS,
    "shuffleSeed": SHUFFLE_SEED,
}
with open(JS_OUT, "w") as f:
    f.write("/* Delta log bench data, learn-databricks-with-phoebe. Generated by "
            "materials/build-delta-bench.py with json.dumps from real NYC TLC trips. */\n")
    f.write("window.DBX_BENCH = " + json.dumps(data, separators=(",", ":")) + ";\n")
with open(REF_OUT, "w") as f:
    json.dump(ref, f, indent=1, sort_keys=True)
print("N", N, "target", TARGET, "late", len(late), "resent", len(resend), "base", BASE_V, "ckpt", CKPT_VERSION)
for s in steps[31:] + branch_steps["zone"] + branch_steps["vendor"]:
    print(json.dumps(s))
print("JS bytes", os.path.getsize(JS_OUT))
