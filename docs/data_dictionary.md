# Data Dictionary

All processed CSV files use UTF-8 with a byte-order mark. Monetary fields are nominal US dollars unless noted. Percentage fields ending in `_Pct` are stored as fractions: `0.05` means 5%.

## `data/processed/pitcher_stats.csv`

One row per Dodgers pitcher-season. Primary key: (`season`, `player_id`).

| Field | Type | Definition |
| --- | --- | --- |
| `season` | integer | MLB season |
| `player_id` | integer | MLB Stats API person identifier |
| `name` | string | Player display name |
| `team` | string | Team abbreviation; LAD in this table |
| `Age` | integer | Age on June 30 of the season |
| `IP` | number | Baseball innings notation; `.1` and `.2` mean one and two outs, not decimal tenths |
| `IP_decimal` | number | Innings converted to true decimal thirds |
| `K_pct` | number | Strikeouts divided by batters faced, multiplied by 100 |
| `ERA` | number | Earned run average |
| `fastball_velo_mph` | number | Mean release speed in mph for four-seam fastballs and sinkers |
| `WAR` | number | Retained FanGraphs regular-season pitcher WAR |
| `WAR_per_IP` | number | `WAR / IP_decimal` |
| `IL_days` | number | Reconstructed IL days in the player-season; zero also includes unmatched/no closed stint in the processed table |
| `Postseason_IP` | number | Postseason decimal innings represented in the proxy input; zero if no matched appearance |
| `Postseason_WAR_proxy` | number | Simplified FIP-based postseason value proxy; not official WAR |
| `low_sample_flag` | integer | 1 when `IP_decimal < 5`; otherwise 0 |

Analysis notes:

- The full table has 221 rows and 129 unique players.
- Main pitcher regressions use `low_sample_flag = 0`: 184 rows and 106 unique players.
- A zero in `IL_days` should not be read as independently verified proof that the pitcher was healthy all season; see [Limitations](limitations.md).

## `data/processed/team_financials.csv`

One row per Dodgers season for 2017–2019 and 2022–2025. Primary key: (`season`, `team`).

| Field | Type | Definition |
| --- | --- | --- |
| `season` | integer | MLB season |
| `team` | string | LAD |
| `active_roster_payroll` | dollars | Spotrac active-roster payroll allocation |
| `injured_list_payroll` | dollars | Spotrac injured-list payroll allocation |
| `suspended_restricted_payroll` | dollars | Suspended/restricted payroll; blank where unavailable/not applicable |
| `dead_money` | dollars | Dead-money allocation |
| `retained_payroll` | dollars | Retained salary allocation |
| `minor_league_payroll` | dollars | Minor-league payroll allocation represented by the source table |
| `signing_bonus` | dollars | Signing-bonus allocation represented by the source table |
| `total_adjusted_payroll` | dollars | Spotrac total adjusted payroll allocation |
| `CBT_Tax_Paid` | dollars | Competitive Balance Tax bill |
| `Road_Attendance` | count | Mean reported attendance at Dodgers regular-season road games |
| `Postseason_Home_Games` | count | Postseason games hosted by the Dodgers |
| `Injured_Salary_Loss` | dollars | Constructed estimate: pitcher salary / 183 × reconstructed IL days, summed by season |
| `Superstar_Era` | integer | 1 for season 2024 onward; otherwise 0 |
| `Pure_Marginal_Benefit` | dollars | `Revenue − total_adjusted_payroll − CBT_Tax_Paid`; constructed, non-GAAP metric |
| `Team_Value` | dollars | Forbes-style public team-value estimate |
| `Revenue` | dollars | Forbes-style public revenue estimate |
| `Operating_Income` | dollars | Forbes-style public operating-income estimate |
| `OI_Margin_Pct` | fraction | `Operating_Income / Revenue` as supplied/rounded in the source |
| `Player_Expenses_External` | dollars | External estimate of player expenses |
| `Player_Exp_Pct` | fraction | Player expenses as a share of revenue |
| `Win_Player_Cost_Ratio` | number | Source-provided win-to-player-cost ratio |
| `Wins` | integer | Regular-season wins |
| `Avg_Ticket_Price` | dollars | Source-provided average ticket price |

## `data/processed/comparable_teams_financials.csv`

One row per team-season. Teams are LAD, NYY, BOS, NYM, CHC, and SFG; seasons are 2017–2026. Primary key: (`team`, `season`).

| Field | Type | Definition |
| --- | --- | --- |
| `team` | string | MLB team abbreviation |
| `season` | integer | Season/year of the financial estimate |
| `Treat` | integer | 1 for LAD; 0 for peer teams |
| `Post` | integer | 1 for 2024–2026; 0 for 2017–2023 |
| `Treat_Post` | integer | `Treat × Post`, the DiD interaction |
| `Team_Value` | dollars | Forbes-style team-value estimate |
| `Revenue` | dollars | Forbes-style revenue estimate |
| `Operating_Income` | dollars | Forbes-style operating-income estimate |
| `OI_Margin_Pct` | fraction | Operating-income margin; e.g. `0.18` is 18% |
| `Player_Expenses_External` | dollars | External player-expense estimate |
| `Player_Exp_Pct` | fraction | Player expenses divided by revenue |
| `Win_Player_Cost_Ratio` | number | Source-provided win-to-player-cost ratio |
| `Seating_Capacity` | number | Source field for stadium seating capacity; may be missing |
| `Avg_Ticket_Price` | dollars | Source field for average ticket price; may be missing |

**2026 fields are preliminary, in-season estimates.** They should not be combined with completed historical seasons without a sensitivity analysis.

## `data/processed/did_regression_results.csv`

One row per outcome and sample specification.

| Field | Type | Definition |
| --- | --- | --- |
| `outcome` | string | Dependent variable in the DiD regression |
| `sample` | string | `full_2017_2026` or `excl_2020_2021` |
| `did_coef` | number | Coefficient on `Treat_Post` |
| `se` | number | Team-clustered standard error |
| `p_value` | number | Two-sided p-value from the stored regression |

Coefficient units follow the underlying outcome. For `OI_Margin_Pct`, values are fractions: `−0.1317` means **−13.17 percentage points**.

## Important intermediate tables

The `data/snapshots/` directory preserves inherited analysis artifacts for auditability. These are not the canonical project inputs.

| File | Unit | Purpose |
| --- | --- | --- |
| `il_stints.csv` | IL spell | Parsed placement and activation dates |
| `il_days_by_player_season.csv` | player-season | Aggregated reconstructed IL days |
| `postseason_war_proxy.csv` | player-season | Postseason proxy components/results |
| `attendance_postseason.csv` | team-season | Road attendance and postseason home games |
| `cbt_tax.csv` | team-season | CBT threshold/payroll/tax results |
| `injured_salary_loss.csv` | team-season | Salary-weighted IL-day estimate |
| `dodgers_analysis.db` | SQLite database | Snapshot used for SQL exploration; reproducible and not authoritative |
