"""Clean the raw six-team financial panel used for Diff-in-Differences."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "raw" / "financials" / "comparable_teams_financials_raw.csv"
OUTPUT = ROOT / "data" / "processed" / "comparable_teams_financials.csv"
COLS = [
    "team_raw", "season", "Team_Value", "Revenue", "Operating_Income",
    "OI_Margin_Pct", "Player_Expenses_External", "Player_Exp_Pct",
    "Win_Player_Cost_Ratio", "Seating_Capacity", "Avg_Ticket_Price",
]
TEAM_MAP = {
    "LA Dogers": "LAD", "Yankees": "NYY", "Boston": "BOS", "Metz": "NYM",
    "Chicago Cubs": "CHC", "San Francisco Giants": "SFG",
}


def main() -> None:
    raw = pd.read_csv(SOURCE, header=0, names=COLS, encoding="utf-8-sig")
    required_money_cols = [
        "Team_Value", "Revenue", "Operating_Income", "Player_Expenses_External",
    ]
    for column in required_money_cols:
        raw[column] = pd.to_numeric(
            raw[column].astype(str).str.replace(",", "", regex=False), errors="raise"
        )
    # Peer seating-capacity and ticket-price fields were not supplied for every
    # team. They are descriptive metadata, not DiD outcomes, so preserve them
    # as missing numeric values instead of rejecting an otherwise valid panel.
    raw["Seating_Capacity"] = pd.to_numeric(
        raw["Seating_Capacity"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )
    for column in ["OI_Margin_Pct", "Player_Exp_Pct"]:
        raw[column] = pd.to_numeric(
            raw[column].astype(str).str.replace("%", "", regex=False), errors="raise"
        ) / 100
    for column in ["Win_Player_Cost_Ratio", "Avg_Ticket_Price"]:
        raw[column] = pd.to_numeric(raw[column], errors="coerce")

    raw["season"] = raw["season"].astype(int)
    raw["team"] = raw["team_raw"].map(TEAM_MAP)
    unmapped = sorted(raw.loc[raw["team"].isna(), "team_raw"].dropna().unique())
    if unmapped:
        raise ValueError(f"Unmapped team names: {unmapped}")
    raw["Treat"] = raw["team"].eq("LAD").astype(int)
    raw["Post"] = raw["season"].ge(2024).astype(int)
    raw["Treat_Post"] = raw["Treat"] * raw["Post"]

    output_cols = [
        "team", "season", "Treat", "Post", "Treat_Post", "Team_Value", "Revenue",
        "Operating_Income", "OI_Margin_Pct", "Player_Expenses_External",
        "Player_Exp_Pct", "Win_Player_Cost_Ratio", "Seating_Capacity", "Avg_Ticket_Price",
    ]
    panel = raw[output_cols].sort_values(["team", "season"]).reset_index(drop=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(
        f"Saved {OUTPUT.relative_to(ROOT)}: {len(panel)} rows, "
        f"{panel['team'].nunique()} teams, {panel['season'].min()}-{panel['season'].max()}"
    )


if __name__ == "__main__":
    main()
