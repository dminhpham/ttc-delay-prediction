from sklearn.tree import DecisionTreeRegressor
from sklearn.pipeline import Pipeline
from src.features.build import build_preprocessor, add_time_features
from src.data.clean import clean_data
from src.data.split import get_split
from src.evaluate import evaluate, mae
import time
import yaml


def make_decision_tree(seed, **params):
    """Decision tree regressor on the same preprocessed features as Linear Regression."""
    return Pipeline(
        [
            ("preprocess", build_preprocessor()),
            ("model", DecisionTreeRegressor(random_state=seed, **params)),
        ]
    )


if __name__ == "__main__":
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
    df = clean_data(config)
    t_train = add_time_features(get_split(df, config, "training_set"))
    y = t_train["min_delay"]
    t_val = add_time_features(get_split(df, config, "validation_set"))
    y_val = t_val["min_delay"]

    # Measure how long the model.fit() takes to run 
    start = time.perf_counter()
    model = make_decision_tree(config["seed"]).fit(t_train, y)  # untuned: no extra settings
    fit_seconds = time.perf_counter() - start
    tree = model.named_steps["model"]  # the fitted tree inside the Pipeline

    # Check the tree's depth and number of leaves
    print(f"depth: {tree.get_depth()}, leaves: {tree.get_n_leaves():,}")
    print(f"rows per leaf (average): {len(t_train) / tree.get_n_leaves():.1f}")
    print(f"fit time: {fit_seconds:.1f} s")

    # Predict only: the Pipeline already learned its encoders from the training rows
    start = time.perf_counter()
    val_pred = model.predict(t_val)
    predict_seconds = time.perf_counter() - start
    print(f"predict time (validation): {predict_seconds:.1f} s")

    # Training error: rows the tree has seen. No interval needed.
    train_mae = mae(y, model.predict(t_train))
    # Validation error: 2023 rows the tree has never seen, with 95% bootstrap intervals
    val = evaluate(y_val, val_pred, seed=config["seed"])

    print(f"train MAE: {train_mae:.2f}")
    print(f"val MAE:   {val['mae']:.2f}  (95% CI {val['mae_ci_low']:.2f}-{val['mae_ci_high']:.2f})")
    print(f"val RMSE:  {val['rmse']:.2f}  (95% CI {val['rmse_ci_low']:.2f}-{val['rmse_ci_high']:.2f})")
    print(f"gap (val - train MAE): {val['mae'] - train_mae:.2f}")
