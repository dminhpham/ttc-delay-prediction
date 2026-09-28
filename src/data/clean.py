import pandas as pd
from src.data.load import load_data
import yaml



# Combine date and time columns into timestamp
def parse_datetime(df: pd.DataFrame):
    df = df.copy()
    print(f"Rows in {df.shape[0]}")
    # pad HH:MM -> HH:MM:00
    time = df["time"].where(df["time"].str.len() != 5, df["time"] + ":00")
    df["timestamp"] = pd.to_datetime(df["date"] + " " + time, format="%Y-%m-%d %H:%M:%S", errors="coerce")
    # Check if new column timestamp contains N/A values
    print(f"dropped {df['timestamp'].isna().sum()}")
    df = df.dropna(subset=["timestamp"])
    print(f"Rows out {df.shape[0]}")
    return df

DIRECTION_MAP = {
    "N": "North", "NB": "North", "NORTH": "North",
    "S": "South", "SB": "South", "SOUTH": "South",
    "E": "East",  "EB": "East",  "EAST": "East",
    "W": "West",  "WB": "West",  "WEST": "West",
    "BW": "Both", "B": "Both", "BWS": "Both", "BOTHWAYS": "Both",
    "NS": "Both", "SN": "Both", "EW": "Both", "WE": "Both",
}

def clean_direction(df: pd.DataFrame):
    df = df.copy()
    df["direction"] = df["direction"].str.upper().str.replace(r"[^A-Z]", "", regex=True)
    df["direction"] = df["direction"].map(DIRECTION_MAP)
    print(f"mapped to Unknown: {df['direction'].isna().sum()}")
    df["direction"] = df["direction"].fillna("Unknown")
    print(df["direction"].value_counts())
    return df

def clean_route(df: pd.DataFrame, config):
    df = df.copy()
    print(f"Rows in {df.shape[0]}")
    df["route"] = pd.to_numeric(df["route"], errors="coerce")
    # Keep only rows where the route is between the config values
    rows_before = len(df)
    df = df[df["route"].between(config["route"]["min"],config["route"]["max"])]
    print(f"dropped (missing / non-numeric / outside 1 - 999): {rows_before - len(df)}")
    # Cast df to int type 
    df["route"] = df["route"].astype(int)
    print(f"Rows out {df.shape[0]}")
    print(f"distinct routes: {df['route'].nunique()}")
    return df

if __name__ == "__main__":
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)
    df = load_data()
    df = parse_datetime(df)
    df = clean_direction(df)
    df = clean_route(df, config)