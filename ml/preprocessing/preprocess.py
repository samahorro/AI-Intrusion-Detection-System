
"""
Reusable preprocessing utilities for CIC-IDS2017 datasets.

This module cleans CIC-IDS2017 network-flow datasets
before feature engineering and machine-learning training.
"""

import numpy as np
import pandas as pd


def preprocess_dataset(df):
    """
    Clean a CIC-IDS2017 DataFrame for machine-learning development.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw CIC-IDS2017 dataset.

    Returns
    -------
    clean_df : pandas.DataFrame
        Cleaned dataset.

    summary : dict
        Preprocessing statistics.
    """

    # -----------------------------------------------
    # 1. Validate input
    # -----------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    # Preserve the original DataFrame
    clean_df = df.copy(deep=True)

    # Record original dataset size
    rows_before = len(clean_df)

    # -----------------------------------------------
    # 2. Standardize column names
    # -----------------------------------------------

    clean_df.columns = clean_df.columns.str.strip()

    # -----------------------------------------------
    # 3. Standardize traffic labels
    # -----------------------------------------------

    if "Label" in clean_df.columns:

        # Preserve missing values during string conversion
        clean_df["Label"] = (
            clean_df["Label"]
            .astype("string")
            .str.strip()
        )

        # Treat empty labels as missing values
        clean_df["Label"] = (
            clean_df["Label"]
            .replace("", pd.NA)
        )

    # -----------------------------------------------
    # 4. Replace infinite values with NaN
    # -----------------------------------------------

    clean_df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    # -----------------------------------------------
    # 5. Record missing-value statistics
    # -----------------------------------------------

    missing_values_before = int(
        clean_df.isna().sum().sum()
    )

    rows_with_missing = int(
        clean_df.isna().any(axis=1).sum()
    )

    # -----------------------------------------------
    # 6. Remove rows containing missing values
    # -----------------------------------------------

    clean_df.dropna(inplace=True)

    # -----------------------------------------------
    # 7. Identify and remove duplicate rows
    # -----------------------------------------------

    duplicates_before = int(
        clean_df.duplicated().sum()
    )

    clean_df.drop_duplicates(inplace=True)

    # -----------------------------------------------
    # 8. Reset row indexes
    # -----------------------------------------------

    clean_df.reset_index(
        drop=True,
        inplace=True
    )

    # -----------------------------------------------
    # 9. Calculate final dataset statistics
    # -----------------------------------------------

    rows_after = len(clean_df)

    rows_removed = rows_before - rows_after

    percent_removed = (
        round(
            (rows_removed / rows_before) * 100,
            2
        )
        if rows_before > 0
        else 0
    )

    # -----------------------------------------------
    # 10. Verify final dataset quality
    # -----------------------------------------------

    numeric_df = clean_df.select_dtypes(
        include=[np.number]
    )

    remaining_missing = int(
        clean_df.isna().sum().sum()
    )

    remaining_infinite = int(
        np.isinf(
            numeric_df.to_numpy()
        ).sum()
    )

    remaining_duplicates = int(
        clean_df.duplicated().sum()
    )

    # -----------------------------------------------
    # 11. Create preprocessing summary
    # -----------------------------------------------

    summary = {
        "rows_before": int(rows_before),
        "rows_after": int(rows_after),
        "rows_removed": int(rows_removed),
        "percent_removed": percent_removed,
        "missing_values_found": missing_values_before,
        "rows_with_missing": rows_with_missing,
        "duplicates_found": duplicates_before,
        "remaining_missing_values": remaining_missing,
        "remaining_infinite_values": remaining_infinite,
        "remaining_duplicates": remaining_duplicates
    }

    return clean_df, summary
