"""Exploratory H2 before/after comparison with the extended team history."""

from pathlib import Path

import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[2]
TEAM_HISTORY = ROOT / "data" / "snapshots" / "team_financials_extended.csv"
METRICS = [
    "CBT_Tax_Paid",
    "Injured_Salary_Loss",
    "Postseason_Home_Games",
    "total_adjusted_payroll",
    "Road_Attendance",
]


def main() -> None:
    team = pd.read_csv(TEAM_HISTORY, encoding="utf-8-sig")
    before = team.loc[team["Superstar_Era"].eq(0)]
    after = team.loc[team["Superstar_Era"].eq(1)]

    print(
        f"Seasons: {len(team)} (before={len(before)}, after={len(after)}); "
        "Welch tests are exploratory because the after sample is very small."
    )
    for metric in METRICS:
        result = stats.ttest_ind(after[metric], before[metric], equal_var=False, nan_policy="omit")
        print(
            f"{metric}: before={before[metric].mean():,.1f}, "
            f"after={after[metric].mean():,.1f}, t={result.statistic:.2f}, "
            f"p={result.pvalue:.3f}"
        )


if __name__ == "__main__":
    main()
