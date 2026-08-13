"""Fail fast when project datasets drift from the documented analysis sample."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"
EXPECTED_SEASONS = {2017, 2018, 2019, 2022, 2023, 2024, 2025}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    pitchers = pd.read_csv(DATA / "pitcher_stats.csv", encoding="utf-8-sig")
    teams = pd.read_csv(DATA / "team_financials.csv", encoding="utf-8-sig")
    peers = pd.read_csv(DATA / "comparable_teams_financials.csv", encoding="utf-8-sig")

    check(len(pitchers) == 221, "Expected 221 pitcher-season rows")
    check(pitchers.loc[pitchers["low_sample_flag"] == 0].shape[0] == 184,
          "Expected 184 analysis pitcher-seasons")
    check(pitchers.loc[pitchers["low_sample_flag"] == 0, "player_id"].nunique() == 106,
          "Expected 106 unique pitchers in the analysis sample")
    check(set(pitchers["season"]) == EXPECTED_SEASONS, "Unexpected pitcher seasons")
    check(not pitchers.duplicated(["season", "player_id"]).any(),
          "Duplicate pitcher-season rows found")
    check(pitchers["fastball_velo_mph"].between(80, 105).all(),
          "Fastball velocity outside plausible bounds")
    check((pitchers["IL_days"] >= 0).all(), "Negative IL days found")

    check(len(teams) == 7, "Expected seven Dodgers team-season rows")
    check(set(teams["season"]) == EXPECTED_SEASONS, "Unexpected financial seasons")
    check(len(peers) == 60 and peers["team"].nunique() == 6,
          "Expected a balanced 6-team x 10-season comparison panel")
    check(peers.groupby("team")["season"].nunique().eq(10).all(),
          "Comparison panel is not balanced")

    print("Data validation passed")
    print("pitcher-seasons=221, analysis rows=184, unique pitchers=106")
    print("team financial seasons=7, comparison panel rows=60")


if __name__ == "__main__":
    main()
