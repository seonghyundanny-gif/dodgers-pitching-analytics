"""Bridge pitcher-level velocity metrics to team outcomes by season."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[2]
PITCHERS = ROOT / "data" / "processed" / "pitcher_stats.csv"
TEAM = ROOT / "data" / "processed" / "team_financials.csv"
FIGURES = ROOT / "reports" / "figures"


def correlation_table(data: pd.DataFrame, pairs: list[tuple[str, str, str]]) -> None:
    for x_col, y_col, label in pairs:
        subset = data[[x_col, y_col]].dropna()
        r_value, p_value = stats.pearsonr(subset[x_col], subset[y_col])
        print(f"{label}: r={r_value:+.3f}, p={p_value:.3f}, n={len(subset)}")


def add_scatter(ax, data, x_col, y_col, x_label, y_label) -> None:
    subset = data[[x_col, y_col, "season"]].dropna()
    ax.scatter(subset[x_col], subset[y_col], color="#2E75B6", s=70, edgecolors="white")
    for row in subset.itertuples():
        ax.annotate(str(row.season), (getattr(row, x_col), getattr(row, y_col)),
                    xytext=(5, 3), textcoords="offset points", fontsize=8)
    if len(subset) >= 2:
        slope, intercept = np.polyfit(subset[x_col], subset[y_col], 1)
        xs = np.linspace(subset[x_col].min(), subset[x_col].max(), 100)
        ax.plot(xs, slope * xs + intercept, color="gray", linestyle="--", linewidth=1)
    r_value, p_value = stats.pearsonr(subset[x_col], subset[y_col])
    ax.set(xlabel=x_label, ylabel=y_label, title=f"r={r_value:+.3f} (p={p_value:.3f})")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    pitchers = pd.read_csv(PITCHERS, encoding="utf-8-sig")
    team = pd.read_csv(TEAM, encoding="utf-8-sig")
    sample = pitchers.loc[pitchers["low_sample_flag"].eq(0)].copy()

    season_velocity = sample.groupby("season").agg(
        Team_Avg_Velo=("fastball_velo_mph", "mean"),
        High_Velo_Pitchers=("fastball_velo_mph", lambda values: values.ge(96).sum()),
        Pitcher_Count=("fastball_velo_mph", "count"),
    ).reset_index()
    season_velocity["High_Velo_Pct"] = (
        100 * season_velocity["High_Velo_Pitchers"] / season_velocity["Pitcher_Count"]
    )
    merged = season_velocity.merge(
        team[["season", "Postseason_Home_Games", "Revenue", "CBT_Tax_Paid", "Superstar_Era"]],
        on="season",
        how="inner",
    ).sort_values("season")
    print(merged.to_string(index=False))

    level_pairs = [
        ("Team_Avg_Velo", "Postseason_Home_Games", "Average velocity vs postseason home games"),
        ("Team_Avg_Velo", "Revenue", "Average velocity vs revenue"),
        ("High_Velo_Pitchers", "Postseason_Home_Games", "96+ mph pitchers vs postseason home games"),
        ("High_Velo_Pitchers", "Revenue", "96+ mph pitchers vs revenue"),
    ]
    print("\nLevel correlations (exploratory)")
    correlation_table(merged, level_pairs)

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for ax, (x_col, y_col, _) in zip(axes.flat, level_pairs):
        add_scatter(ax, merged, x_col, y_col, x_col.replace("_", " "), y_col.replace("_", " "))
    fig.suptitle("Bridge: team velocity, postseason and revenue", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "chart4_bridge.png", dpi=150)
    plt.close(fig)

    annualized = merged.copy()
    year_gap = annualized["season"].diff()
    for source, target in [
        ("Team_Avg_Velo", "D_Team_Avg_Velo"),
        ("High_Velo_Pitchers", "D_High_Velo_Pitchers"),
        ("Revenue", "D_Revenue"),
        ("Postseason_Home_Games", "D_Postseason_HG"),
    ]:
        annualized[target] = annualized[source].diff() / year_gap
    annualized = annualized.dropna(subset=["D_Team_Avg_Velo"])

    diff_pairs = [
        ("D_Team_Avg_Velo", "D_Postseason_HG", "Annualized velocity change vs postseason change"),
        ("D_Team_Avg_Velo", "D_Revenue", "Annualized velocity change vs revenue change"),
        ("D_High_Velo_Pitchers", "D_Postseason_HG", "Annualized 96+ count change vs postseason change"),
        ("D_High_Velo_Pitchers", "D_Revenue", "Annualized 96+ count change vs revenue change"),
    ]
    print("\nAnnualized first-difference correlations")
    correlation_table(annualized, diff_pairs)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    add_scatter(axes[0], annualized, "D_Team_Avg_Velo", "D_Revenue",
                "Annualized change in velocity (mph)", "Annualized change in revenue ($)")
    add_scatter(axes[1], annualized, "D_Team_Avg_Velo", "D_Postseason_HG",
                "Annualized change in velocity (mph)", "Annualized change in postseason home games")
    fig.suptitle("Bridge: annualized first differences", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "chart4b_bridge_diff.png", dpi=150)
    plt.close(fig)
    print(f"\nSaved bridge figures to {FIGURES.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
