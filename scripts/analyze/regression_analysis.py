"""Player-clustered H1 regressions for the public analysis."""

from pathlib import Path

import pandas as pd
import statsmodels.api as sm


ROOT = Path(__file__).resolve().parents[2]
PITCHERS = ROOT / "data" / "processed" / "pitcher_stats.csv"
RESULTS = ROOT / "data" / "processed" / "pitcher_regression_results.csv"


def run_clustered_ols(data: pd.DataFrame, y_col: str, x_cols: list[str], label: str):
    """Fit OLS with standard errors clustered by player."""
    model = sm.OLS(data[y_col], sm.add_constant(data[x_cols])).fit(
        cov_type="cluster", cov_kwds={"groups": data["player_id"]}
    )
    print(f"\n{'=' * 24} {label} {'=' * 24}")
    print(model.summary().tables[1])
    print(
        f"R-squared: {model.rsquared:.4f} | N: {int(model.nobs)} | "
        f"player clusters: {data['player_id'].nunique()}"
    )
    return model


def main() -> None:
    pitchers = pd.read_csv(PITCHERS, encoding="utf-8-sig")
    sample = (
        pitchers.loc[pitchers["low_sample_flag"].eq(0)]
        .sort_values(["player_id", "season"])
        .copy()
    )
    sample["Prior_IL_days"] = sample.groupby("player_id")["IL_days"].shift(1)

    print(f"H1 sample: n={len(sample)}")
    print(f"Unique pitchers: {sample['player_id'].nunique()}")
    print(f"Prior-season subsample: n={sample['Prior_IL_days'].notna().sum()}")

    controls = ["fastball_velo_mph", "Age", "IP_decimal"]
    fitted = [
        ("IL_days", "main", run_clustered_ols(sample, "IL_days", controls, "H1-a: IL days")),
        ("IL_days", "no_current_ip", run_clustered_ols(
            sample,
            "IL_days",
            ["fastball_velo_mph", "Age"],
            "H1-a sensitivity: same-season IP excluded",
        )),
        ("WAR_per_IP", "main", run_clustered_ols(sample, "WAR_per_IP", controls, "H1-b: WAR per IP")),
        ("Postseason_WAR_proxy", "main", run_clustered_ols(
        sample, "Postseason_WAR_proxy", controls, "H1-c: postseason WAR proxy"
        )),
    ]

    history = sample.dropna(subset=["Prior_IL_days"]).copy()
    history_model = run_clustered_ols(
        history,
        "IL_days",
        controls + ["Prior_IL_days"],
        "H1-a sensitivity: prior IL controlled",
    )
    fitted.append(("IL_days", "prior_il_control", history_model))

    rows = []
    for outcome, specification, model in fitted:
        rows.append(
            {
                "outcome": outcome,
                "specification": specification,
                "velocity_coef": model.params["fastball_velo_mph"],
                "velocity_se": model.bse["fastball_velo_mph"],
                "velocity_p_value": model.pvalues["fastball_velo_mph"],
                "r_squared": model.rsquared,
                "n_obs": int(model.nobs),
                "player_clusters": int(
                    history["player_id"].nunique()
                    if specification == "prior_il_control"
                    else sample["player_id"].nunique()
                ),
            }
        )
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(RESULTS, index=False, encoding="utf-8-sig")
    print(f"\nSaved {RESULTS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
