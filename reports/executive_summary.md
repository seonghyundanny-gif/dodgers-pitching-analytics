# Executive Summary

## The question

Do harder-throwing pitchers create enough performance value to justify their injury risk, and did the Dodgers' post-2024 roster strategy coincide with financial gains beyond those experienced by comparable clubs?

## Data and approach

The pitcher analysis covers 221 Dodgers pitcher-seasons from 2017–2019 and 2022–2025. The main regression sample excludes 37 observations below five innings, leaving 184 pitcher-seasons from 106 unique pitchers. Player-clustered OLS models relate average fastball velocity to reconstructed IL days, regular-season WAR per inning, and a simplified FIP-based postseason WAR proxy.

The team analysis combines a seven-season Dodgers financial table with a 60-observation panel of the Dodgers and five selected large-market peers—Yankees, Red Sox, Mets, Cubs, and Giants—from 2017–2026. A two-way fixed-effects Difference-in-Differences model compares the change for LAD after 2024 with the contemporaneous change among those peers.

## Findings

### Velocity presents a measurable risk–return trade-off

- A 1 mph increase in average fastball velocity is associated with approximately **4.24 additional IL days** (`p < 0.001`) after controlling for age and same-season innings.
- Excluding same-season innings from that model produces a similar estimate of **+4.28 IL days** (`p < 0.001`), reducing concern that the result is driven by that potentially endogenous control alone.
- The association remains positive in the smaller sample with an observed prior in-sample injury history: **+4.32 days** (`p = 0.031`, `n = 78`).
- A 1 mph increase is associated with **+0.0015 WAR per inning** (`p < 0.001`).
- The postseason proxy estimate is positive but inconclusive (`p = 0.075–0.116`).

Descriptively, 96+ mph pitcher-seasons have 45.9 average IL days and 0.0127 average WAR/IP, the highest values in both dimensions. This is consistent with a high-risk/high-upside profile, but does not establish that velocity caused either outcome.

### The post-2024 financial pattern differs by outcome

Relative to the five selected peers, the stored DiD model estimates a post-2024 LAD change of:

| Outcome | DiD estimate | Stored p-value | Interpretation |
| --- | ---: | ---: | --- |
| Revenue | +$97.37M | <0.001 | Positive relative change; exploratory |
| Team value | +$1.655B | <0.001 | Positive relative change; exploratory |
| Operating income | −$2.84M | 0.955 | No detectable relative change |
| Operating-income margin | −13.17 percentage points | 0.199 | Statistically inconclusive |

The revenue result is not a constant annual gain. The event-study pattern is approximately −$53M in 2024, +$98.6M in 2025, and +$171M in **preliminary 2026** data. This heterogeneity is more consistent with a delayed or bundled change than an immediate effect attributable to one signing.

### Velocity is not shown to drive revenue

A positive level correlation between team average velocity and revenue disappears after annualized first differencing. All differenced bridge correlations are statistically inconclusive (`p > 0.6`). The project therefore does not connect the pitcher-level velocity relationship causally to the financial DiD result.

## Decision implication

The evidence supports treating high velocity as one attribute in a broader pitching strategy rather than as an unconditional objective. A club should price both expected performance and downside exposure, while diversifying roles, medical risk, contract structure, and workload. The available data do not justify a single break-even dollar estimate for one additional mph.

The financial results are best read as a signal that the Dodgers' broader post-2024 period coincided with unusually strong revenue and valuation movement relative to the selected peers. They do not identify velocity, a specific player, or the superstar strategy alone as the causal mechanism.

## Critical caveats

- The pitcher models are observational and retain substantial unmeasured confounding.
- Same-season innings may be affected by injury and can be an endogenous control.
- IL days are parsed from transaction text; open or unmatched stints can be understated or zero-filled.
- WAR/IP is a volatile ratio, and the postseason outcome is a non-official proxy.
- The DiD has only six team clusters, so conventional cluster-robust p-values may be too optimistic.
- Pre-treatment revenue trends are not perfectly parallel, and peer selection is judgment-based.
- Financial inputs are external estimates, not audited statements; exact page-level provenance was not preserved for some inherited values.
- The 2026 financial values are preliminary and in-season.

## Recommended next step

Before treating the findings as decision-grade, validate injury spells, rerun workload specifications with prior-season controls, add count/hurdle and within-player models, apply wild-cluster bootstrap or randomization inference to the DiD, report a panel ending in 2025, and replace preliminary 2026 estimates when final figures are available.

For technical detail, see [Methodology](../docs/methodology.md), [Data Sources](../docs/data_sources.md), [Data Dictionary](../docs/data_dictionary.md), [Limitations](../docs/limitations.md), and [Reproducibility](../docs/reproducibility.md).
