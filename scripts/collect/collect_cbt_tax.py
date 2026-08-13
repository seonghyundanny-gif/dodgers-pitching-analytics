"""
LA Dodgers Competitive Balance Tax (luxury tax) paid by season, 2017-2019 & 2022-2025.
Source: Spotrac team tax pages (year-specific URLs).
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


def get_tax_summary(season):
    url = f"https://www.spotrac.com/mlb/los-angeles-dodgers/tax/{season}/"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    tables = pd.read_html(io.StringIO(r.text))
    summary = None
    for t in tables:
        if t.shape[1] == 3 and t.iloc[:, 0].astype(str).str.contains("Tax Payroll|Tax Bill|Threshold").any():
            summary = t
            break
    if summary is None:
        return {}
    result = {}
    for _, row in summary.iterrows():
        label = str(row.iloc[0]).strip()
        value = str(row.iloc[1]).strip().replace("$", "").replace(",", "")
        try:
            result[label] = int(value)
        except ValueError:
            pass
    return result


def main():
    rows = []
    for season in SEASONS:
        print(f"== Season {season} ==")
        summary = get_tax_summary(season)
        tax_bill = None
        for k, v in summary.items():
            if "Tax Bill" in k:
                tax_bill = v
                break
        rows.append({
            "season": season,
            "team": "LAD",
            "cbt_threshold": summary.get("Competitive Balance Tax Threshold"),
            "tax_payroll": summary.get("Final Tax Payroll") or summary.get("Tax Payroll") or summary.get("Projected Tax Payroll"),
            "CBT_Tax_Paid": tax_bill,
        })
        print(f"  CBT_Tax_Paid={tax_bill}")
        time.sleep(0.5)
    df = pd.DataFrame(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / "cbt_tax.csv"
    df.to_csv(destination, index=False, encoding="utf-8-sig")
    print(f"Saved {destination.relative_to(ROOT)} ({len(df)} rows)")


if __name__ == "__main__":
    main()
