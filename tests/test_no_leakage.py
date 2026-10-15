# tests/test_no_leakage.py — run with: python -m tests.test_no_leakage
from src.features.build import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, ROUTE_COLUMN


def test_min_gap_not_a_feature():
    feature_columns = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS + ROUTE_COLUMN
    
    assert "min_gap" not in feature_columns, "Leakage detected: min_gap is in features"
    assert "min_delay" not in feature_columns, "Target min_delay must not be an input feature"
    
    print("test_min_gap_not_a_feature passed:", feature_columns)

if __name__ == "__main__":
    test_min_gap_not_a_feature()

