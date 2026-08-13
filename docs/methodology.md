# Methodology

## Study objective

This project evaluates a roster decision under uncertainty: higher fastball velocity may increase both pitching value and physical risk. It also asks whether the Dodgers' financial outcomes changed relative to selected large-market peers after the 2023–24 superstar-signing offseason.

The design is observational. Pitcher-level regressions estimate conditional associations, and the team-level Difference-in-Differences (DiD) design is an exploratory quasi-experimental comparison. Neither identifies velocity itself as a causal driver of club revenue.

## Data scope and units of observation

### Pitcher panel

- Unit: Dodgers pitcher-season
- Seasons: 2017–2019 and 2022–2025
- Full processed table: 221 observations, 129 unique players
- Main regression sample: 184 observations, 106 unique players
- Exclusion: 37 pitcher-seasons with fewer than 5 decimal innings (`low_sample_flag = 1`)

The 2020 and 2021 pitcher seasons are excluded because shortened schedules and pandemic-era operating conditions create a structural break. Each pitcher can appear in more than one season.

### Dodgers financial table

- Unit: Dodgers team-season
- Seasons: 2017–2019 and 2022–2025
- Observations: 7

This table supports descriptive summaries only. A pre/post mean comparison cannot isolate a strategy effect from market-wide changes.

### Comparable-team financial panel

- Unit: team-season
- Teams: LAD, NYY, BOS, NYM, CHC, SFG
- Seasons: 2017–2026
- Observations: 60
- Treatment indicator: `Treat = 1` for LAD
- Post indicator: `Post = 1` for 2024 onward

The 2026 values are preliminary, in-season estimates. All financial outcomes are public external estimates rather than audited club financial statements.

## Data preparation

1. Dodgers roster and conventional pitching statistics were collected through MLB Stats API.
2. Four-seam fastball and sinker velocities were averaged from Statcast pitch-level data through `pybaseball`.
3. Retained FanGraphs CSV exports supplied regular-season WAR and postseason FIP/IP inputs.
4. Baseball innings notation was converted to decimal innings: for example, `64.1` means 64⅓ innings, not 64.1.
5. IL placements and activations were parsed from MLB transaction descriptions, paired by normalized player name, and aggregated to player-season IL days.
6. Payroll and CBT tables were collected from Spotrac; schedule and attendance fields came from MLB Stats API.
7. Financial estimates were normalized to numeric dollars/fractions and merged by team-season.
8. Analysis tables were validated for duplicate keys, missingness, plausible ranges, and small-inning observations.

The checked-in `data/processed/` tables are the stable review inputs. The collection scripts show how API/web inputs were assembled, but the inherited archive does not contain a single fully automated merge that reconstructs every final pitcher field from scratch. This is documented as a reproducibility limitation.

## Pitcher-level models

The main specifications are pooled ordinary least squares:

```text
IL_days_it = α + β Velocity_it + γ Age_it + δ IP_it + ε_it

WAR_per_IP_it = α + β Velocity_it + γ Age_it + δ IP_it + ε_it

Postseason_WAR_proxy_it = α + β Velocity_it + γ Age_it + δ IP_it + ε_it
```

where `i` indexes pitchers and `t` indexes seasons. Standard errors are clustered by `player_id` to allow arbitrary within-player dependence across seasons.

A secondary injury-history specification uses the most recent earlier in-sample observation:

```text
IL_days_it = α + β Velocity_it + γ Age_it + δ IP_it
             + θ Prior_IL_days_it + ε_it
```

This reduces the sample to 78 pitcher-seasons with an observed prior in-sample season. The velocity coefficient remains positive (+4.32 days) with `p = 0.031`. This sensitivity check reduces, but does not eliminate, omitted-variable and reverse-causality concerns.

Same-season innings may be endogenous because injury itself limits workload. Accordingly, the specification is treated as descriptive. A stronger follow-up would use prior-season innings, role, pitch mix, prior injury, and within-player comparisons.

As a direct sensitivity check, the repository also estimates `IL_days ~ velocity + age`
without same-season innings. The velocity coefficient is +4.28 days per mph
(`p < 0.001`, 184 pitcher-seasons, 106 player clusters), close to the +4.24 estimate
from the primary specification. This check addresses one modeling choice but does not
turn the association into a causal estimate.

## Descriptive velocity buckets

The regression sample is grouped using left-closed intervals:

- Below 92 mph
- 92 to below 94 mph
- 94 to below 96 mph
- 96 mph and above

Group means describe the sample; they are not adjusted treatment effects. The exact counts are 36, 46, 65, and 37.

## Postseason WAR proxy

Official individual postseason WAR was unavailable in the retained FanGraphs export. The project therefore uses a simplified FIP-based proxy:

```text
Postseason_WAR_proxy = ((4.20 − Pitcher_FIP) / 10) × (IP / 9)
                       + (IP / 9) × 0.12
```

The constants are a league FIP of 4.20, 10 runs per win, and replacement value of 0.12 wins per nine innings. Unlike a production WAR implementation, the proxy does not use season-specific league context or role-specific replacement levels. It is a directional research feature, not official WAR.

## Dodgers pre/post comparison

For descriptive reporting, 2024 marks the start of the post period. Pre-period means use the available non-pandemic Dodgers seasons, and post-period means use 2024–2025. Metrics include payroll, CBT paid, injured salary loss, postseason home games, road attendance, revenue, operating income, team value, and:

```text
Pure_Marginal_Benefit = Revenue − total_adjusted_payroll − CBT_Tax_Paid
```

The word “marginal” is used as a before/after level-change approximation, not a calculus derivative. This constructed metric is not GAAP operating income and should not be interpreted as audited cash flow.

## Difference-in-Differences

The peer analysis estimates:

```text
Y_it = team fixed effects + season fixed effects
       + β (LAD_i × Post2024_t) + ε_it
```

Outcomes are revenue, team value, operating income, and operating-income margin. Standard errors are clustered at the team level. Season fixed effects absorb shocks common to all six teams, including the pandemic seasons. A robustness run excludes 2020–2021.

The coefficient `β` measures the change in LAD relative to the contemporaneous change among the five selected peers. It should be interpreted cautiously because:

- there are only six team clusters;
- peer selection is judgment-based;
- pre-period revenue gaps are not perfectly parallel;
- only a short post period is available;
- 2026 is preliminary;
- financial figures are external estimates.

The stored full-sample estimates are +$97.37M for revenue, +$1.655B for team value, −$2.84M for operating income, and −0.1317 in operating-income-margin fraction units. The last value corresponds to **−13.17 percentage points**, not −0.13 percentage points. Revenue and team-value coefficients are statistically distinguishable from zero under the stored cluster-robust calculation; operating-income outcomes are not. With six clusters, conventional p-values may be anti-conservative, so the results remain exploratory.

## Event study and bridge analysis

An event-study variant compares annual LAD-versus-peer revenue gaps with 2023 as the reference year. Its main purpose is to inspect timing and the plausibility of parallel trends, not to prove a mechanism. The post pattern is heterogeneous: approximately −$53M in 2024, +$98.6M in 2025, and +$171M in preliminary 2026 data.

The bridge analysis correlates season-level team velocity measures with revenue and postseason home games. A positive level correlation between team average velocity and revenue (`r = 0.777`, `p = 0.040`) disappears after annualized first differencing; all differenced correlations have `p > 0.6`. The analysis therefore does not support a direct velocity-to-revenue pathway.

## Diagnostics

- Repeated pitchers: handled with player-clustered standard errors.
- Multicollinearity: reported VIF values are approximately 1.0–1.1.
- Heteroskedasticity: Breusch–Pagan tests indicate heteroskedasticity in the main pitcher models; clustered standard errors mitigate but do not fully solve model misspecification.
- Small samples: observations under five innings are flagged and excluded from the main regressions.
- COVID sensitivity: DiD results are reported with and without 2020–2021.

See [Limitations](limitations.md) for interpretation boundaries and [Reproducibility](reproducibility.md) for the execution path.
