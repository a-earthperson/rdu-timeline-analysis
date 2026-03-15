from __future__ import annotations

import numpy as np

from rdu_timeline_analysis.io import load_dataset_csv, parse_date, parse_num


def test_parse_tokens() -> None:
    assert str(parse_date("?")) == "NaT"
    assert str(parse_date("FUTURE")) == "NaT"
    assert np.isnan(parse_num("N/A"))
    assert np.isnan(parse_num("#VALUE!"))


def test_load_dataset_adds_helper_columns() -> None:
    csv_text = """user,field_office,i-485 receipt date,interview date,i-130 approval date,i-485 approval date,receipt to interview,interview to i130,interview to i485,i130 to i485,days since interview,days total,case closed
u1,Raleigh/Durham,01-01-2025,02-01-2025,02-03-2025,02-10-2025,31,2,9,7,9,40,YES
"""
    df = load_dataset_csv(csv_text=csv_text)
    assert "i-485 receipt date_dt" in df.columns
    assert "days total_num" in df.columns
    assert "closed" in df.columns
