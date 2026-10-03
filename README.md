<!-- learn-with-phoebe hub banner -->
> ### 📚 Part of [**Learn with Phoebe**](https://phoebefu6.github.io/learn-with-phoebe/)
> The shelf of 138 free, hands-on courses on AI, data, and the craft around them. **[Browse every course ↗](https://phoebefu6.github.io/learn-with-phoebe/)**
<!-- /learn-with-phoebe hub banner -->

# Databricks: Lakehouse for Data & AI

Fourteen 45-minute sessions on Databricks and the lakehouse idea, by Phoebe Fu.

- **Leader track (6 sessions, no code):** what a lakehouse is, Delta tables that remember, Unity Catalog governance, notebooks versus jobs, what DBUs cost, and the lakehouse or warehouse decision.
- **Analyst track (8 sessions, Python):** Delta tables by hand, the transaction log, time travel and restore, MERGE and change data, data skipping and clustering, Unity Catalog grants, MLflow on Databricks, and the Delta log bench.

Every analyst build-along runs on a laptop with the open-source `deltalake` (delta-rs) package, DuckDB and polars, no account needed, and shows the same move in Databricks Free Edition. The data is the NYC Taxi and Limousine Commission's public yellow taxi trip file for January 2024.

The capstone bench replays a real `_delta_log`, written by delta-rs over 8,000 sampled trips in 37 commits, in the browser: time travel to any version, data skipping for your own predicate, two clustering choices, and a break button that shuffles the per-file statistics.

Open `index.html` to start. Static HTML, no build step.
