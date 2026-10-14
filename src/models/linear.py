from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from src.features.build import build_preprocessor, add_time_features
from src.data.clean import clean_data
from src.data.split import get_split
import yaml


def make_linear_regression():
    """Linear Regression (default settings, untuned) on the preprocessed features."""
    return Pipeline(
        [("preprocess", build_preprocessor()), ("model", LinearRegression())]
    )


if __name__ == "__main__":
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
    df = clean_data(config)
    train = get_split(df, config, "training_set")
    train = add_time_features(train)  # same table, now with time columns
    y = train["min_delay"]
    model = make_linear_regression().fit(train, y)
    prediction = model.predict(train)

    print(f"predictions: {len(prediction)}, first 5: {prediction[:5].round(2)}")
    print(
        f"min {prediction.min():.2f}, max {prediction.max():.2f}, negative: {(prediction < 0).sum()}"
    )
