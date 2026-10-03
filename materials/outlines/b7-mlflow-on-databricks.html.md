# b7-mlflow-on-databricks.html · "Analyst session 7 of 8" · MLflow on Databricks
h1: `<span class="accent">MLflow</span> on Databricks` · 🟠 Hands-on · chips "Analysts, data scientists, ML engineers", "Laptop path needs no account"
Script: b7.py / b7.out.txt (MLflow 3.16.1, sqlite backend). Install line adds `mlflow==3.16.1 scikit-learn==1.9.1`. Output label on this page: "Output · laptop path, MLflow 3.16.1".
Win: two tracked runs, a registered model with the alias @champion loaded by alias, and the three things that change on Databricks: tracking is built in, models are named catalog.schema.model, and aliases replace stages.

Part 1 · covers tracking · "A run remembers what you tried" · 5 min live
- Figure (b7a): an experiment "taxi-tips" with two runs side by side: linear (MAE $1.387) and forest (MAE $1.331), each recording params, metrics, the logged model with its signature.
- Cards: (open, Live) experiment tracking logs "parameters, metrics, artifacts, and code versions" (docs); on Databricks the workspace is the tracking server, so set_tracking_uri is not needed (say: Databricks-managed MLflow, docs); laptop uses sqlite. (Live) the data: 61,260 card trips on 15 January with fare above 0, 75/25 split, seed 15; real data, real MAEs. (Self) MLflow 3 also covers agents and LLM evaluation (docs); out of scope here.

Part 2 · covers the registry and aliases · "Aliases, not stages" · 6 min live
- Figure (b7b): registered model taxi_tip_model with version 1 and an alias pointer @champion → version 1; the loader asks for models:/taxi_tip_model@champion and gets whatever the alias points to; on Databricks the name becomes catalog.schema.taxi_tip_model.
- Cards: (Live) models in Unity Catalog: `<catalog>.<schema>.<model>`; `mlflow.set_registry_uri("databricks-uc")` is the default in MLflow 3; "stages are not supported" - use aliases like @Champion; load by `models:/cat.sch.model@Champion` (docs). (Live) privileges: CREATE MODEL + USE SCHEMA to create, EXECUTE to load, CREATE MODEL VERSION to add versions (docs) - the session 6 grants govern models too. (Self) seam: MLOps tooling in general (CI, monitoring, feature stores) in learn-dataops (link).

Part 3 · covers what MLflow refused · "Two refusals worth keeping" · 4 min live
- Figure (b7c): two gates: (1) MLflow 3.16 saves sklearn models with skops and refused the random forest until `skops_trusted_types=["sklearn.tree._tree.Tree"]` was passed (vouch only for types you created); (2) the logged signature refused a prediction where pu_zone was int64 against the logged int32 ("Can not safely convert int64 to int32"), fixed by predicting on a real test row.
- Cards: (Live) the trusted-types refusal and why it exists (loading untrusted tree files can crash or read memory out of bounds, per the MLflow error text: say "MLflow's own error message explains"); (Live) signatures enforce input schema; (Self) the champion on a real JFK test trip: fare $85.60, 21.66 miles, predicted tip $14.93, actual $21.77 - one row, not an evaluation.
- Real world: these two refusals happened while building this session's script (true story of this build; say so).

Build-along: b7.py in four parts: setup and data (output: card trips on 15 Jan: 61260); two runs (output: linear MAE $1.387, forest MAE $1.331); register and alias (output: registered taxi_tip_model version 1 from forest as @champion); load by alias and predict (output: champion on a real JFK trip ...). Copy outputs exactly from b7.out.txt; ignore warning lines. Free Edition notebook step (not run): `import mlflow; mlflow.set_registry_uri("databricks-uc")` (default in MLflow 3), `mlflow.register_model(f"runs:/{run_id}/model", "your_catalog.your_schema.taxi_tip_model")`, `MlflowClient().set_registered_model_alias("your_catalog.your_schema.taxi_tip_model", "champion", 1)`, `mlflow.pyfunc.load_model("models:/your_catalog.your_schema.taxi_tip_model@champion")`. Figure (b7d): the run → register → alias → load chain with the Databricks names.
Bad box: promoting a model by overwriting version 1 or by a "Production" stage. Tip: move the alias, never the model.
Quiz: (1) what replaces stages in Unity Catalog (aliases); (2) the three-level model name; (3) why MLflow refused the forest (untrusted types until vouched for).
Covered: Databricks MLflow and models-in-UC docs read at source; outputs run with MLflow 3.16.1; Free Edition not run.
Cheat: experiment → runs; log params, metrics, model + signature; catalog.schema.model; aliases not stages; EXECUTE to load; vouch only for your own types.
Next: session 8, the bench: everything from sessions 1 to 5 on one real log.
Footer: prev b6 "Unity Catalog grants", next b8 "The Delta log bench".
