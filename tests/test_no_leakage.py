# Run test in terminal: python -m tests.test_no_leakage

# Negative test: To verify that the test correctly detects data leakage.
# 1. Temporarily add:  feature_columns.append("min_gap") before the assertions.
# 2. Run test in terminal: python -m tests.test_no_leakage
# 3. Confirm that the test fails with an AssertionError indicating data leakage.
# 4. Remove the temporary line and rerun the test to confirm it passes.


from src.features.build import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, ROUTE_COLUMN

def test_min_gap_not_a_feature():

    # Combines  categorical and numerical features into one list
    feature_columns = list(CATEGORICAL_COLUMNS) + list(NUMERIC_COLUMNS)

    # Adds the route feature regardless of whether it is a string or a list
    if isinstance(ROUTE_COLUMN, str):
        feature_columns.append(ROUTE_COLUMN)
    else:
        feature_columns.extend(ROUTE_COLUMN)

    # Assertions to check that neither min_gap or the target min_delay is used as an input
    assert "min_gap" not in feature_columns, "Leakage detected: min_gap is in features"
    assert "min_delay" not in feature_columns, "Target min_delay must not be an input feature"

    print("test_min_gap_not_a_feature passed:", feature_columns)


if __name__ == "__main__":
    test_min_gap_not_a_feature()
