from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


@pytest.fixture(scope="session")
def pitcher_stats() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "pitcher_stats.csv", encoding="utf-8-sig")


@pytest.fixture(scope="session")
def team_financials() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "team_financials.csv", encoding="utf-8-sig")


@pytest.fixture(scope="session")
def comparison_panel() -> pd.DataFrame:
    return pd.read_csv(
        PROCESSED / "comparable_teams_financials.csv", encoding="utf-8-sig"
    )


@pytest.fixture(scope="session")
def did_results() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "did_regression_results.csv", encoding="utf-8-sig")
