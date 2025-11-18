#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean Mental_Health_Lifestyle_Dataset
- Drops rows with missing values ONLY in essential columns
- Removes rows with unrealistic numeric values
- Normalizes categorical text (strip/case) and filters obviously invalid categories (only where safe)
- Does NOT create extra columns

Usage:
    python clean_mental_health_dataset.py --input Mental_Health_Lifestyle_Dataset.csv --output Mental_Health_Lifestyle_CLEAN.csv
"""

import argparse
import pandas as pd

# -------- realistic numeric bounds (closed intervals) --------
NUMERIC_BOUNDS = {
    "Age": (10, 100),
    "Sleep Hours": (3.0, 12.0),
    "Screen Time per Day (Hours)": (0.0, 10.0),
    "Social Interaction Score": (0.0, 10.0),
    "Happiness Score": (0.0, 10.0),
    "Work Hours per Week": (0, 84),
}

# -------- which columns MUST NOT be missing? --------
# Mental Health Condition ve Diet Type BURADA YOK, yani sadece bunlar boş diye satır silmiyoruz.
ESSENTIAL_NOT_NULL = {
    "Age",
    "Gender",
    "Country",
    "Sleep Hours",
    "Stress Level",
    "Screen Time per Day (Hours)",
    "Social Interaction Score",
    "Work Hours per Week",
    "Happiness Score",
    "Exercise Level",
    "Diet Type",
    "Mental Health Condition",
}

# -------- categorical normalization helpers --------
SAFE_FILTER_SETS = {
    # Keep this conservative to avoid dropping valid data accidentally
    # Use title case after normalization
    "Stress Level": {"Low", "Moderate", "High"},
    "Exercise Level": {"Low", "Moderate", "High"},
    # Allow a broad set for gender to avoid over-filtering real data
    "Gender": {"Male", "Female", "Other", "Non-Binary", "Nonbinary", "Prefer Not To Say"},
}

NORMALIZE_TITLE = {"Gender", "Stress Level", "Exercise Level", "Diet Type", "Mental Health Condition", "Country"}


def normalize_text(s: pd.Series) -> pd.Series:
    """
    Metni normalize ederken NaN'lere dokunma.
    """
    s = s.copy()
    mask = s.notna()
    s.loc[mask] = (
        s.loc[mask]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", required=True, help="Path to input CSV (Mental_Health_Lifestyle_Dataset.csv)")
    ap.add_argument("--output", "-o", required=True, help="Path to output cleaned CSV")
    args = ap.parse_args()

    df = pd.read_csv(args.input, keep_default_na=False)
    initial_rows = len(df)

    # 1) Drop rows with missing values ONLY in essential columns
    existing_essential = [c for c in ESSENTIAL_NOT_NULL if c in df.columns]
    df = df.dropna(subset=existing_essential)
    after_dropna = len(df)

    # 2) Normalize categorical text (no new columns)
    for col in NORMALIZE_TITLE:
        if col in df.columns:
            df[col] = normalize_text(df[col])

    # 3) Filter obviously invalid categorical entries (only where safe and well-defined)
    for col, allowed in SAFE_FILTER_SETS.items():
        if col in df.columns:
            df = df[df[col].isin(allowed)]
    after_categorical = len(df)

    # 4) Enforce numeric bounds (remove unrealistic rows)
    for col, (lo, hi) in NUMERIC_BOUNDS.items():
        if col in df.columns:
            df = df[df[col].between(lo, hi, inclusive="both")]
    after_numeric = len(df)

    # 5) Save
    df.to_csv(args.output, index=False)

    # 6) Simple report
    print("=== Cleaning Report ===")
    print(f"Input rows:            {initial_rows}")
    print(f"After dropna (essential cols only): {after_dropna}")
    print(f"After categorical fix: {after_categorical}")
    print(f"After numeric bounds:  {after_numeric}")
    print(f"Output saved to:       {args.output}")


if __name__ == "__main__":
    main()


