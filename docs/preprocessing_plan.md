# Pre-processing Plan

### Leakage audit
The target is `min_delay`: how long a TTC bus or streetcar delay lasts, in minutes. The prediction is made at the moment the incident is logged, so features must only use information that would be available at that time.

`min_gap` is kept in `data/processed/clean.csv` for EDA but will not be used as a model feature. In the cleaned dataset, `min_gap` and `min_delay` have a Pearson correlation of approximately 0.753. `min_gap` describes the service gap associated with the delay and is closely related to the delay duration we are trying to predict. Because the prediction is made at the moment the incident is logged, using `min_gap` could provide information about the outcome that would not be reliably available at prediction time, causing target leakage.

`min_delay` is the continuous target, measured in minutes, and is never included in the feature matrix. The target filter `0 < min_delay <= 180` is applied during cleaning before the data is split for modelling.

The remaining candidate information is:
- `timestamp`: used to derive time features; the raw timestamp itself will not be passed directly to the model.
- `route`, `location`, `incident`, `direction`, `vehicle`, and `mode`: candidate predictors.
- `date`, `time`, and `day`: not used directly when the same information is represented by features derived from `timestamp`.

Any preprocessing that learns information from the data will be fitted on the training set only, then applied unchanged to validation and test data.

### Data split
The data will be split chronologically using the years defined in `config/config.yaml`:
- Training: 2014-2022
- Validation: 2023
- Test: 2024

A chronological split is used instead of a random split because the goal is to predict future delay incidents using historical data. This also keeps later records out of the training set.

The training set is used to fit the models and any data-dependent preprocessing. The validation set is used for model and hyperparameter selection. The test set is held out until the final evaluation.

The year 2020 will remain in the training set despite the change in TTC delay patterns during the COVID-19 period. Its effect will be treated as a robustness question for a later milestone rather than removing the year without evidence.

### Time features
The cleaned `timestamp` will be used to derive time-based features instead of using the raw date and time strings.

Planned model features include:
- cyclical hour-of-day features
- cyclical month-of-year features
- weekend indicator
- rush-hour indicator

Hour of day and month of year are cyclical, so they will be represented using sine and cosine transformations. This avoids treating values at the ends of a cycle as far apart, such as 23:00 and 00:00 or December and January.

Day of week will be used to derive a weekend indicator, and a rush-hour indicator will be derived from the time of day.

The year is used to create the chronological train, validation, and test split rather than as a model feature.

### Categorical features
Categorical features will be encoded after the chronological split so that preprocessing decisions are based on the training set only.

`direction`, `incident`, and `mode` will be treated as categorical features. `route` is stored as an integer after cleaning, but the number identifies a transit route rather than a continuous quantity, so it will also be treated as categorical.

`mode`, `direction`, and `incident` will be one-hot encoded. The encoder will be fitted on the training set only and will handle categories not seen during training without using information from the validation or test sets.

`route` will use frequency encoding because it has higher cardinality. Route frequencies will be calculated from the training set only and then applied unchanged to the validation and test sets.

Route frequency is highly uneven in the training set. Of the 486 routes, 196 have fewer than 10 records and 241 have fewer than 100 records. Frequency encoding allows this information to be represented without creating a separate one-hot column for every route.

`location` will be deferred from the initial feature set because of its very high cardinality. `vehicle` will also be evaluated separately before inclusion because it has high cardinality and many missing values. In the training set, `location` has 131,614 unique values, with 124,400 appearing fewer than 10 times. `vehicle` has 4,871 unique values, with 1,239 appearing fewer than 10 times. Direct one-hot encoding of these features could create a very large and sparse feature space, so they will not be automatically encoded in the same way as the lower-cardinality categorical features.

In the 2014-2022 training set, `mode` has 2 unique values, `direction` has 6, `incident` has 35, and `route` has 486. `vehicle` has 4,871 unique values and 70,825 missing values, while `location` has 131,614 unique values and 952 missing values. `incident` has 930 missing values.

Missing categorical values will be handled explicitly rather than silently dropping rows. After cleaning, `route` and `direction` have no missing values in the training set. Missing values in `incident`, `location`, and `vehicle` will be treated as an explicit missing category if those features are included in the model.

The exact treatment of rare and high-cardinality categories will be decided using the training set before model fitting.

### Scaling
Scaling will be fitted on the training set only and then applied unchanged to the validation and test sets.

Numeric features that require scaling will be standardized for models that are sensitive to feature scale, such as Linear Regression. Tree-based models such as Decision Trees and Random Forests do not require feature scaling, so the preprocessing pipeline can handle scaling according to the model being evaluated.

Categorical features will be encoded separately and will not be treated as continuous numeric values.

### Evaluation metrics
Mean Absolute Error (MAE) will be the primary evaluation metric, with Root Mean Squared Error (RMSE) reported as a secondary metric.
