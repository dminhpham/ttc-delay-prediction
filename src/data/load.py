# import config
"""
Load the raw TTC bus and streetcar delay into DF
"""

import pandas as pd
import glob

raw_data_dir = "data/raw/csv"

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
def load_data():
    frames = []
    for mode in ["bus", "streetcar"]:
        # Data from 2014 - 2021
        paths = glob.glob(f"{raw_data_dir}/ttc-{mode}-delay-data-*/*.csv")
        # Data from 2022-2024
        paths += glob.glob(f"{raw_data_dir}/ttc-{mode}-delay-data-20*.csv")

        for path in sorted(paths):
            df = pd.read_csv(path)
            # Remove all leading and trailing whitespace from column headers
            df.columns = df.columns.str.strip()
            # Rename the column
            df = df.rename(columns=RENAME)[COLUMNS]
            df["mode"] = mode
            frames.append(df)
    return pd.concat(frames)

df = load_data()
print(df.shape)
print(df["mode"].value_counts())