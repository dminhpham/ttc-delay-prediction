from sklearn.tree import DecisionTreeRegressor
from sklearn.pipeline import Pipeline
from src.features.build import build_preprocessor, add_time_features
from src.data.clean import clean_data
from src.data.split import get_split
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

    model = make_decision_tree(config["seed"]).fit(t_train, y)  # untuned: no extra settings
    tree = model.named_steps["model"]  # the fitted tree inside the Pipeline

    # Check the tree's depth and number of leaves
    print(f"depth: {tree.get_depth()}, leaves: {tree.get_n_leaves():,}")
    print(f"rows per leaf (average): {len(t_train) / tree.get_n_leaves():.1f}")
