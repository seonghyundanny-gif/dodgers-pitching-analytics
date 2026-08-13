# Data guide

This repository separates reproducible public analysis tables from source snapshots and
optional raw downloads. Monetary values are nominal U.S. dollars unless a column says
otherwise. Percent columns use decimal fractions (`0.13` means 13%). CSV files use
UTF-8 with a byte-order mark so they open cleanly in Excel.

## Directory policy

| Directory | Purpose | Git policy |
|---|---|---|
| `processed/` | Small, analysis-ready tables used by scripts, tests, SQL, and Tableau | Tracked |
| `snapshots/` | Frozen intermediate/source snapshots retained for auditability | Tracked when redistribution is allowed |
| `raw/` | Downloads from upstream providers | Not assumed redistributable; see source notes before adding |

Generated SQLite files are intentionally ignored. Recreate them with `make database`.
Downloaded ZIP archives, caches, and dependency directories are also ignored.

## Processed datasets

### `pitcher_stats.csv`

One row per Dodgers pitcher-season. The checked-in release covers 2017-2019 and
2022-2025; the 2020-2021 seasons are excluded from the pitcher analysis because the
pandemic and lockout created structurally unusual workloads.

| Column | Meaning |
|---|---|
| `season`, `player_id`, `name`, `team` | Observation identifiers |
| `Age` | Player age on June 30 of the season |
| `IP` | Baseball innings notation; `.1` and `.2` mean one and two outs |
| `IP_decimal` | True decimal innings used in calculations |
| `K_pct`, `ERA` | Strikeout percentage and earned-run average |
| `fastball_velo_mph` | Average four-seam/sinker velocity in mph |
| `WAR`, `WAR_per_IP` | Wins Above Replacement and workload-normalized WAR |
| `IL_days` | Days on the injured list during the player-season |
| `Postseason_IP`, `Postseason_WAR_proxy` | Postseason workload and an explicitly labeled proxy outcome |
| `low_sample_flag` | `1` when `IP_decimal < 5`; those rows remain auditable but are excluded from primary regressions |

The current file contains 221 pitcher-seasons. The primary regression sample contains
184 observations representing 106 unique pitchers after applying `low_sample_flag == 0`.
These are repeated player-season observations, not 184 unique players.

### `team_financials.csv`

One row per Dodgers season with payroll components, competitive-balance-tax payments,
attendance/postseason measures, injury salary loss, and external financial outcomes.
`Superstar_Era` marks the post-2024 strategy period. Some source categories can be
unavailable rather than zero; consult `docs/data_dictionary.md` before imputing values.

### `comparable_teams_financials.csv`

A balanced six-team, ten-season panel (2017-2026) for the exploratory
difference-in-differences analysis. The comparison teams are BOS, CHC, NYM, NYY, and
SFG; LAD is the treated team. `Treat_Post` must always equal `Treat * Post`, where
`Post == 1` beginning in 2024.

The 2026 financial observations are preliminary/in-season estimates, not finalized
annual accounts. Any result using them should retain that caveat.

### `did_regression_results.csv`

Model output for revenue, team value, operating income, and operating-income margin.
Each outcome includes the full 2017-2026 panel and a sensitivity sample excluding
2020-2021. `did_coef`, `se`, and `p_value` are machine-readable numeric fields.
`OI_Margin_Pct` coefficients are fractions: multiply by 100 to report percentage points.

## Rebuilding and validation

From the repository root:

```bash
make setup
make data
make test
```

`make data` builds the processed tables and runs the project validation script. Tests
then enforce column contracts, unique keys, plausible ranges, treatment coding, the
documented 184-observation analysis sample, and published DiD smoke-test estimates.

## Provenance and redistribution

The analysis combines MLB Stats API, Baseball Savant/Statcast, FanGraphs-derived WAR,
Spotrac-style payroll/CBT data, and externally reported franchise financial estimates.
Upstream terms can change. Do not add newly downloaded raw data to the public repository
until its redistribution terms have been checked. Record the source URL, access date,
coverage, raw filename, and cleaning script in `docs/data_sources.md` for every update.

Processed data are provided for reproducibility and should not be interpreted as an
independent license grant for third-party source material. This is an observational
independent project, not an official MLB, Dodgers, FanGraphs, Spotrac, or Forbes product.
