"""Checks for clean_incident in src/data/clean.py, on a tiny hand-made table where we know the right answer."""

import pandas as pd

from src.data.clean import clean_incident


def ttc_incidents():
    # 7 made-up incidents: 5 spelling problems (rows 0-4) and 2 that must NOT change (rows 5-6)
    return pd.DataFrame({
        "incident": ["Securitty", "Late  ", "e", "Road Block - Non-TTC Collision",
                     "Roadblock by Collision - Non-TTC", "Mechanical", None],
        "min_delay": [10, 5, 7, 30, 25, 12, 8],
    })


def test_variants_are_merged():
    out = clean_incident(ttc_incidents())["incident"]
    assert out[0] == "Security", out[0]                          # typo fixed
    assert out[1] == "Late", repr(out[1])                        # trailing spaces removed
    assert pd.isna(out[2]), out[2]                               # 'e' is not a real type -> missing
    assert out[3] == "Road Blocked - NON-TTC Collision", out[3]  # variant merged
    assert out[4] == "Road Blocked - NON-TTC Collision", out[4]  # variant merged


def test_correct_labels_are_unchanged():
    out = clean_incident(ttc_incidents())["incident"]
    assert out[5] == "Mechanical", out[5]    # a correct label stays as it is
    assert pd.isna(out[6]), out[6]           # missing stays missing


def test_no_rows_lost_and_other_columns_untouched():
    before = ttc_incidents()
    after = clean_incident(before)
    assert len(after) == len(before), f"{len(before)} rows in, {len(after)} rows out"
    assert after["min_delay"].tolist() == before["min_delay"].tolist()


def test_input_is_not_modified():
    before = ttc_incidents()
    clean_incident(before)
    assert before["incident"][0] == "Securitty"   # the function works on a copy


if __name__ == "__main__":
    tests = [f for name, f in sorted(globals().items()) if name.startswith("test_") and callable(f)]
    for test in tests:
        test()
        print(f"{test.__name__} passed")
    print(f"{len(tests)} tests passed")