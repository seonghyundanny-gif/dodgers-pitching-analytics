"""Six-team Diff-in-Differences analysis with team and season fixed effects."""

from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "processed" / "comparable_teams_financials.csv"
RESULTS = ROOT / "data" / "processed" / "did_regression_results.csv"
FIGURES = ROOT / "reports" / "figures"
OUTCOMES = ["Revenue", "Team_Value", "Operating_Income", "OI_Margin_Pct"]
LABELS = {
    "Revenue": "Revenue ($)",
    "Team_Value": "Team value ($)",
    "Operating_Income": "Operating income ($)",
    "OI_Margin_Pct": "Operating-income margin (percentage points)",
}


def display_effect(outcome: str, value: float) -> str:
    """Format ratio outcomes as percentage points, not as raw proportions."""
    if outcome == "OI_Margin_Pct":
        return f"{value * 100:+.2f} pp"
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:+.3f}B"
    return f"{value / 1_000_000:+.2f}M"


def run_did(data: pd.DataFrame, outcome: str):
    result = smf.ols(
        f"{outcome} ~ C(team) + C(season) + Treat_Post", data=data
    ).fit(cov_type="cluster", cov_kwds={"groups": data["team"]})
    coefficient = result.params["Treat_Post"]
    standard_error = result.bse["Treat_Post"]
    p_value = result.pvalues["Treat_Post"]
    print(
        f"{LABELS[outcome]}: effect={display_effect(outcome, coefficient)}, "
        f"SE={display_effect(outcome, standard_error)}, p={p_value:.4f}, n={len(data)}"
    )
    return coefficient, standard_error, p_value


def make_trend_figure(panel: pd.DataFrame) -> None:
    indexed = panel.copy()
    base = indexed.loc[indexed["season"].eq(2017)].set_index("team")[["Revenue", "Team_Value"]]
    indexed["Revenue_idx"] = indexed.apply(
        lambda row: row["Revenue"] / base.loc[row["team"], "Revenue"] * 100, axis=1
    )
    indexed["Value_idx"] = indexed.apply(
        lambda row: row["Team_Value"] / base.loc[row["team"], "Team_Value"] * 100, axis=1
    )
    lad = indexed.loc[indexed["team"].eq("LAD")].sort_values("season")
    peers = (
        indexed.loc[indexed["team"].ne("LAD")]
        .groupby("season")[["Revenue_idx", "Value_idx"]]
        .mean()
        .reset_index()
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, column, title in [
        (axes[0], "Revenue_idx", "Revenue"),
        (axes[1], "Value_idx", "Team value"),
    ]:
        ax.plot(lad["season"], lad[column], color="#1F4E79", marker="o", label="LAD")
        ax.plot(peers["season"], peers[column], color="#9DC3E6", marker="o",
                linestyle="--", label="Peer average")
        ax.axvline(2023.5, color="gray", linestyle=":", linewidth=1)
        ax.set(xlabel="Season", ylabel="Index (2017=100)", title=f"{title} (indexed)")
        ax.legend(fontsize=8)
    fig.suptitle("LAD versus peer-team average", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "chart5_did_trend.png", dpi=150)
    plt.close(fig)


def make_event_study(panel: pd.DataFrame) -> pd.DataFrame:
    fitted = smf.ols(
        "Revenue ~ C(team) + C(season) + C(season):Treat", data=panel
    ).fit(cov_type="cluster", cov_kwds={"groups": panel["team"]})
    covariance = fitted.cov_params()
    pattern = re.compile(r"C\(season\)\[(\d{4})\]:Treat")
    terms = {
        int(match.group(1)): name
        for name in fitted.params.index
        if (match := pattern.fullmatch(name))
    }
    reference = terms[2023]
    rows = []
    for season, term in sorted(terms.items()):
        coefficient = fitted.params[term] - fitted.params[reference]
        variance = (
            covariance.loc[term, term] + covariance.loc[reference, reference]
            - 2 * covariance.loc[term, reference]
        )
        standard_error = np.sqrt(max(variance, 0))
        p_value = 2 * stats.norm.sf(abs(coefficient / standard_error)) if standard_error else np.nan
        rows.append({"season": season, "coef": coefficient, "se": standard_error, "p_value": p_value})
    event = pd.DataFrame(rows)
    print("\nRevenue event study (2023 reference)")
    print(event.to_string(index=False))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.errorbar(event["season"], event["coef"], yerr=1.96 * event["se"], fmt="o-",
                color="#1F4E79", ecolor="#9DC3E6", capsize=4)
    ax.axhline(0, color="black", linestyle=":", linewidth=0.8)
    ax.axvline(2023.5, color="gray", linestyle=":", linewidth=1)
    ax.set(xlabel="Season", ylabel="Revenue gap relative to 2023 ($)",
           title="Event study: LAD revenue gap versus peers (95% CI)")
    fig.tight_layout()
    fig.savefig(FIGURES / "chart6_event_study.png", dpi=150)
    plt.close(fig)
    return event


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(PANEL, encoding="utf-8-sig")
    rows = []
    samples = {
        "full_2017_2026": panel,
        "excl_2020_2021": panel.loc[~panel["season"].isin([2020, 2021])],
    }
    for sample_name, sample in samples.items():
        print(f"\n{sample_name} ({sample['team'].nunique()} team clusters)")
        for outcome in OUTCOMES:
            coefficient, standard_error, p_value = run_did(sample, outcome)
            rows.append(
                {
                    "outcome": outcome,
                    "sample": sample_name,
                    "did_coef": coefficient,
                    "se": standard_error,
                    "p_value": p_value,
                    "effect_display": display_effect(outcome, coefficient),
                    "unit": "percentage_points" if outcome == "OI_Margin_Pct" else "usd",
                }
            )

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(RESULTS, index=False, encoding="utf-8-sig")
    make_trend_figure(panel)
    make_event_study(panel)
    print(f"\nSaved {RESULTS.relative_to(ROOT)} and DiD figures")
    print("Caution: six clusters and imperfect pre-trends require conservative interpretation.")


if __name__ == "__main__":
    main()
