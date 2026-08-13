# Limitations

## Interpretation boundary

This project supports a risk–return description, not a causal statement that throwing harder causes injury, better performance, or higher Dodgers revenue. The pitcher and team analyses operate at different levels, and the bridge analysis does not establish a direct mechanism between them.

## Pitcher-level limitations

### Observational confounding

Pitchers do not receive velocity at random. Role, pitch mix, mechanics, medical history, workload, selection into the majors, and organizational usage can affect both velocity and outcomes. Age and innings controls do not remove these sources of confounding.

### Same-season innings may be a bad control

Injury can reduce innings, so contemporaneous `IP_decimal` may sit downstream of the outcome process. Controlling for it can introduce post-treatment or collider bias. Preferred follow-ups include prior-season workload, role controls, and specifications with and without current innings.

### IL-day measurement

`IL_days` is reconstructed from transaction text, not obtained as an official duration field. The parser can miss wording variants, name changes, overlapping stints, transfers, retroactive placements, or placements that remain open past the collection window. In the inherited pipeline, an open stint without an in-year activation has a missing duration, and later cleaning can turn missing player-season IL values into zero. This can understate injury time and misclassify missingness as health.

### Distributional mismatch

IL days are non-negative, zero-heavy, and right-skewed. OLS can produce inefficient or poorly calibrated inference. Negative binomial, two-part/hurdle, zero-inflated, or survival models would better match the outcome-generating process.

### Repeated observations and selection

Player-clustered standard errors address within-player dependence but do not correct selection into the Dodgers roster or survival in MLB. Excluding observations under five innings reduces unstable rate statistics but may remove injured or marginal players non-randomly.

### Velocity definition

The velocity field averages only four-seam fastballs and sinkers. Pitch usage, role, max velocity, velocity loss during the season, and other fastball types are not modeled. A single season average can hide fatigue and injury timing.

### WAR per inning

`WAR_per_IP` is a ratio outcome and can be volatile at low workloads. The five-inning threshold is modest; sensitivity thresholds at 10, 20, and 40 innings would show whether conclusions depend on small samples. WAR, FIP/xFIP, K−BB%, or run-value outcomes should also be modeled directly.

### Postseason proxy

`Postseason_WAR_proxy` is not official WAR. It uses constant league FIP, runs-per-win, and replacement values across seasons and roles. Measurement error may attenuate its velocity coefficient, but the direction and size of bias cannot be established without validation.

### Two-way-player coverage

Roster-position filters can miss a two-way player when the source does not classify that player as a pitcher for the relevant pull. This is particularly relevant to recent Dodgers seasons.

## Team-level limitations

### Simple pre/post comparisons

The Dodgers-only comparison has few post-2024 observations and cannot separate the roster strategy from league growth, championships, media exposure, international fandom, ticket pricing, macroeconomic conditions, or other concurrent events.

### Financial estimates are not audited

Revenue, operating income, player expenses, and team value are public external estimates. Measurement methods may change across years or teams. Team value is an appraisal-like stock measure, not realized cash flow.

### Constructed benefit metric

`Pure_Marginal_Benefit = Revenue − adjusted payroll − CBT` omits many club operating costs and may overlap conceptually with components of public operating-income estimates. It is a transparent descriptive construct, not accounting profit or economic surplus.

## Difference-in-Differences limitations

### Only six clusters

Team-clustered standard errors rely on large-cluster asymptotics, but the analysis has six teams. Conventional p-values can be too optimistic. Wild-cluster bootstrap inference or randomization-based inference should be added before treating significance as strong evidence.

### Parallel trends are imperfect

The identifying assumption is that, absent the post-2024 change, the LAD-versus-peer outcome gap would have evolved similarly. Revenue gaps move materially during the pre-period. Season fixed effects remove common shocks but do not fix differential pre-trends.

### Peer selection

NYY, BOS, NYM, CHC, and SFG were chosen as large-market/high-payroll peers. This is reasonable but subjective and can create selection bias. A synthetic-control design or a pre-registered donor pool would be more defensible.

### Treatment is bundled

“Post-2024 superstar era” combines multiple signings, team performance, postseason success, marketing, media attention, and broader organizational choices. Its coefficient cannot be attributed specifically to velocity, Ohtani, Yamamoto, or any single decision.

### Short and heterogeneous post period

The estimated average combines a negative 2024 revenue gap with large positive gaps in 2025 and preliminary 2026 data. It should not be described as a stable annual increment.

### Preliminary 2026 data

The 2026 panel is in-season and estimated. It is not directly comparable to finalized historical seasons. Results should always be rerun excluding 2026 and replaced when final values become available.

### Margin units

`OI_Margin_Pct` is stored as a fraction. The full-sample coefficient of `−0.1317` equals **−13.17 percentage points**, not −0.1 percentage points. The operating-income-margin estimate is statistically inconclusive, but the unit still matters.

## Reproducibility and provenance limitations

- Exact source URLs and access dates were not preserved for manually supplied financial values.
- API raw responses were not archived, so a future pull may differ from the checked-in snapshot.
- The inherited collection stage leaves WAR and IL fields blank before separate/manual merges; no single command currently reconstructs every final pitcher field solely from raw sources.
- Web-table scrapers are vulnerable to layout and access-policy changes.
- The packaged Tableau workbook may require Tableau Desktop/Public and is not validated in headless CI.
- PDF/DOCX generation can vary with fonts and operating-system rendering.

## Recommended next analyses

1. Repair open/censored IL spells, merge overlaps, log unmatched transaction text, and validate a stratified sample manually.
2. Report models both with and without current innings; add prior workload, prior injury, role, and pitch-mix controls.
3. Estimate count/hurdle and within-player models, with sensitivity thresholds for minimum innings.
4. Validate or replace the postseason proxy.
5. Add wild-cluster bootstrap DiD inference, pre-trend tests, and a synthetic-control analysis.
6. Rerun the financial panel without 2026 and update it after the season is finalized.
7. Add row-level URLs, access timestamps, source status, and checksums for every external financial observation.
