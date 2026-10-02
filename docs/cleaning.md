# 3. Dataset Filtering and Cleaning

All cleaning is done in code, not by editing files by hand. `src/data/load.py` reads the raw CSVs
into one table and `src/data/clean.py` cleans it. Every threshold lives in `config/config.yaml`.
Running `python -m src.data.clean` rebuilds `data/processed/clean.csv` and prints the row count
after each step.

### Removed

**Duplicate files.** The raw download contains a folder, `ttc-streetcar-delay-data-2020 (1)`, that
is a byte-for-byte copy of the 2020 streetcar folder (12 files, 7,830 rows). We deleted it before
loading. In the bus folder, the July and August 2021 files contain streetcar data (they use the
streetcar column names, and the rows match the streetcar files exactly), so we removed them too. As
a result, bus has no data for July–August 2021.

**Exact duplicate rows (1,730).** Some incidents are logged twice with identical values in every
column. We cannot tell a double log apart from two genuinely identical incidents, so we drop exact
copies and report the count.

**Unparseable times (39 rows).** These rows have a date where the time should be (e.g. `1940-10-01`),
so no valid timestamp can be built for them.

**Invalid routes (2,849 rows).** 2,334 rows have no route, 34 have numbers outside the TTC route
range of 1–999 (e.g. `0`, `898630`, most likely vehicle numbers entered in the wrong field), and 481
have text labels instead of a route number. Our reading of the labels, which TTC does not document:
`RAD` is "Run As Directed" (no fixed route); `LINE 1/2/3`, `BD`, `YU` and `SRT` are shuttle buses
replacing subway service, which is outside our scope; `SHUTTLE` is a temporary service. The label
`927 HIGHWAY 27` is the 927 express route, which already appears in the data under its number.

**Target filter (38,020 rows).** We keep `0 < min_delay ≤ 180` minutes.
- *Missing delay (540 rows):* there is no target to learn from.
- *Zero or negative (27,847 rows):* a zero means the incident caused no delay. Our task is to
  predict *how long* a delay lasts, so including zeros would turn this into a different problem
  (compare the subway data, where 65% of rows are zero). Negative delays are impossible and must be
  data entry errors. **Limitation:** our model assumes that a delay has occurred.
- *Over 180 minutes (9,633 rows):* the 99th percentile jumps to 209 minutes. The most common values
  above 180 are 999 (1,231 rows, almost certainly a placeholder) and round blocks such as 240, 300
  and 480, which look like planned closures rather than timed incidents. These rows are 1.2% of the
  data but 30% of all delay minutes, so they would dominate squared-error models such as Linear
  Regression. The 180-minute cut-off is a judgement call. It is set in the config so that a
  different value, such as 240, can be tested in a later milestone.

### Modified or corrected

**Column names.** The column headers change over the years: 5 layouts across the bus files and 4
across the streetcar files (`Report Date`/`Date`, `Route`/`Line`, `Direction`/`Bound`,
`Min Delay`/`Delay`, `Min Gap`/`Gap`, an extra `Incident ID` column in April 2019, a trailing empty
column in December 2021, and stray spaces). The loader strips the spaces and maps every spelling to
one name, giving the same 10 columns plus `mode` (bus or streetcar).

**Date and time → `timestamp`.** Older files record times as `HH:MM:SS` and newer ones as `HH:MM`.
We pad the short form and combine `date` and `time` into one datetime column using an explicit
format. The chronological split and all time features are built from this column.

**Direction: 1,226 spellings → 6 values.** The same direction appears as `N`, `NB`, `N/B`, `n`,
` N`, and so on. We upper-case each value, remove anything that is not a letter, and map the result
to North, South, East, West, Both or Unknown. "Both ways" (`B/W`, `BW`, `B`, …) is kept as its own
value rather than forced into one direction. `NS` and `EW` are read as both directions on that axis
and mapped to Both (an assumption, since TTC does not define these codes; it affects 1,325 rows).
Missing and unclear values (`UP`, `DOWN`, `OB`, numbers) become Unknown.

| North | South | East | West | Both | Unknown |
|---|---|---|---|---|---|
| 173,049 | 155,067 | 192,053 | 185,255 | 79,197 | 65,930 |

**Route: 858 values → 503.** Routes were stored as numbers (`504`), text (`"504"`) and decimals
(`504.0`), so the same route counted as up to three different values. We convert every value to a
number, keep 1–999 (see *Removed* above) and store routes as whole numbers. About 200 routes have
fewer than 10 rows each. We keep them, because grouping rare routes is a pre-processing decision
that must be made on the training years only (Section 4).

### Excluded

**Subway.** We loaded and profiled the subway data, then excluded it. Its median delay is 0 minutes,
65% of its rows are zero, and it uses a 222-code incident system instead of the 35 categories used
for bus and streetcar. It is a different prediction problem (see Section 1).

**`min_gap`.** This column is kept in the cleaned file for analysis but will not be used as a model
feature: it is not known when the incident is logged and would leak the answer (Section 4).

### Row counts

| Step | Rows | Removed |
|---|---|---|
| Raw (97 bus + 99 streetcar files) | 852,320 | – |
| Drop exact duplicate rows | 850,590 | 1,730 |
| Parse date and time | 850,551 | 39 |
| Clean direction | 850,551 | 0 (values relabelled only) |
| Clean route | 847,702 | 2,849 |
| Target filter `0 < delay ≤ 180` | **809,682** | 38,020 |

In total, 42,638 of 852,320 raw rows (5.0%) were removed. The cleaned dataset covers every year
from 2014 to 2024.
