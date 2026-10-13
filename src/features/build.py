import pandas as pd
from src.data.split import get_split
from src.data.clean import clean_data
import yaml
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

def add_time_features(df: pd.DataFrame):
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour
    df["month"] = df["timestamp"].dt.month
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    # Hour and month are cyclical (23:00 is next to 00:00), so place them on a circle
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    # Weekday commuting peaks: 7-10 am and 4-7 pm
    weekday = df["day_of_week"] < 5
    morning = (df["hour"] >= 7) & (df["hour"] < 10)
    evening = (df["hour"] >= 16) & (df["hour"] < 19)
    df["rush_hour"] = (weekday & (morning | evening)).astype(int)
    # Fill N/A value incidents
    df["incident"] = df["incident"].fillna("Missing")
    return df

class RouteFrequencyEncoder(BaseEstimator, TransformerMixin):
    """Replace each route with its share of training incidents (unseen routes -> 0)."""
    def fit(self, X, y=None):
        self.freq_ = X["route"].value_counts(normalize=True).to_dict()
        return self

    def transform(self, X):
        route_freq = X["route"].map(self.freq_).fillna(0)
        return route_freq.to_frame("route_freq")
    
if __name__ == "__main__":
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
    df = clean_data(config)

    train = get_split(df, config, "training_set")
    
    time = add_time_features(train)
    print(time[["timestamp", "hour", "hour_sin", "hour_cos", "month", "day_of_week", "rush_hour"]].head())
    print(time[["hour_sin", "hour_cos", "month_sin", "month_cos"]].describe().loc[["min", "max"]])
    print(f"rush_hour share: {time['rush_hour'].mean():.3f}")
    print(f"missing incident: {time['incident'].isna().sum()}, rows: {len(time)}")

    val = get_split(df, config, "validation_set")
    val_time = add_time_features(val)
    encoder = RouteFrequencyEncoder().fit(time)
    route_freq = encoder.transform(val_time)
    print(f"routes learned: {len(encoder.freq_)}, shares sum: {sum(encoder.freq_.values()):.3f}")
    print(f"val route_freq shape: {route_freq.shape}, unseen routes (0): {(route_freq['route_freq'] == 0).sum()}")