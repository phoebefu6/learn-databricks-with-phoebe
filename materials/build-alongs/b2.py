# Analyst session 2: read the transaction log yourself (run b1.py first)
import json, glob, os
from deltalake import DeltaTable

LOG = "trips_delta/_delta_log"
for f in sorted(glob.glob(LOG + "/*.json")):
    kinds = [list(json.loads(line))[0] for line in open(f)]
    print(os.path.basename(f), kinds)

# one more commit, so the log holds a remove: drop the voided trips
dt = DeltaTable("trips_delta")
m = dt.delete("fare_amount < 0")
print("deleted rows:", m["num_deleted_rows"], "| files removed:", m["num_removed_files"], "| files added:", m["num_added_files"])

def replay(path, upto=None):
    """Rebuild the live file set the way PROTOCOL.md says: newest action per path wins."""
    live = {}
    for f in sorted(glob.glob(path + "/_delta_log/*.json")):
        v = int(os.path.basename(f).split(".")[0])
        if upto is not None and v > upto:
            break
        for line in open(f):
            a = json.loads(line)
            if "add" in a:
                live[a["add"]["path"]] = json.loads(a["add"]["stats"])
            elif "remove" in a:
                live.pop(a["remove"]["path"], None)
    return live

for v in range(DeltaTable("trips_delta").version() + 1):
    mine = replay("trips_delta", v)
    theirs = {os.path.basename(u) for u in DeltaTable("trips_delta", version=v).file_uris()}
    rows = sum(s["numRecords"] for s in mine.values())
    print(f"v{v}: my replay {len(mine)} files, {rows} rows | delta-rs agrees: {set(mine) == theirs}")

DeltaTable("trips_delta").create_checkpoint()
print(sorted(os.listdir(LOG)))
print(open(LOG + "/_last_checkpoint").read())
