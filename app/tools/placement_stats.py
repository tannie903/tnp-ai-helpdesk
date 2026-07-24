"""
app/tools/placement_stats.py

Handles AGGREGATE / CALCULATION style placement questions using pandas
directly on the ground-truth DataFrame. No LLM guessing, no retriever,
no top-k truncation. This is deterministic and always correct relative
to the source sheet (app/data/TNP_Placement_Data.xlsx).

Handles: totals, sums, counts, averages, highest/lowest, per-branch
filters, and simple company lookups by exact name.
"""

from data.stats_loader import get_stats_df


AGGREGATE_KEYWORDS = [
    "total", "how many", "sum", "average", "avg", "highest", "lowest",
    "maximum", "max", "minimum", "min", "compare", "count", "overall",
    "all companies", "across", "combined", "stats", "statistics",
    "breakdown", "list", "department", "dept",
]

BRANCH_ALIASES = {
    "cse": "CSE", "computer science": "CSE",
    "ece": "ECE", "electronics": "ECE",
    "it": "IT", "information technology": "IT",
    "mae": "MAE", "mechanical": "MAE",
    "ai_ds": "AI_DS", "ai-ds": "AI_DS", "ai ds": "AI_DS", "data science": "AI_DS",
}


def is_aggregate_query(user_query: str) -> bool:
    """
    Cheap, fast keyword check to decide: does this need pandas computation,
    or is it a simple lookup better served by RAG?
    """
    q = user_query.lower()
    return any(kw in q for kw in AGGREGATE_KEYWORDS)


def _extract_branch(user_query: str):
    q = user_query.lower()
    for alias, branch_code in BRANCH_ALIASES.items():
        if alias in q:
            return branch_code
    return None


def _filter_by_branch(df, branch_code):
    if branch_code is None:
        return df
    return df[df["branch_list"].apply(lambda lst: branch_code in lst)]


def compute_answer(user_query: str) -> str:
    """
    Runs the actual pandas computation and returns a plain-language
    answer string. This string is ground truth — it can be handed to the
    LLM just to phrase nicely, or returned directly.
    """
    df = get_stats_df()
    q = user_query.lower()

    branch_code = _extract_branch(user_query)
    scoped_df = _filter_by_branch(df, branch_code)
    scope_label = f" in {branch_code}" if branch_code else ""

    if scoped_df.empty:
        return f"I don't have any placement data{scope_label} to compute that."

    # --- Full breakdown / stats for a branch/department ("stats of IT department") ---
    if any(kw in q for kw in ["stats", "statistics", "breakdown", "list", "department", "dept"]):
        TOP_N = 15  # deliberately capped for readability; total below always reflects ALL companies, not just shown ones
        sorted_df = scoped_df.sort_values("students_placed", ascending=False)

        lines = []
        for _, row in sorted_df.head(TOP_N).iterrows():
            avg = row["avg_ctc"] if row["avg_ctc"] == row["avg_ctc"] else "Not Disclosed"
            lines.append(f"{row['company']}: {int(row['students_placed'])} students placed, Average CTC (LPA): {avg}")

        total = int(scoped_df["students_placed"].sum())
        num_companies = scoped_df["company"].nunique()
        body = "\n".join(f"- {line}" for line in lines)

        remaining = num_companies - len(lines)
        more_note = f"\n- ...and {remaining} more companies" if remaining > 0 else ""

        label = branch_code if branch_code else "all departments"
        return (
            f"Placement stats for {label} (top {len(lines)} by students placed):\n"
            f"{body}{more_note}\n\n"
            f"Total students placed: {total} (across {num_companies} companies)."
        )

    # --- Total students placed ---
    if "total" in q and ("student" in q or "placed" in q):
        total = int(scoped_df["students_placed"].sum())
        num_companies = scoped_df["company"].nunique()
        return (
            f"Total students placed{scope_label}: {total} "
            f"(across {num_companies} companies)."
        )

    # --- How many companies visited ---
    if "how many" in q and "compan" in q:
        num_companies = scoped_df["company"].nunique()
        return f"{num_companies} companies visited{scope_label}."

    # --- Average CTC across companies (accepts salary/package/offer/pay as synonyms) ---
    CTC_SYNONYMS = ["ctc", "salary", "package", "offer", "pay", "stipend"]
    if ("average" in q or "avg" in q) and any(syn in q for syn in CTC_SYNONYMS):
        avg = scoped_df["avg_ctc"].dropna().mean()
        if avg is None or avg != avg:  # NaN check
            return f"Average CTC data isn't fully disclosed{scope_label}, so I can't compute an accurate average."
        return f"Average CTC{scope_label}: {avg:.2f} LPA (across companies with disclosed CTC)."

    # --- Highest CTC / highest paying company (accepts salary/package/offer/pay as synonyms for CTC) ---
    if "highest" in q and any(syn in q for syn in CTC_SYNONYMS):
        row = scoped_df.loc[scoped_df["highest_ctc"].idxmax()]
        return f"Highest CTC{scope_label}: {row['company']} at {row['highest_ctc']} LPA."

    # --- Lowest CTC (same synonym handling) ---
    if "lowest" in q and any(syn in q for syn in CTC_SYNONYMS):
        row = scoped_df.loc[scoped_df["lowest_ctc"].idxmin()]
        return f"Lowest CTC{scope_label}: {row['company']} at {row['lowest_ctc']} LPA."

    # --- Students placed at a specific company ---
    for _, row in scoped_df.iterrows():
        if row["company"].lower() in q:
            return (
                f"{row['company']}: {int(row['students_placed'])} students placed, "
                f"Average CTC: {row['avg_ctc'] if row['avg_ctc'] == row['avg_ctc'] else 'Not Disclosed'} LPA."
            )

    # --- Fallback: generic total, since query matched aggregate keywords but no specific pattern ---
    total = int(scoped_df["students_placed"].sum())
    return f"Total students placed{scope_label}: {total} (across {scoped_df['company'].nunique()} companies)."