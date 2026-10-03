# Analyst session 7: MLflow tracking + a registered model with an alias, all local (no account)
import duckdb, mlflow, numpy as np
from mlflow.models import infer_signature
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

mlflow.set_tracking_uri("sqlite:///mlflow.db")      # Databricks: the workspace tracks for you
mlflow.set_experiment("taxi-tips")

df = duckdb.sql("""
  SELECT fare_amount, trip_distance, PULocationID AS pu_zone, tip_amount
  FROM 'yellow_tripdata_2024-01.parquet'
  WHERE tpep_pickup_datetime >= TIMESTAMP '2024-01-15' AND tpep_pickup_datetime < TIMESTAMP '2024-01-16'
    AND payment_type = 1 AND fare_amount > 0
""").df()
X, y = df[["fare_amount", "trip_distance", "pu_zone"]], df["tip_amount"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=15)
print("card trips on 15 Jan:", len(df))

runs = {}
for name, model in [("linear", LinearRegression()), ("forest", RandomForestRegressor(n_estimators=100, max_depth=8, random_state=15))]:
    with mlflow.start_run(run_name=name) as run:
        model.fit(Xtr, ytr)
        mae = mean_absolute_error(yte, model.predict(Xte))
        mlflow.log_param("model", name)
        mlflow.log_metric("mae_usd", mae)
        # MLflow 3 saves sklearn models with skops and refuses tree types unless you vouch for them
        trusted = ["sklearn.tree._tree.Tree"] if name == "forest" else None
        mlflow.sklearn.log_model(model, name="model", signature=infer_signature(Xte, model.predict(Xte)),
                                 skops_trusted_types=trusted)
        runs[name] = (run.info.run_id, mae)
        print(f"{name:9s} MAE ${mae:.3f}")

best = min(runs, key=lambda k: runs[k][1])
mv = mlflow.register_model(f"runs:/{runs[best][0]}/model", "taxi_tip_model")
client = mlflow.MlflowClient()
client.set_registered_model_alias("taxi_tip_model", "champion", mv.version)
print("registered taxi_tip_model version", mv.version, "from", best, "as @champion")

champ = mlflow.pyfunc.load_model("models:/taxi_tip_model@champion")
row = Xte[Xte["pu_zone"] == 132].head(1)        # a real JFK pickup from the test set
print("champion on a real JFK trip: fare $%.2f, %.2f miles, predicted tip $%.2f, actual tip $%.2f" % (
    row["fare_amount"].iloc[0], row["trip_distance"].iloc[0], champ.predict(row)[0], yte[row.index[0]]))
