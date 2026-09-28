# Observations
Document all raw notes

### Issue 1
In 2021, the data from Open Data for bus delay is identical to the streetcar in July and August. Drop 2 months for bus

### Issue 2
Check the median delay for subway to see if we can use the data for training.
"Resolved: subway excluded, see notebooks/raw_data_profile.ipynb"

### Issue 3 — exact duplicate rows
double-logging rather than one bad file. Dropped with `drop_duplicates()`: 852,320 raw → 850,590.
We can't tell a double log from two genuinely identical incidents, so we drop exact copies and report the count.

### Issue 4 — header drift across files
Column names change over the years (`Report Date`/`Date`, `Route`/`Line`, `Direction`/`Bound`,
`Min Delay`/`Delay`, `Min Gap`/`Gap`, extra `Incident ID` in Apr 2019, stray spaces). The loader
strips whitespace and maps every spelling to one name (`RENAME` in `src/data/load.py`), then keeps
the same 10 columns plus `mode`.

### Loader row counts (`src/data/load.py`)
| Step | Bus | Streetcar | Total |
|---|---|---|---|
| Raw (97 bus + 99 streetcar files) | 705,095 | 147,225 | 852,320 |
| After dedupe | 703,610 | 146,980 | 850,590 |

### Issue 5 — time format drift
Old files use `HH:MM:SS`, newer ones `HH:MM`. `parse_datetime` pads `HH:MM` → `HH:MM:00`, joins
`date` + `time` into one `timestamp` with an explicit format, and `errors="coerce"` turns bad values
into NaT. 39 rows had a date in the time field (e.g. `1940-10-01`) → dropped.

### Issue 6 — direction spellings
1,226 raw spellings (`N/B`, `nb`, ` N`, `B/W`…) + 59,586 missing. `clean_direction` upper-cases,
strips non-letters (→ 278 spellings), then maps via `DIRECTION_MAP` to 6 values. Unmapped → `Unknown`.
- "Both ways" (`B/W`, `BW`, `B`…) kept as its own value, not forced into N/S/E/W.
- **Assumption:** `NS`/`SN`/`EW`/`WE` (1,325 rows) read as both directions on that axis → `Both`.
  TTC does not document this.
- Unknown = missing + unclear (`OB`, `UP`, `DOWN`, vehicle numbers typed in the wrong field).

| Value | Rows |
|---|---|
| East | 192,053 |
| West | 185,255 |
| North | 173,049 |
| South | 155,067 |
| Both | 79,197 |
| Unknown | 65,930 |

### Issue 7 — route stored three ways + non-route labels
`504`, `"504"` and `504.0` were three different values → 858 "routes". `clean_route` converts with
`pd.to_numeric(errors="coerce")` and keeps 1–999 (range in config; TTC numbers routes 1–199, 300s
night, 400s community, 500s streetcar, 900s express). Dropped 2,849 rows → 503 routes remain.
- Missing: 2,334. Out of range (`0`, `5063`, `898630`, likely vehicle numbers): 34.
- Text labels (481), **our reading, not documented by TTC:** `RAD` = Run As Directed (no fixed
  route); `LINE 1/2/3`, `BD`, `YU`, `SRT` = subway shuttle buses (subway is out of scope);
  `SHUTTLE` = temporary service; `927 HIGHWAY 27` = route 927, already present as `927`.
- ~200 routes have < 10 rows. Kept: grouping rare routes is pre-processing, decided on train only.

### Config (`config/config.yaml`)
One place for settings, so code doesn't hard-code them: `seed: 42`; target filter `0 < delay ≤ 180`;
chronological split train 2014–2022, validation 2023, test 2024 (years inclusive, no overlap);
valid route range 1–999.

### Cleaning row counts (`src/data/clean.py`)
| Step | Rows | Removed |
|---|---|---|
| From loader | 850,590 | – |
| `parse_datetime` | 850,551 | 39 (unparseable time) |
| `clean_direction` | 850,551 | 0 (values relabelled only) |
| `clean_route` | 847,702 | 2,849 (missing / non-numeric / outside 1–999) |
