import pandas as pd
from src.data.clean import clean_data
import yaml

def get_split(df: pd.DataFrame, config, name: str):
    """Return the rows of one chronological split (e.g. "training_set")"""
    start = config["split"][name]["start"]
    end = config["split"][name]["end"]

    mask = df["timestamp"].dt.year.between(start, end)

    filter_data = df[mask].copy()

    print(f"{name}: {start}-{end}, rows {len(filter_data)}")

    return filter_data


if __name__ == "__main__":
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
    df = clean_data(config)

    train = get_split(df, config, "training_set")
    val = get_split(df, config, "validation_set")
    test = get_split(df, config, "testing_set")

    print(f"total: {len(train) + len(val) + len(test)}")