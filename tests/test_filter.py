# Run test in terminal: python -m tests.test_filter

# Negative test: Verify that the test correctly detects delays outside the specified range.
# 1. Temporarily comment out the original upper-bound assertion:
#    assert (delays <= upper).all(), f"Some delays exceed {upper} minutes"
# 2. Replace it with:
#    assert (delays <= 100).all(), "Some delays exceed 100 minutes"
# 3. Run test in terminal: python -m tests.test_filter
# 4. Confirm that the test fails with an AssertionError.
# 5. Restore the original assertion and rerun the test to confirm it passes.

import yaml
from src.data.clean import clean_data

def test_delays_in_range():
    # Loads the configuration settings
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)

    # Clean the dataset and gets the delay values
    df = clean_data(config)
    delays = df["min_delay"]

    # Stores minimum and maximum allowed delays for easier readability in code
    lower = config["target"]["lower_min_delay"]
    upper = config["target"]["upper_min_delay"]

    # Checks that the cleaned dataset is not empty
    assert not df.empty, "Cleaning returned no rows"

    # Checks that there are no missing delay values
    assert delays.isna().sum() == 0, "Missing values found in min_delay"

    # Checks that all delays are greater than the lower limit
    assert (delays > lower).all(), f"Some delays are below {lower} minutes"

    # Checks that all delays are within the upper limit
    assert (delays <= upper).all(), f"Some delays exceed {upper} minutes"

    print(f"test_delays_in_range passed: {len(df)} rows checked")


if __name__ == "__main__":
    test_delays_in_range()
