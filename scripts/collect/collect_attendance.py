"""
Dodgers Road_Attendance (avg attendance per road game, regular season) and
Postseason_Home_Games (postseason games hosted at Dodger Stadium), 2017-2019 & 2022-2025.
Source: MLB Stats API schedule endpoint (statsapi.mlb.com), hydrate=gameInfo for attendance.
"""
from pathlib import Path

import requests
import pandas as pd

DODGERS_ID = 119
SEASONS = [2017, 2018, 2019, 2022, 2023, 2024, 2025]
SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule"
ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "snapshots" / "live"


def get_games(season, game_type):
    r = requests.get(
        SCHEDULE_URL,
        params={"teamId": DODGERS_ID, "season": season, "sportId": 1, "gameType": game_type, "hydrate": "gameInfo"},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    return [g for d in data.get("dates", []) for g in d.get("games", [])]


def main():
    rows = []
    for season in SEASONS:
        print(f"== Season {season} ==")
        reg_games = get_games(season, "R")
        road_games = [g for g in reg_games if g["teams"]["away"]["team"]["id"] == DODGERS_ID]
        attendances = [g.get("gameInfo", {}).get("attendance") for g in road_games]
        attendances = [a for a in attendances if a is not None]
        road_attendance_avg = round(sum(attendances) / len(attendances), 0) if attendances else None

        post_games = []
        for gt in ["F", "D", "L", "W"]:  # Wild Card, Division Series, League Championship, World Series
            post_games.extend(get_games(season, gt))
        post_home_games = sum(1 for g in post_games if g["teams"]["home"]["team"]["id"] == DODGERS_ID)

        rows.append({
            "season": season,
            "team": "LAD",
            "Road_Attendance": road_attendance_avg,
            "road_games_counted": len(attendances),
            "Postseason_Home_Games": post_home_games,
        })
        print(f"  Road_Attendance={road_attendance_avg} ({len(attendances)} games), Postseason_Home_Games={post_home_games}")

    df = pd.DataFrame(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / "attendance_postseason.csv"
    df.to_csv(destination, index=False, encoding="utf-8-sig")
    print(f"Saved {destination.relative_to(ROOT)} ({len(df)} rows)")


if __name__ == "__main__":
    main()
