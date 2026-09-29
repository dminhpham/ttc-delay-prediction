"""
Load the raw TTC bus and streetcar delay into DF
subway is loaded separately, for profiling only
"""

import pandas as pd
import glob
from pathlib import Path
raw_data_dir = Path(__file__).resolve().parents[2]/"data"/"raw"/"csv"

# Rename spelling ttc used to one name
RENAME = {
    "Report Date": "date",
    "Date": "date",
    "Route": "route",
    "Line": "route",
    "Direction": "direction",
    "Bound": "direction",
    "Min Delay": "min_delay",
    "Delay": "min_delay",
    "Min Gap": "min_gap",
    "Gap": "min_gap",
    "Time": "time",
    "Day": "day",
    "Location": "location",
    "Incident": "incident",
    "Vehicle": "vehicle",
    # subway incident category: 222 short codes vs 35 labels for bus/streetcar
    "Station": "location",
    "Code": "incident"
}

# Re-order the columns name
COLUMNS = [
    "date",
    "time",
    "day",
    "route",
    "location",
    "incident",
    "min_delay",
    "min_gap",
    "direction",
    "vehicle",
]

# Read bus and streetcar data into DF
def load_data() -> pd.DataFrame:
    frames = []
    for mode in ["bus", "streetcar"]:
        # Data from 2014 - 2021
        paths = glob.glob(f"{raw_data_dir}/ttc-{mode}-delay-data-*/*.csv")
        # Data from 2022-2024
        paths += glob.glob(f"{raw_data_dir}/ttc-{mode}-delay-data-20*.csv")

        for path in sorted(paths):
            df = pd.read_csv(path)
            # Remove duplicated row
            df = df.drop_duplicates()
            # Remove all leading and trailing whitespace from column headers
            df.columns = df.columns.str.strip()
            # Rename the column
            df = df.rename(columns=RENAME)[COLUMNS]
            df["mode"] = mode
            frames.append(df)
    return pd.concat(frames, ignore_index=True)

# Read subway data
def load_subway() -> pd.DataFrame:
    frames = []
    # Data from 2018-2021
    paths = glob.glob(f"{raw_data_dir}/ttc-subway-delay-data-*/*.csv")
    # Data from 2022-2024
    paths += glob.glob(f"{raw_data_dir}/ttc-subway-delay-data-20*.csv")
    # Data from 2014-2017
    paths += glob.glob(f"{raw_data_dir}/ttc-subway-delay-jan-2014-april-2017.csv")
    # Data from May-December 2017
    paths += glob.glob(f"{raw_data_dir}/ttc-subway-delay-may-december-2017/*.csv")
    for path in sorted(paths):
        df = pd.read_csv(path)
        # Remove duplicated row
        df = df.drop_duplicates()
        # Remove all leading and trailing whitespace from column headers
        df.columns = df.columns.str.strip()
        # Rename the column
        df = df.rename(columns=RENAME)[COLUMNS]
        df["mode"] = "subway"
        frames.append(df)
    return pd.concat(frames, ignore_index=True)

if __name__ == "__main__":
    df = load_data()
    df_subway = load_subway()
    print(df_subway.shape)
    print(df_subway["mode"].value_counts())
    print(df.shape)
    print(df["mode"].value_counts())