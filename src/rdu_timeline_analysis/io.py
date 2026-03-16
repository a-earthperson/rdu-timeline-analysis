from __future__ import annotations

import io
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

MISSING_TOKENS = {"?", "FUTURE", "N/A", "#VALUE!", ""}

DATE_COLS = [
    "i-485 receipt date",
    "interview date",
    "i-130 approval date",
    "i-485 approval date",
]
NUMERIC_COLS = [
    "receipt to interview",
    "interview to i130",
    "interview to i485",
    "i130 to i485",
    "days since interview",
    "days total",
]

CANONICAL_REQUIRED_COLUMNS = [
    "user",
    "field_office",
    "i-485 receipt date",
    "interview date",
    "i-130 approval date",
    "i-485 approval date",
    "receipt to interview",
    "interview to i130",
    "interview to i485",
    "i130 to i485",
    "days since interview",
    "days total",
    "case closed",
]


def parse_date(value: object, fmt: str = "%m-%d-%Y") -> pd.Timestamp:
    """Parse date strings and return NaT for sentinel/malformed values."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return pd.NaT
    s = str(value).strip()
    if s in MISSING_TOKENS:
        return pd.NaT
    return pd.to_datetime(s, format=fmt, errors="coerce")


def parse_num(value: object) -> float:
    """Parse numeric values and return NaN for sentinel/malformed values."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    s = str(value).strip()
    if s in MISSING_TOKENS:
        return np.nan
    try:
        return float(s)
    except Exception:
        return np.nan


def load_dataset_csv(
    csv_path: Optional[str] = None, csv_text: Optional[str] = None
) -> pd.DataFrame:
    """Load CSV from path/text and add parsed helper columns used by the pipeline."""
    if (csv_path is None) == (csv_text is None):
        raise ValueError("Provide exactly one of csv_path or csv_text.")

    if csv_path is not None:
        df = pd.read_csv(csv_path)
    else:
        df = pd.read_csv(io.StringIO(csv_text))

    for c in DATE_COLS:
        if c in df.columns:
            df[f"{c}_dt"] = df[c].apply(parse_date)
    for c in NUMERIC_COLS:
        if c in df.columns:
            df[f"{c}_num"] = df[c].apply(parse_num)

    df["closed"] = df["case closed"].astype(str).str.upper().eq("YES")
    df["receipt_year"] = df["i-485 receipt date_dt"].dt.year
    df["receipt_month"] = df["i-485 receipt date_dt"].dt.to_period("M")
    df["receipt_quarter"] = df["i-485 receipt date_dt"].dt.to_period("Q")
    df["interview_year"] = df["interview date_dt"].dt.year
    df["interview_month"] = df["interview date_dt"].dt.to_period("M")
    df["interview_quarter"] = df["interview date_dt"].dt.to_period("Q")
    return df


def load_canonical_dataset(path: str | Path) -> pd.DataFrame:
    """Load canonical dataset from disk."""
    return load_dataset_csv(csv_path=str(path))
