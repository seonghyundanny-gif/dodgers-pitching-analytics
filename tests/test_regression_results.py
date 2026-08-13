import pytest


def _estimate(results, outcome, sample="full_2017_2026"):
    row = results.loc[(results["outcome"] == outcome) & (results["sample"] == sample)]
    assert len(row) == 1
    return row.iloc[0]


def test_documented_pitcher_analysis_sample_is_preserved(pitcher_stats):
    analysis_sample = pitcher_stats.loc[pitcher_stats["low_sample_flag"].eq(0)]
    assert len(analysis_sample) == 184
    assert analysis_sample["player_id"].nunique() == 106


def test_did_results_cover_every_outcome_and_sensitivity_sample(did_results):
    assert not did_results.duplicated(["outcome", "sample"]).any()
    assert set(did_results["outcome"]) == {
        "Revenue",
        "Team_Value",
        "Operating_Income",
        "OI_Margin_Pct",
    }
    assert set(did_results["sample"]) == {"full_2017_2026", "excl_2020_2021"}
    assert did_results[["did_coef", "se", "p_value"]].notna().all().all()
    assert did_results["se"].gt(0).all()
    assert did_results["p_value"].between(0, 1).all()


def test_full_sample_did_core_estimates(did_results):
    revenue = _estimate(did_results, "Revenue")
    team_value = _estimate(did_results, "Team_Value")
    operating_income = _estimate(did_results, "Operating_Income")
    margin = _estimate(did_results, "OI_Margin_Pct")

    assert revenue["did_coef"] == pytest.approx(97_371_429, rel=0.001)
    assert team_value["did_coef"] == pytest.approx(1_655_238_095, rel=0.001)
    assert revenue["p_value"] < 0.001
    assert team_value["p_value"] < 0.001
    assert operating_income["p_value"] > 0.05
    # Stored as a fraction: -0.1317 corresponds to -13.17 percentage points.
    assert margin["did_coef"] == pytest.approx(-0.131714, abs=0.00001)
    assert margin["p_value"] > 0.05


def test_covid_excluded_margin_uses_fraction_not_percent_units(did_results):
    margin = _estimate(did_results, "OI_Margin_Pct", "excl_2020_2021")
    assert margin["did_coef"] == pytest.approx(0.0912, abs=0.00001)
