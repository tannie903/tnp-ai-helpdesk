"""
data/stats_loader.py

Loads the placement statistics sheet into a pandas DataFrame ONCE and
caches it, mirroring the pattern used by retriever_singleton.py.

This DataFrame is the "ground truth" used for any aggregation/calculation
query (totals, sums, averages, comparisons, counts). RAG/vector search is
never used for these — pandas does exact computation instead.

NOTE: data/ must have an __init__.py for this import path to work:
    from data.stats_loader import get_stats_df
"""

import pandas as pd
import os

_df_cache = None

# Since this file now lives inside data/ alongside the sheet itself,
# the path is just the filename (still relative to repo root when run).
DATA_PATH = os.getenv("PLACEMENT_DATA_PATH", "data/TNP_Placement_Data.xlsx")

# Map your real column names here if they differ from the sheet in your screenshot
COLUMN_MAP = {
    "Company": "company",
    "Students Placed": "students_placed",
    "Average CTC (LPA)": "avg_ctc",
    "Highest CTC (LPA)": "highest_ctc",
    "Lowest CTC (LPA)": "lowest_ctc",
    "Branches": "branches",
    "Year": "year",
}


def _clean_numeric(series: pd.Series) -> pd.Series:
    """Convert 'Not Disclosed' / blanks to NaN, keep numbers numeric."""
    return pd.to_numeric(series, errors="coerce")


def get_stats_df() -> pd.DataFrame:
    """
    Returns the cached placement stats DataFrame, loading it from disk
    on first call only.
    """
    global _df_cache

    if _df_cache is not None:
        return _df_cache

    df = pd.read_excel(DATA_PATH, header=3)  # rows 0-2 are title/description/blank; real headers are row index 3
    df = df.rename(columns=COLUMN_MAP)

    # Clean numeric columns — "Not Disclosed" becomes NaN, not a string
    for col in ["students_placed", "avg_ctc", "highest_ctc", "lowest_ctc"]:
        if col in df.columns:
            df[col] = _clean_numeric(df[col])

    # Normalize branches into a list per row, e.g. "CSE, ECE, IT" -> ["CSE","ECE","IT"]
    if "branches" in df.columns:
        df["branch_list"] = df["branches"].astype(str).apply(
            lambda s: [b.strip().upper() for b in s.split(",")]
        )

    _df_cache = df
    return df


def reload_stats_df() -> pd.DataFrame:
    """Force a fresh reload from disk (e.g. after the source sheet is updated)."""
    global _df_cache
    _df_cache = None
    return get_stats_df()