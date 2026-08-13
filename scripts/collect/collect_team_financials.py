"""
LA Dodgers team payroll/financials by season (2017-2019, 2022-2025).
Source: Spotrac team payroll pages (FanGraphs/Baseball-Reference are blocked
in this environment, so payroll figures come from Spotrac's "Payroll Summary" table).
"""
import io
from pathlib import Path
import time
import requests
import pandas as pd

SEASONS = [2017, 2018, 2019, 2022, 2023, 2024, 2025]
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "snapshots" / "live"


def get_payroll_summary(season):
    url = f"https://www.spotrac.com/mlb/los-angeles-dodgers/payroll/{season}/"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    tables = pd.read_html(io.StringIO(r.text))
    summary = None
    for t in tables:
        first_col = t.iloc[:, 0].astype(str)
        if first_col.str.contains("Payroll Summary").any():
            summary = t
            break
    if summary is None:
        return {}
    summary.columns = ["label", "value"] + list(summary.columns[2:])
    result = {}
    for _, row in summary.iterrows():
        label = str(row["label"]).strip()
        value = str(row["value"]).strip().replace("$", "").replace(",", "")
        if label and label != "Payroll Summary" and value not in ("nan", ""):
            try:
                result[label] = int(value)
            except ValueError:
                pass
    return result


def main():
    rows = []
    for season in SEASONS:
        print(f"== Season {season} ==")
        summary = get_payroll_summary(season)
        rows.append({
            "season": season,
            "team": "LAD",
            "active_roster_payroll": summary.get("Active Roster"),
            "injured_list_payroll": summary.get("Injured List"),
            "suspended_restricted_payroll": summary.get("Suspended/Restricted"),
            "dead_money": summary.get("Dead Money"),
            "retained_payroll": summary.get("Retained"),
            "minor_league_payroll": summary.get("Minor"),
            "signing_bonus": summary.get("Signing Bonus"),
            "total_adjusted_payroll": summary.get("Total Adjusted Payroll Allocations"),
        })
        print(f"  total_adjusted_payroll={summary.get('Total Adjusted Payroll Allocations')}")
        time.sleep(0.5)
    df = pd.DataFrame(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / "team_payroll_spotrac.csv"
    df.to_csv(destination, index=False, encoding="utf-8-sig")
    print(f"Saved {destination.relative_to(ROOT)} ({len(df)} rows)")


if __name__ == "__main__":
    main()
