"""Load processed analysis datasets into a reproducible SQLite database."""

from pathlib import Path
import sqlite3

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"
BUILD = ROOT / "build"


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    database = BUILD / "dodgers_analysis.db"
    pitchers = pd.read_csv(DATA / "pitcher_stats.csv", encoding="utf-8-sig")
    teams = pd.read_csv(DATA / "team_financials.csv", encoding="utf-8-sig")

    with sqlite3.connect(database) as connection:
        pitchers.to_sql("pitcher_stats", connection, if_exists="replace", index=False)
        teams.to_sql("team_financials", connection, if_exists="replace", index=False)
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]

    print(f"Built {database.relative_to(ROOT)} (integrity={integrity})")
    print(f"pitcher_stats={len(pitchers)} rows, team_financials={len(teams)} rows")


if __name__ == "__main__":
    main()
