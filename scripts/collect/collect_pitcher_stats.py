"""
LA Dodgers pitcher stats collector (2017-2019, 2022-2025).

Data source notes (this environment cannot reach FanGraphs / Baseball-Reference,
both return HTTP 403 here, so pybaseball.pitching_stats() / pitching_stats_bref()
do not work):
  - IP, K%, ERA          -> MLB Stats API (statsapi.mlb.com)
  - Fastball velocity    -> Baseball Savant / Statcast via pybaseball
  - WAR                  -> NOT AVAILABLE (FanGraphs/BBRef only, blocked) -> NaN
  - IL days              -> NOT AVAILABLE (no source reachable here) -> NaN
"""
from pathlib import Path
import time
import requests
import pandas as pd
from pybaseball import statcast_pitcher

DODGERS_ID = 119
SEASONS = [2017, 2018, 2019, 2022, 2023, 2024, 2025]
STATSAPI = "https://statsapi.mlb.com/api/v1"
ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "snapshots" / "live"


def get_season_roster_pitchers(season):
    """All pitchers who appeared for the Dodgers in a season (40-man + roster history)."""
    url = f"{STATSAPI}/teams/{DODGERS_ID}/roster"
    r = requests.get(url, params={"rosterType": "fullSeason", "season": season}, timeout=20)
    r.raise_for_status()
    data = r.json()
    pitchers = []
    for p in data.get("roster", []):
        if p["position"]["type"] == "Pitcher":
            pitchers.append({"player_id": p["person"]["id"], "name": p["person"]["fullName"]})
    return pitchers


def get_pitching_stats(player_id, season):
    url = f"{STATSAPI}/people/{player_id}/stats"
    r = requests.get(url, params={"stats": "season", "group": "pitching", "season": season}, timeout=20)
    r.raise_for_status()
    data = r.json()
    splits = data.get("stats", [{}])[0].get("splits", [])
    for s in splits:
        if s.get("team", {}).get("id") == DODGERS_ID:
            return s["stat"]
    return None


def get_fastball_velocity(player_id, season):
    """Average four-seam/sinker velocity for the season from Statcast pitch-level data."""
    start = f"{season}-03-01"
    end = f"{season}-11-30"
    try:
        df = statcast_pitcher(start, end, player_id)
    except Exception:
        return None
    if df is None or df.empty:
        return None
    fb = df[df["pitch_type"].isin(["FF", "SI"])]
    if fb.empty or "release_speed" not in fb.columns:
        return None
    return round(fb["release_speed"].dropna().mean(), 1)


def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", "replace").decode())


def main():
    rows = []
    for season in SEASONS:
        print(f"== Season {season} ==")
        pitchers = get_season_roster_pitchers(season)
        for p in pitchers:
            stat = get_pitching_stats(p["player_id"], season)
            if stat is None:
                continue
            velo = get_fastball_velocity(p["player_id"], season)
            ip = stat.get("inningsPitched")
            strikeouts = stat.get("strikeOuts")
            batters_faced = stat.get("battersFaced")
            k_pct = round(100 * strikeouts / batters_faced, 1) if strikeouts is not None and batters_faced else None
            rows.append({
                "season": season,
                "player_id": p["player_id"],
                "name": p["name"],
                "team": "LAD",
                "IP": ip,
                "K_pct": k_pct,
                "ERA": stat.get("era"),
                "fastball_velo_mph": velo,
                "WAR": None,      # not available: FanGraphs/BBRef blocked in this environment
                "IL_days": None,  # not available: no reachable source for injury-list days
            })
            safe_print(f"  {p['name']}: IP={ip} K%={k_pct} velo={velo}")
            time.sleep(0.3)
    df = pd.DataFrame(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / "pitcher_stats_mlb_savant.csv"
    df.to_csv(destination, index=False, encoding="utf-8-sig")
    print(f"Saved {destination.relative_to(ROOT)} ({len(df)} rows)")


if __name__ == "__main__":
    main()
