#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean Mental_Health_Lifestyle_Dataset
- Drops rows with any missing values
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
    "Screen Time per Day (Hours)": (0.0, 20.0),
    "Social Interaction Score": (0.0, 10.0),
    "Happiness Score": (0.0, 10.0),
    "Work Hours per Week": (0, 120),
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
    return (
        s.astype(str)
         .str.strip()
         .str.replace(r"\s+", " ", regex=True)
         .str.title()
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", required=True, help="Path to input CSV (Mental_Health_Lifestyle_Dataset.csv)")
    ap.add_argument("--output", "-o", required=True, help="Path to output cleaned CSV")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    initial_rows = len(df)

    # 1) Drop rows with ANY missing values
    df = df.dropna()
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
    print(f"After dropna:          {after_dropna}")
    print(f"After categorical fix: {after_categorical}")
    print(f"After numeric bounds:  {after_numeric}")
    print(f"Output saved to:       {args.output}")

if __name__ == "__main__":
    main()
