
# Data Card: TTC Surface-Transit Delays (cleaned)

A one-page summary of the dataset used in this project. The details are in Section 1 (Dataset
Selection) and Section 3 (Filtering and Cleaning).

### Overview
| Item | Value |
|---|---|
| Source | City of Toronto Open Data Portal: [TTC Bus Delay Data](https://open.toronto.ca/dataset/ttc-bus-delay-data/), [TTC Streetcar Delay Data](https://open.toronto.ca/dataset/ttc-streetcar-delay-data/) |
| Publisher | Toronto Transit Commission (TTC) |
| Licence | [Open Government Licence – Toronto](https://open.toronto.ca/open-data-licence/) |
| Coverage | January 2014 – December 2024 (bus has no data for July–August 2021; see Section 3) |
| Unit of analysis | One logged delay incident on a bus or streetcar |
| Task | Supervised regression: predict delay duration at the moment the incident is logged |
| Target | `min_delay`: delay in minutes, continuous, kept in the range 0 < delay ≤ 180 |
| Rebuild | `python -m src.data.clean` → `data/processed/clean.csv` |

### Size
| Stage | Rows |
|---|---|
| Raw (97 bus + 99 streetcar CSV files) | 852,320 |
| After removing exact duplicates | 850,590 |
| After cleaning | **809,682** (bus 671,437 · streetcar 138,245) |

### Target summary (cleaned)
| Median | Mean | 90th percentile | 99th percentile | Range |
|---|---|---|---|---|
| 10 min | 14.0 min | 25 min | 91 min | 1 – 180 min |

### Columns (cleaned file)
| Column | Type | Notes |
|---|---|---|
| `timestamp` | datetime | Built from `date` + `time`; used for the split and time features |
| `date`, `time`, `day` | text | Original values, kept for reference |
| `route` | integer | 498 routes, all within 1–999; treated as a category, not a quantity |
| `direction` | category | 6 values: North, South, East, West, Both, Unknown |
| `incident` | category | 35 incident types; 930 missing |
| `location` | text | Free text, 142,811 distinct values; 953 missing; deferred as a feature |
| `vehicle` | number | 5,156 distinct IDs; 70,825 missing; evaluated separately before use |
| `mode` | category | bus or streetcar |
| `min_delay` | number | **Target** |
| `min_gap` | number | **Not a feature: leakage** (not known when the incident is logged) |

### Split (chronological, set in `config/config.yaml`)
| Set | Years | Rows |
|---|---|---|
| Train | 2014–2022 | 683,475 |
| Validation | 2023 | 62,924 |
| Test | 2024 | 63,283 (held out until the final evaluation) |

### Excluded
- **Subway data:** acquired and profiled, then excluded. Its median delay is 0 minutes, 65% of its
  rows are zero, and it uses a 222-code incident system. It is a different prediction task.
- **42,638 rows (5.0% of raw):** duplicates, unparseable times, invalid routes, and delays that
  are missing, zero or negative, or longer than 180 minutes. Section 3 gives the count and reason
  for each step.

### Known limitations
- Zero-minute delays are removed, so the model assumes that a delay has occurred.
- The 180-minute cut-off is a judgement call. It is set in the config so it can be changed and tested.
- Some codes are our own reading, since TTC does not document them: `NS`/`EW` → Both, and `RAD`,
  `LINE 1/2/3` and `SHUTTLE` treated as non-routes.
- 2020 has far fewer rows (41,378, compared with 103,341 in 2014) because of COVID-19. It is kept in
  training and will be checked for its effect later.
- Delays are logged by TTC staff, so the times, locations and codes contain human entry errors
  that the cleaning cannot fully remove.
