from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .io import CANONICAL_REQUIRED_COLUMNS, parse_date, parse_num


@dataclass(frozen=True)
class ValidationConfig:
    duration_tolerance_days: float = 1.0
    allowed_case_closed: tuple[str, ...] = ("YES", "NO")


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_canonical_dataset(df: pd.DataFrame, config: ValidationConfig | None = None) -> list[str]:
    """Validate canonical dataset contract. Returns list of error strings."""
    cfg = config or ValidationConfig()
    errors: list[str] = []

    missing_columns = [c for c in CANONICAL_REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        _add_error(errors, f"Missing required columns: {missing_columns}")
        return errors

    closed_series = df["case closed"].astype(str).str.upper()
    bad_closed = ~closed_series.isin(cfg.allowed_case_closed)
    if bad_closed.any():
        _add_error(errors, f"Invalid values in `case closed` at rows: {list(df.index[bad_closed])}")

    sentinel_tokens = {"?", "FUTURE", "N/A", "#VALUE!", ""}
    for col in ("i-485 receipt date", "interview date", "i-130 approval date", "i-485 approval date"):
        parsed = df[col].apply(parse_date)
        raw = df[col]
        raw_text = raw.astype(str).str.strip()
        malformed = raw.notna() & ~raw_text.isin(sentinel_tokens) & parsed.isna()
        if malformed.any():
            _add_error(errors, f"Malformed date values in `{col}` at rows: {list(df.index[malformed])}")

    receipt_dt = df["i-485 receipt date"].apply(parse_date)
    approval_dt = df["i-485 approval date"].apply(parse_date)
    interview_dt = df["interview date"].apply(parse_date)

    closed_yes = closed_series.eq("YES")
    closed_no = closed_series.eq("NO")

    inconsistent_closed = closed_yes & approval_dt.isna()
    if inconsistent_closed.any():
        _add_error(errors, f"`case closed=YES` with missing approval date at rows: {list(df.index[inconsistent_closed])}")

    inconsistent_open = closed_no & approval_dt.notna()
    if inconsistent_open.any():
        _add_error(errors, f"`case closed=NO` with present approval date at rows: {list(df.index[inconsistent_open])}")

    impossible_total = receipt_dt.notna() & approval_dt.notna() & ((approval_dt - receipt_dt).dt.days < 0)
    if impossible_total.any():
        _add_error(errors, f"Approval date precedes receipt date at rows: {list(df.index[impossible_total])}")

    impossible_interview = interview_dt.notna() & approval_dt.notna() & ((approval_dt - interview_dt).dt.days < 0)
    if impossible_interview.any():
        _add_error(errors, f"Approval date precedes interview date at rows: {list(df.index[impossible_interview])}")

    derived_total = (approval_dt - receipt_dt).dt.days.astype("float64")
    supplied_total = df["days total"].apply(parse_num)
    check_total = derived_total.notna() & supplied_total.notna()
    total_diff = np.abs(derived_total[check_total] - supplied_total[check_total])
    bad_total = check_total.copy()
    bad_total.loc[check_total] = total_diff > cfg.duration_tolerance_days
    if bad_total.any():
        _add_error(errors, f"`days total` mismatch from derived values at rows: {list(df.index[bad_total])}")

    derived_i2i485 = (approval_dt - interview_dt).dt.days.astype("float64")
    supplied_i2i485 = df["interview to i485"].apply(parse_num)
    check_i2i485 = derived_i2i485.notna() & supplied_i2i485.notna()
    i2i485_diff = np.abs(derived_i2i485[check_i2i485] - supplied_i2i485[check_i2i485])
    bad_i2i485 = check_i2i485.copy()
    bad_i2i485.loc[check_i2i485] = i2i485_diff > cfg.duration_tolerance_days
    if bad_i2i485.any():
        _add_error(errors, f"`interview to i485` mismatch from derived values at rows: {list(df.index[bad_i2i485])}")

    dup_keys = df[["user", "i-485 receipt date"]].astype(str).agg("|".join, axis=1).duplicated(keep=False)
    if dup_keys.any():
        _add_error(errors, f"Duplicate user+receipt rows detected at rows: {list(df.index[dup_keys])}")

    return errors


def assert_valid_canonical_dataset(df: pd.DataFrame, config: ValidationConfig | None = None) -> None:
    errors = validate_canonical_dataset(df, config=config)
    if errors:
        msg = "\n".join(f"- {x}" for x in errors)
        raise ValueError(f"Canonical dataset validation failed:\n{msg}")
