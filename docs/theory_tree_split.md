# How a decision tree chooses a split

Our Decision Tree (`src/models/tree.py`, scikit-learn `DecisionTreeRegressor`) uses the default
criterion, **squared error**. This note explains the rule with a small example worked by hand.

## The rule

At each node the tree looks at every feature and every possible cut point. A cut sends the rows
into a left group and a right group. For each group it predicts the group **mean**, and it measures
the squared error around that mean (SSE = sum of squared differences from the mean).

It keeps the cut with the smallest total:

    cost(split) = SSE_left + SSE_right  =  n_left · MSE_left + n_right · MSE_right

Then it repeats the same search inside each new group, until a stopping rule says stop
(`max_depth`, or a group smaller than `min_samples_leaf`). Each final group is a **leaf**, and every
new incident that lands in that leaf gets the leaf's training mean as its prediction.

## Worked example

Six delays (minutes), sorted by one feature: **5, 6, 7, 30, 32, 34**.

**No split.** Mean = 114 / 6 = 19.
SSE = 14² + 13² + 12² + 11² + 13² + 15² = 196 + 169 + 144 + 121 + 169 + 225 = **1024**.

**Every possible cut:**

| Cut between | Left group (mean, SSE) | Right group (mean, SSE) | Total SSE |
|---|---|---|---|
| 5 \| 6 | {5}: 5.0, 0 | {6, 7, 30, 32, 34}: 21.8, 788.8 | 788.8 |
| 6 \| 7 | {5, 6}: 5.5, 0.5 | {7, 30, 32, 34}: 25.75, 476.75 | 477.25 |
| **7 \| 30** | **{5, 6, 7}: 6.0, 2** | **{30, 32, 34}: 32.0, 8** | **10** |
| 30 \| 32 | {5, 6, 7, 30}: 12.0, 434 | {32, 34}: 33.0, 2 | 436 |
| 32 \| 34 | {5, 6, 7, 30, 32}: 16.0, 754 | {34}: 34.0, 0 | 754 |

Check of the winning cut: left SSE = (5−6)² + (6−6)² + (7−6)² = 2; right SSE = (30−32)² + 0 + (34−32)² = 8.

The tree picks **7 | 30**, because 10 is far below 1024 (no split) and below every other cut. The
two leaves then predict **6 min** and **32 min**.

## Why "leaf = mean" fits RMSE, and why MAE would prefer "leaf = median"

The mean is the single number that minimises squared error, so a tree built on squared error is, in
effect, optimising for RMSE. Our main metric is MAE, and the number that minimises absolute error is
the **median**. The two differ when a leaf has a long tail. Example leaf: 8, 9, 10, 10, 11, 90.

| Leaf predicts | Value | MAE on this leaf | RMSE on this leaf |
|---|---|---|---|
| mean | 23.0 | 22.33 | **29.98** |
| median | 10.0 | **14.00** | 32.68 |

One 90-minute delay drags the mean to 23, which is too high for the five normal incidents. The
median stays at 10 and wins on MAE, while the mean wins on RMSE. This is why we expected the tree to
do clearly better than the route × hour median on RMSE but only a little better on MAE, and it is
the question behind experiment C (leaf median instead of leaf mean).

**Why not grow the tree with absolute error instead?** scikit-learn supports
`criterion="absolute_error"`, but it is far slower on 683,475 rows, so we keep squared error for
growing the tree and test the cheaper fix in experiment C: grow with squared error, then replace
each leaf's value with the median of its training rows.
