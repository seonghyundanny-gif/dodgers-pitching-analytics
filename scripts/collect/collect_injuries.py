"""Collect Dodgers IL transactions and reconstruct injury-list stints.

This is an optional live-data utility. Published results use the frozen files in
``data/snapshots`` so they remain reproducible when the MLB API changes.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from pathlib import Path
import re

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "snapshots" / "live"
DODGERS_ID = 119
SEASONS = [2017, 2018, 2019, 2022, 2023, 2024, 2025]
STATSAPI = "https://statsapi.mlb.com/api/v1/transactions"

PLACE_RE = re.compile(
    r"placed (?P<pos>\S+) (?P<name>.+?) on the (?:\d+-day )?(?:injured|disabled) list"
    r"(?: retroactive to (?P<retro>\w+ \d+, \d{4}))?",
    re.IGNORECASE,
)
ACTIVATE_RE = re.compile(
    r"activated (?P<pos>\S+) (?P<name>.+?) from the "
    r"(?:\d+-day )?(?:injured|disabled) list",
    re.IGNORECASE,
)


def fetch_transactions(season: int) -> list[dict]:
    response = requests.get(
        STATSAPI,
        params={
            "teamId": DODGERS_ID,
            "startDate": f"{season}-01-01",
            "endDate": f"{season}-12-31",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("transactions", [])


def parse_il_stints(
    transactions: Iterable[dict], season_end: str
) -> list[dict[str, object]]:
    """Pair placement/activation events; right-censor open stints at season end."""
    events: list[dict[str, str]] = []
    for transaction in transactions:
        description = transaction.get("description", "")
        transaction_date = transaction.get("date")
        placed = PLACE_RE.search(description)
        if placed:
            start = transaction_date
            if placed.group("retro"):
                try:
                    start = pd.Timestamp(placed.group("retro")).strftime("%Y-%m-%d")
                except ValueError:
                    pass
            events.append(
                {"date": start, "name": placed.group("name").strip(), "action": "placed"}
            )
            continue
        activated = ACTIVATE_RE.search(description)
        if activated:
            events.append(
                {
                    "date": transaction_date,
                    "name": activated.group("name").strip(),
                    "action": "activated",
                }
            )

    events.sort(key=lambda event: (event["date"], event["action"] == "placed"))
    open_stints: dict[str, str] = {}
    stints: list[dict[str, object]] = []
    for event in events:
        name = event["name"]
        if event["action"] == "placed":
            # Duplicate placements are common in transaction text. Do not
            # overwrite an earlier unmatched start date.
            open_stints.setdefault(name, event["date"])
        elif name in open_stints:
            start = open_stints.pop(name)
            stints.append(
                {
                    "name": name,
                    "start_date": start,
                    "end_date": event["date"],
                    "right_censored": False,
                }
            )

    for name, start in open_stints.items():
        stints.append(
            {
                "name": name,
                "start_date": start,
                "end_date": season_end,
                "right_censored": True,
            }
        )
    return stints


def main() -> None:
    rows: list[dict[str, object]] = []
    for season in SEASONS:
        stints = parse_il_stints(fetch_transactions(season), f"{season}-12-31")
        for stint in stints:
            start = pd.Timestamp(stint["start_date"])
            end = pd.Timestamp(stint["end_date"])
            rows.append(
                {
                    "season": season,
                    "name": stint["name"],
                    "il_start": start.date().isoformat(),
                    "il_end": end.date().isoformat(),
                    "il_days": max((end - start).days, 0),
                    "right_censored": stint["right_censored"],
                }
            )
        print(f"{season}: {len(stints)} IL stints")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUTPUT / "il_stints.csv", index=False, encoding="utf-8-sig")
    totals = frame.groupby(["season", "name"], as_index=False)["il_days"].sum()
    totals.to_csv(OUTPUT / "il_days_by_player_season.csv", index=False, encoding="utf-8-sig")
    print(f"Saved live snapshots to {OUTPUT.relative_to(ROOT)} on {date.today().isoformat()}")


if __name__ == "__main__":
    main()
