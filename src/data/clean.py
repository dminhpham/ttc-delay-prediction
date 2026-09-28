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

if __name__ == "__main__":
    df = load_data()
    df = parse_datetime(df)