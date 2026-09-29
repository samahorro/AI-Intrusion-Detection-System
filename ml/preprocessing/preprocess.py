"""
Reusable preprocessing utilities for CIC-IDS2017 datasets.
"""

import numpy as np
import pandas as pd


def preprocess_dataset(df):
    """
    Clean a CIC-IDS2017 DataFrame for feature engineering
    and machine-learning development.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw CIC-IDS2017 DataFrame.

    Returns
    -------
    clean_df : pandas.DataFrame
        Cleaned DataFrame.

    summary : dict
        Basic preprocessing statistics.
    """

    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    # Preserve the original DataFrame
    clean_df = df.copy()

    # -----------------------------------------------
    # Record initial dataset size
    # -----------------------------------------------

    rows_before = clean_df.shape[0]

    # -----------------------------------------------
    # Standardize column names
    # -----------------------------------------------

    clean_df.columns = clean_df.columns.str.strip()

    # -----------------------------------------------
    # Standardize traffic labels
    # -----------------------------------------------

    if "Label" in clean_df.columns:
        clean_df["Label"] = (
            clean_df["Label"]
            .astype(str)
            .str.strip()
        )

    # -----------------------------------------------
    # Replace infinite values with NaN
    # -----------------------------------------------

    clean_df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    # Count invalid/missing values before removal
    missing_values_before = (
        clean_df
        .isnull()
        .sum()
        .sum()
    )

    rows_with_missing = (
        clean_df
        .isnull()
        .any(axis=1)
        .sum()
    )

    # -----------------------------------------------
    # Remove rows containing missing values
    # -----------------------------------------------

    clean_df.dropna(inplace=True)

    # -----------------------------------------------
    # Remove exact duplicate rows
    # -----------------------------------------------

    duplicates_before = (
        clean_df
        .duplicated()
        .sum()
    )

    clean_df.drop_duplicates(
        inplace=True
    )

    # -----------------------------------------------
    # Reset row indexes
    # -----------------------------------------------

    clean_df.reset_index(
        drop=True,
        inplace=True
    )

    # -----------------------------------------------
    # Final dataset statistics
    # -----------------------------------------------

    rows_after = clean_df.shape[0]

    rows_removed = (
        rows_before - rows_after
    )

    percent_removed = (
        (rows_removed / rows_before) * 100
        if rows_before > 0
        else 0
    )

    # -----------------------------------------------
    # Verify final data quality
    # -----------------------------------------------

    numeric_df = clean_df.select_dtypes(
        include=[np.number]
    )

    remaining_missing = (
        clean_df
        .isnull()
        .sum()
        .sum()
    )

    remaining_infinite = (
        np.isinf(numeric_df)
        .sum()
        .sum()
    )

    remaining_duplicates = (
        clean_df
        .duplicated()
        .sum()
    )

    # -----------------------------------------------
    # Create preprocessing summary
    # -----------------------------------------------

    summary = {
        "rows_before": int(rows_before),
        "rows_after": int(rows_after),
        "rows_removed": int(rows_removed),
        "percent_removed": round(
            percent_removed,
            2
        ),
        "missing_values_found":
            int(missing_values_before),
        "rows_with_missing":
            int(rows_with_missing),
        "duplicates_found":
            int(duplicates_before),
        "remaining_missing_values":
            int(remaining_missing),
        "remaining_infinite_values":
            int(remaining_infinite),
        "remaining_duplicates":
            int(remaining_duplicates)
    }

    return clean_df, summary