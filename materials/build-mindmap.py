"""Inject the landing knowledge map data with json.dumps (never string interpolation)."""
import json, re, sys
C = "courses/"
S = [
 ("Lakehouse", "a1-what-a-lakehouse-is.html", ["Three generations", "The metadata layer", "Open questions"]),
 ("Remembers", "a2-a-table-that-remembers.html", ["Versions and history", "Retention defaults"]),
 ("Unity Catalog", "a3-unity-catalog-governance.html", ["Three keys to read", "Inheritance"]),
 ("Notebooks, jobs", "a4-notebooks-vs-jobs.html", ["Compute types", "Promote a notebook"]),
 ("DBUs", "a5-what-dbus-cost.html", ["Two bills", "Idle is expensive"]),
 ("Decision", "a6-lakehouse-or-warehouse.html", ["Vendor benchmarks", "Decision tree"]),
 ("By hand", "b1-delta-tables-by-hand.html", ["Folder plus log", "Schema enforcement"]),
 ("The log", "b2-the-transaction-log.html", ["Add and remove", "Checkpoints"]),
 ("Time travel", "b3-time-travel-and-restore.html", ["RESTORE commits", "VACUUM ends history"]),
 ("MERGE, CDF", "b4-merge-and-change-data.html", ["Upsert in one commit", "Change data feed"]),
 ("Skipping", "b5-data-skipping-and-clustering.html", ["Min/max per file", "Liquid clustering"]),
 ("Grants", "b6-unity-catalog-grants.html", ["GRANT on securables"]),
 ("MLflow", "b7-mlflow-on-databricks.html", ["Aliases, not stages"]),
 ("The bench", "b8-the-delta-log-bench.html", ["Replay the log", "Break the stats"]),
]
data = {"title": "Databricks\nLakehouse", "centerColor": "#9E0B00",
        "sessions": [{"label": l, "href": C + f, "concepts": [{"label": c, "href": C + f} for c in cs]} for l, f, cs in S]}
p = sys.argv[1]
s = open(p).read()
new = "window.MINDMAP_DATA = " + json.dumps(data, indent=2, ensure_ascii=False) + ";"
s = re.sub(r'window\.MINDMAP_DATA = .*?;\n</script>', lambda m: new + "\n</script>", s, count=1, flags=re.S)
open(p, "w").write(s)
print("sessions", len(S), "concepts", sum(len(x[2]) for x in S))
