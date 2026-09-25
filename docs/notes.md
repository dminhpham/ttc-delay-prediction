# Observations
Document all raw notes

### Issue 1
In 2021, the data from Open Data for bus delay is identical to the streetcar in July and August. Drop 2 months for bus

### Issue 2
Check the median delay for subway to see if we can use the data for training.

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

