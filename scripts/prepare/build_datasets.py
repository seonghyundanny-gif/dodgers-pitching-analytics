"""Build analysis-ready datasets from the repository's frozen source snapshots.

The snapshots preserve the data used for the published analysis results. Live
collection is intentionally a separate, optional step because upstream APIs and
web tables change over time. This command never mutates the source snapshots.
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOTS = ROOT / "data" / "snapshots"
PROCESSED = ROOT / "data" / "processed"


PITCHER_REQUIRED = {
    "season",
    "player_id",
    "name",
    "Age",
    "IP_decimal",
    "fastball_velo_mph",
    "WAR",
    "IL_days",
    "Postseason_IP",
    "Postseason_WAR_proxy",
}

TEAM_REQUIRED = {
    "season",
    "team",
    "total_adjusted_payroll",
    "CBT_Tax_Paid",
    "Revenue",
    "Operating_Income",
    "Team_Value",
    "Superstar_Era",
}


def require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")


def build_pitcher_data() -> pd.DataFrame:
    source = SNAPSHOTS / "pitcher_stats.csv"
    frame = pd.read_csv(source, encoding="utf-8-sig")
    require_columns(frame, PITCHER_REQUIRED, source.name)

    # Missing IL/proxy values mean no matched closed IL stint or no postseason
    # appearance in the frozen source data. See docs/limitations.md for the
    # implications of this operational definition.
    frame["IL_days"] = frame["IL_days"].fillna(0)
    frame["Postseason_IP"] = frame["Postseason_IP"].fillna(0)
    frame["Postseason_WAR_proxy"] = frame["Postseason_WAR_proxy"].fillna(0)
    frame["low_sample_flag"] = (frame["IP_decimal"] < 5).astype(int)

    output = PROCESSED / "pitcher_stats.csv"
    frame.to_csv(output, index=False, encoding="utf-8-sig")
    return frame


def build_team_data() -> pd.DataFrame:
    source = SNAPSHOTS / "team_financials.csv"
    frame = pd.read_csv(source, encoding="utf-8-sig")
    require_columns(frame, TEAM_REQUIRED, source.name)
    for column in ("suspended_restricted_payroll", "dead_money"):
        if column in frame:
            frame[column] = frame[column].fillna(0)

    output = PROCESSED / "team_financials.csv"
    frame.to_csv(output, index=False, encoding="utf-8-sig")
    return frame


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    pitchers = build_pitcher_data()
    teams = build_team_data()
    print(
        f"Built data/processed/pitcher_stats.csv: {len(pitchers)} rows "
        f"({int(pitchers['low_sample_flag'].sum())} low-sample rows flagged)"
    )
    print(f"Built data/processed/team_financials.csv: {len(teams)} rows")


if __name__ == "__main__":
    main()
