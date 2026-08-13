# Reproducibility Guide

## Reproducibility levels

This repository supports two different goals:

1. **Review reproduction:** rerun the analysis from the checked-in processed/snapshot data without calling external providers.
2. **Source reconstruction:** collect current data again from APIs and web pages, then rebuild all intermediate tables.

The first path is the stable analysis workflow. The second can change over time and is not yet fully automated for every field.

## Environment

Recommended local environment:

- Python 3.11 or newer
- `venv` and `pip`
- Node.js/npm for document generation
- Tableau Desktop or Tableau Public only if opening the packaged workbook

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm ci
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

## Stable review workflow

From the repository root, install Python and Node dependencies:

```bash
make setup
```

The workflow is split into explicit targets:

| Target | Purpose |
| --- | --- |
| `make setup` | Install runtime, development, and Node dependencies |
| `make data` | Rebuild processed pitcher, team, and peer-panel data from frozen inputs and validate them |
| `make database` | Load the canonical processed tables into the generated SQLite database |
| `make sql` | Build the database, then execute the documented hypothesis queries |
| `make analysis` | Run pitcher regressions, diagnostics, team pre/post, bridge, DiD, and event-study code |
| `make report` | Rebuild charts, the Excel workbook, and PDF/DOCX report outputs |
| `make test` | Run automated schema, transformation, and result checks |
| `make reproduce` | Run the full checked-in workflow in dependency order |

```bash
make data
make database
make sql
make analysis
make report
make test
```

Run all reproducible stages in dependency order with:

```bash
make reproduce
```

`make report` rebuilds figures and analysis report artifacts and therefore requires the Python and Node dependencies installed by `make setup`. `make test` runs the automated validation suite.

The expected canonical inputs are:

- `data/processed/pitcher_stats.csv`
- `data/processed/team_financials.csv`
- `data/processed/comparable_teams_financials.csv`

The primary statistical result table is:

- `data/processed/did_regression_results.csv`

The `data/snapshots/` directory contains inherited intermediates used for auditability. It should not silently override the canonical processed files.

## Pipeline map

```text
collect
  MLB Stats API / Statcast / Spotrac
    ↓
prepare
  innings conversion, joins, IL aggregation, financial normalization,
  postseason proxy, validation, SQLite build
    ↓
analyze
  SQL summaries, clustered pitcher regressions, bridge analysis,
  DiD, event study
    ↓
report
  figures, Excel workbook, PDF/DOCX, Tableau package
```

Scripts are organized by purpose:

```text
scripts/collect/    external acquisition
scripts/prepare/    transformation and validation
scripts/analyze/    statistical analysis
scripts/report/     output generation
```

## Source reconstruction workflow

The collection scripts can be run individually from the repository root:

```bash
python3 scripts/collect/collect_pitcher_stats.py
python3 scripts/collect/collect_injuries.py
python3 scripts/collect/collect_team_financials.py
python3 scripts/collect/collect_cbt_tax.py
python3 scripts/collect/collect_attendance.py
```

Preparation scripts then normalize and merge inputs. Check each script's input/output paths before running because the project layout separates `data/raw`, `data/processed`, and inherited `data/snapshots`.

Important: this path is **not a guaranteed clean-room rebuild**. The original collection script intentionally emits missing WAR and IL fields; retained FanGraphs exports and separate injury outputs must be merged. Exact source URLs/access dates for manually supplied financial estimates were not preserved. Therefore, do not overwrite the canonical processed tables until row counts, keys, and key estimates have been compared.

## Validation checkpoints

After a rebuild, verify at minimum:

| Check | Expected snapshot value |
| --- | ---: |
| Pitcher table rows | 221 |
| Unique pitchers | 129 |
| Rows with `low_sample_flag = 0` | 184 |
| Unique pitchers in regression sample | 106 |
| Velocity-bucket counts | 36 / 46 / 65 / 37 |
| Dodgers financial rows | 7 |
| Comparable-panel rows | 60 |
| Teams in comparable panel | 6 |
| Comparable-panel seasons | 2017–2026 |
| Duplicate (`season`, `player_id`) keys | 0 |
| Duplicate (`team`, `season`) peer keys | 0 |

Key result tolerances should be asserted rather than matched as formatted strings:

```text
IL-days velocity coefficient        ≈ 4.24
WAR/IP velocity coefficient         ≈ 0.0015
Revenue DiD coefficient             ≈ 97,371,429
Team-value DiD coefficient          ≈ 1,655,238,095
Operating-income DiD coefficient    ≈ -2,840,000
```

Floating-point last digits can differ by library/BLAS version. Sample definitions, units, signs, and meaningful decimal precision should not.

## Preventing accidental source overwrite

Before re-collection:

1. Work on a branch.
2. Save timestamped API responses or downloaded files under a dated raw-data directory.
3. Record URL, query parameters, access time, HTTP status, and SHA-256 checksum.
4. Write new processed outputs to a temporary/staging location.
5. Diff row counts, schemas, missingness, and estimates against the checked-in tables.
6. Promote new data only after documenting the revision.

## Known environment-sensitive steps

- Statcast collection can be slow and network-sensitive.
- Spotrac HTML parsers may break if table labels or access rules change.
- FanGraphs exports are retained files, not an automated API pull.
- PDF and DOCX rendering depends on installed fonts and document tooling.
- The Tableau `.twbx` file requires a compatible Tableau application for interactive review.

## Updating 2026 data

The current six-team panel contains preliminary, in-season 2026 estimates. When finalized data are available:

1. Preserve the current snapshot.
2. Add row-level source URLs and access dates.
3. Mark the new values as final or revised.
4. Rerun the full DiD and the model excluding 2020–2021.
5. Report a sensitivity model ending in 2025 so readers can see how much 2026 drives the result.
6. Regenerate figures, result CSVs, the executive summary, and the final report from the same output table.
