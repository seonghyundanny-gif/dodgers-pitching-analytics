import numpy as np


PITCHER_COLUMNS = {
    "season",
    "player_id",
    "name",
    "team",
    "Age",
    "IP",
    "IP_decimal",
    "K_pct",
    "ERA",
    "fastball_velo_mph",
    "WAR",
    "WAR_per_IP",
    "IL_days",
    "Postseason_IP",
    "Postseason_WAR_proxy",
    "low_sample_flag",
}

TEAM_COLUMNS = {
    "season",
    "team",
    "total_adjusted_payroll",
    "CBT_Tax_Paid",
    "Road_Attendance",
    "Postseason_Home_Games",
    "Injured_Salary_Loss",
    "Superstar_Era",
    "Team_Value",
    "Revenue",
    "Operating_Income",
    "OI_Margin_Pct",
}

PANEL_COLUMNS = {
    "team",
    "season",
    "Treat",
    "Post",
    "Treat_Post",
    "Team_Value",
    "Revenue",
    "Operating_Income",
    "OI_Margin_Pct",
}


def test_pitcher_schema_and_primary_key(pitcher_stats):
    assert PITCHER_COLUMNS.issubset(pitcher_stats.columns)
    assert not pitcher_stats.duplicated(["season", "player_id"]).any()
    assert pitcher_stats[list(PITCHER_COLUMNS)].notna().all().all()
    assert pitcher_stats["team"].eq("LAD").all()
    assert set(pitcher_stats["low_sample_flag"].unique()) <= {0, 1}


def test_pitcher_numeric_invariants(pitcher_stats):
    assert pitcher_stats["season"].between(2017, 2025).all()
    assert pitcher_stats["Age"].between(18, 50).all()
    assert pitcher_stats["fastball_velo_mph"].between(80, 105).all()
    assert pitcher_stats["IL_days"].between(0, 366).all()
    assert pitcher_stats["IP_decimal"].gt(0).all()
    assert pitcher_stats["low_sample_flag"].eq(
        pitcher_stats["IP_decimal"].lt(5).astype(int)
    ).all()
    expected_war_rate = pitcher_stats["WAR"] / pitcher_stats["IP_decimal"]
    assert np.allclose(pitcher_stats["WAR_per_IP"], expected_war_rate, atol=0.0008)


def test_team_financial_schema(team_financials):
    assert TEAM_COLUMNS.issubset(team_financials.columns)
    assert not team_financials.duplicated(["season", "team"]).any()
    assert team_financials["team"].eq("LAD").all()
    assert set(team_financials["Superstar_Era"].unique()) <= {0, 1}
    assert team_financials["Revenue"].gt(0).all()
    assert team_financials["Team_Value"].gt(0).all()


def test_comparison_panel_is_balanced_and_treatment_is_consistent(comparison_panel):
    assert PANEL_COLUMNS.issubset(comparison_panel.columns)
    assert not comparison_panel.duplicated(["team", "season"]).any()
    assert comparison_panel["team"].nunique() == 6
    assert comparison_panel["season"].nunique() == 10
    assert len(comparison_panel) == 60
    assert comparison_panel.groupby("team")["season"].nunique().eq(10).all()
    assert comparison_panel["Treat"].eq(comparison_panel["team"].eq("LAD").astype(int)).all()
    assert comparison_panel["Post"].eq(comparison_panel["season"].ge(2024).astype(int)).all()
    assert comparison_panel["Treat_Post"].eq(
        comparison_panel["Treat"] * comparison_panel["Post"]
    ).all()
