"""Generate the three core descriptive figures used in the report."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PITCHERS = ROOT / "data" / "processed" / "pitcher_stats.csv"
TEAM_HISTORY = ROOT / "data" / "snapshots" / "team_financials_extended.csv"
FIGURES = ROOT / "reports" / "figures"
BUCKETS = [-np.inf, 92, 94, 96, np.inf]
BUCKET_LABELS = ["1) <92 mph", "2) 92-94 mph", "3) 94-96 mph", "4) 96+ mph"]


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    pitchers = pd.read_csv(PITCHERS, encoding="utf-8-sig")
    sample = pitchers.loc[pitchers["low_sample_flag"].eq(0)].copy()

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(sample["fastball_velo_mph"], sample["IL_days"], alpha=0.5,
               edgecolor="steelblue", facecolor="none")
    slope, intercept = np.polyfit(sample["fastball_velo_mph"], sample["IL_days"], 1)
    xs = np.linspace(sample["fastball_velo_mph"].min(), sample["fastball_velo_mph"].max(), 100)
    ax.plot(xs, slope * xs + intercept, color="gray", linestyle="--")
    ax.set(xlabel="Fastball velocity (mph)", ylabel="IL days",
           title=f"Fastball velocity versus IL days (n={len(sample)})")
    fig.tight_layout()
    fig.savefig(FIGURES / "chart1_velo_il.png", dpi=150)
    plt.close(fig)

    sample["velocity_bucket"] = pd.cut(
        sample["fastball_velo_mph"], bins=BUCKETS, labels=BUCKET_LABELS, right=False
    )
    buckets = sample.groupby("velocity_bucket", observed=False)["IL_days"].agg(["mean", "count"])
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(buckets.index.astype(str), buckets["mean"], color="#4C72B0")
    ax.bar_label(bars, labels=[f"n={count}" for count in buckets["count"]], padding=3, fontsize=8)
    ax.set(ylabel="Average IL days", title="Average IL days by velocity bucket")
    fig.tight_layout()
    fig.savefig(FIGURES / "chart2_bucket.png", dpi=150)
    plt.close(fig)

    team = pd.read_csv(TEAM_HISTORY, encoding="utf-8-sig")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = np.where(team["Superstar_Era"].eq(1), "#1F4E79", "#9DC3E6")
    ax.bar(team["season"].astype(str), team["CBT_Tax_Paid"], color=colors)
    ax.set(xlabel="Season", ylabel="CBT tax paid ($)", title="Competitive Balance Tax by season")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(FIGURES / "chart3_cbt.png", dpi=150)
    plt.close(fig)
    print(f"Saved 3 figures to {FIGURES.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
