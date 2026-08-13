# Data Sources and Provenance

This document separates known source provenance from gaps in the inherited project archive. Where an original access date or page-level citation was not preserved, it is marked as unknown rather than inferred.

## Source inventory

| Dataset / fields | Source organization | Source location | Coverage | Local evidence | Access date | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Rosters, IP, strikeouts, batters faced, ERA, birth dates | Major League Baseball | [MLB Stats API](https://statsapi.mlb.com/api/v1/) | LAD, 2017–2019 and 2022–2025 | `scripts/collect/collect_pitcher_stats.py`, `scripts/prepare/add_age_and_war_rate.py` | Not preserved | API responses were transformed; raw JSON was not retained |
| Pitch-level release speed | MLB Baseball Savant / Statcast | Accessed through [`pybaseball`](https://github.com/jldbc/pybaseball) | LAD pitchers, selected seasons | `scripts/collect/collect_pitcher_stats.py` | Not preserved | Velocity averages FF and SI pitch types |
| Regular-season WAR and postseason FIP/IP | FanGraphs | Manually retained CSV exports | LAD, selected seasons | `data/raw/fangraphs/` | Not preserved | Export page URL and download timestamp are not preserved |
| Injured-list transactions | Major League Baseball | [MLB Stats API transactions](https://statsapi.mlb.com/api/v1/transactions) | LAD, selected calendar years | `scripts/collect/collect_injuries.py`, snapshot CSVs | Not preserved | Transaction descriptions are parsed with regular expressions |
| Road attendance and postseason home games | Major League Baseball | [MLB Stats API schedule](https://statsapi.mlb.com/api/v1/schedule) | LAD, selected seasons | `scripts/collect/collect_attendance.py` | Not preserved | Attendance is averaged over road games with reported values |
| Payroll allocations | Spotrac | Season-specific Dodgers payroll pages, e.g. `https://www.spotrac.com/mlb/los-angeles-dodgers/payroll/{season}/` | LAD, selected seasons | `scripts/collect/collect_team_financials.py` | Not preserved | HTML tables can change; outputs should be treated as snapshots |
| Competitive Balance Tax | Spotrac | Season-specific Dodgers tax pages, e.g. `https://www.spotrac.com/mlb/los-angeles-dodgers/tax/{season}/` | LAD, selected seasons | `scripts/collect/collect_cbt_tax.py` | Not preserved | Tax table labels are parsed from HTML |
| Dodgers and peer revenue, value, operating income, player expense, ticket metrics | Forbes-style public estimates supplied with the original project | Original page-level URLs not preserved | Six teams, 2017–2026 | `data/raw/financials/comparable_teams_financials_raw.csv`; values embedded in inherited merge scripts | Not preserved | Not audited financial statements; 2026 is preliminary/in-season |
| Regular-season wins | MLB / inherited project table | Exact page/API call not preserved | LAD selected seasons | `data/processed/team_financials.csv` | Not preserved | Used descriptively |

## Derived data lineage

```text
MLB Stats API + Statcast + retained FanGraphs exports
    → pitcher-season joins and innings conversion
    → IL transaction parsing and postseason proxy
    → data/processed/pitcher_stats.csv

Spotrac + MLB schedule + public financial estimates
    → Dodgers team-season merge
    → data/processed/team_financials.csv

Public six-team financial estimates
    → cleaning, numeric normalization, treatment indicators
    → data/processed/comparable_teams_financials.csv
    → two-way fixed-effects DiD
    → data/processed/did_regression_results.csv
```

## Provenance caveats

### Financial estimates

The financial files were inherited with the project, but the archive does not preserve the exact original Forbes article/profile URL for each team-year or the date each value was accessed. The values should therefore be described as **Forbes-style public estimates**, not as verified audited figures or directly cited Forbes observations.

Before using the dataset in publication, the preferred remediation is to add a row-level provenance table containing:

```text
team, season, metric, source_url, page_title, accessed_at, value, status
```

The `status` field should distinguish completed historical observations from forecasts, estimates, and in-season values. Every 2026 financial observation should be labeled preliminary.

### FanGraphs exports

The four original CSV exports are retained, which helps audit transformations. Their original leaderboard URLs, export parameters, and access timestamps were not retained. The repository should not imply that its code automatically downloads FanGraphs WAR.

### MLB API pulls

The scripts identify their endpoints and parameters but do not archive raw JSON responses. Re-running them can return corrections made after the original analysis. For durable research, save timestamped raw responses plus SHA-256 checksums.

## Redistribution and licensing

- The repository license applies to original code and documentation only.
- MLB, Baseball Savant, FanGraphs, Spotrac, and Forbes-style data remain subject to their respective terms, licenses, and database rights.
- Inclusion of a small source snapshot for project review does not grant downstream redistribution rights.
- Before publishing or redistributing raw third-party files, review each provider's current terms. If redistribution is not permitted, remove the raw file and provide a documented acquisition procedure instead.

## Citation guidance

When presenting results, cite the source and the transformation separately. Example:

> Pitching statistics were assembled from MLB Stats API and Statcast, with regular-season WAR taken from retained FanGraphs exports. IL days were reconstructed by the author from MLB transaction descriptions and are not an official MLB injury-duration field.

For financial results, use qualified wording:

> Financial outcomes are based on public external estimates rather than audited club statements; the exact page-level provenance for some inherited values was not preserved, and 2026 values are preliminary.
