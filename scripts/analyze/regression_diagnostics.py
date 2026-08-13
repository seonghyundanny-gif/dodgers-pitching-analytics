"""VIF and heteroskedasticity diagnostics for the H1 regressions."""

from pathlib import Path

import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor


ROOT = Path(__file__).resolve().parents[2]
PITCHERS = ROOT / "data" / "processed" / "pitcher_stats.csv"


def main() -> None:
    pitchers = pd.read_csv(PITCHERS, encoding="utf-8-sig")
    sample = pitchers.loc[pitchers["low_sample_flag"].eq(0)].copy()
    x_cols = ["fastball_velo_mph", "Age", "IP_decimal"]
    x = sm.add_constant(sample[x_cols])

    vif = pd.DataFrame(
        {
            "variable": x.columns,
            "VIF": [variance_inflation_factor(x.values, i) for i in range(x.shape[1])],
        }
    )
    print("VIF (values above roughly 5-10 merit investigation)")
    print(vif.to_string(index=False))

    print("\nBreusch-Pagan tests")
    for outcome in ["IL_days", "WAR_per_IP", "Postseason_WAR_proxy"]:
        fitted = sm.OLS(sample[outcome], x).fit()
        statistic, p_value, _, _ = het_breuschpagan(fitted.resid, fitted.model.exog)
        finding = "heteroskedasticity detected" if p_value < 0.05 else "no strong evidence"
        print(f"{outcome}: LM={statistic:.3f}, p={p_value:.4f} ({finding})")


if __name__ == "__main__":
    main()
