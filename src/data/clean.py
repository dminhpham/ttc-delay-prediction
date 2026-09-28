import pandas as pd
from src.data.load import load_data

# Combine date and time columns into timestamp
def parse_datetime(df: pd.DataFrame):
    df = df.copy()
    print(f"Rows in {df.shape[0]}")
    # pad HH:MM -> HH:MM:00
    time = df["time"].where(df["time"].str.len() != 5, df["time"] + ":00")
    df["timestamp"] = pd.to_datetime(df["date"] + " " + time, format="%Y-%m-%d %H:%M:%S", errors="coerce")
    # Check if new column timestamp contains N/A values
    print(f"dropped {df["timestamp"].isna().sum()}")
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
    print(f"mapped to Unknown: {df["direction"].isna().sum()}")
    df["direction"] = df["direction"].fillna("Unknown")
    print(df["direction"].value_counts())
    return df

if __name__ == "__main__":
    df = load_data()
    df = parse_datetime(df)
    clean_direction(df)