from __future__ import annotations

import pandas as pd

from rdu_timeline_analysis.io import load_dataset_csv
from rdu_timeline_analysis.models import build_tte_interview_to_i485_days, build_tte_total_days


CSV_TEXT = """user,field_office,i-485 receipt date,interview date,i-130 approval date,i-485 approval date,receipt to interview,interview to i130,interview to i485,i130 to i485,days since interview,days total,case closed
closed_case,Raleigh/Durham,01-01-2025,02-01-2025,02-03-2025,02-10-2025,31,2,9,7,9,40,YES
open_case,Raleigh/Durham,01-15-2025,03-01-2025,?,FUTURE,45,?,?,?,10,80,NO
"""


def test_total_tte_marks_events_and_censors() -> None:
    df = load_dataset_csv(csv_text=CSV_TEXT)
    tte = build_tte_total_days(df, today=pd.Timestamp("2025-04-01"))
    assert set(tte["event"]) == {0, 1}
    assert len(tte) == 2


def test_interview_tte_handles_pending() -> None:
    df = load_dataset_csv(csv_text=CSV_TEXT)
    tte = build_tte_interview_to_i485_days(df, today=pd.Timestamp("2025-04-01"))
    assert len(tte) == 2
    assert (tte["t"] >= 0).all()
