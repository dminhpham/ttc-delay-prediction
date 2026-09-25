# TTC-delay-prediction
### Group 4 - CSCI 3052U

Predict how long a TTC bus or streetcar delay will last (minutes), at the moment the incident is logged.

#### Data
Raw data is included in `data/raw/csv/`: TTC Bus, Streetcar and Subway Delay Data, Jan 2014 – Dec 2024,
from the [City of Toronto Open Data Portal](https://open.toronto.ca/), under the
Open Government Licence – Toronto.

One change from the original download: the July and August 2021 files in the bus folder were copies of
the streetcar data and have been removed (see `docs/notes.md`, Issue 1).

#### Setup
```
python -m venv .venv
.venv\Scripts\activate        # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

#### Run
From the repo root:
```
python -m src.data.load       # loads bus + streetcar into one table (850,590 rows after dedupe)
```

#### Updated Progress
- Load raw data (`src/data/load.py`)
