# LAUSA: Latent Analysis of Urban site Suitability and Attractiveness

Code for the factor analysis and site-scoring workflow of

> Sohn, S., Kim, N
> ., Hansen, M., Yoon, Y. (2026). Addressing Equity in Urban Air Mobility: Latent Analysis of Urban Site Suitability and Attractiveness (LAUSA). Transportation Research Interdisciplinary Perspectives (under review).

The code takes a table of attributes for areal units (one row per unit) and produces latent factors, Suitability and Attractiveness scores, and v-scores that rank units as candidate vertiport areas.

## Data

The dataset used in the paper combines attributes from the Seoul Open Data Plaza and the Seoul Big Data Campus, facility locations collected through the Kakao Map API, and publicly available aeronautical information on helipads and VFR routes. Data from the Seoul Big Data Campus and the Kakao Map API are subject to access or redistribution restrictions, so the full dataset is not publicly available. Attributes from the Seoul Open Data Plaza can be obtained from https://data.seoul.go.kr.

This repository contains the factor analysis code used in the study. The code takes a table of areal-unit attributes as input, so other researchers can run the same workflow on their own data.

## Method

| Step | Setting |
|---|---|
| Input | numeric attributes, one row per areal unit, no missing values |
| Standardisation | z-scores with the population standard deviation |
| Number of factors | Kaiser criterion: eigenvalues of the correlation matrix R ≥ 1 (or set by the user) |
| Extraction | principal axis factoring: squared multiple correlations as initial communalities, iterated until Σᵢ \|ĉᵢ²⁽ᵏ⁺¹⁾ − ĉᵢ²⁽ᵏ⁾\| < 10⁻⁵ |
| Rotation | varimax with Kaiser normalisation |
| Factor scores | F = Z Bᵀ, with B = (LᵀR⁻¹L)⁻¹LᵀR⁻¹ and L the rotated loadings |
| Suitability, Attractiveness | signed sums of factor scores (paper: Suitability = −F2 + F3 + F4, Attractiveness = F1 + F5 + F6) |
| v-score | v(α) = α · Suitability + (1 − α) · Attractiveness |
| Candidate unit | v ≥ θ (default θ = 2) |

All settings are in [lausa_fa/config.py](lausa_fa/config.py).

## Usage

```bash
pip install -r requirements.txt
python run_pipeline.py attributes.csv --out outputs
```

Options: `--id-col` (ID column; default: first column), `--exclude` (columns to leave out), `--n-factors` (default: Kaiser criterion).

Outputs in `outputs/`:

| File | Content |
|---|---|
| `eigenvalues.csv` | eigenvalues of the correlation matrix |
| `loadings.csv` | rotated loadings |
| `communalities.csv` | final communalities |
| `factor_variance.csv` | sum of squared loadings, proportion and cumulative variance |
| `factor_scores.csv` | factor scores per unit |
| `v_scores.csv` | Suitability, Attractiveness and v-score for each α |
| `candidate_counts.csv` | number of units with v ≥ θ for each α |

## Applying LAUSA to other data

The factors are derived from the data, so a different city or attribute set gives different factors.

1. Run the pipeline and read `loadings.csv`.
2. If needed, fix the factor numbering and signs with `FACTOR_ORDER` and `FACTOR_SIGNS` in the config.
3. Interpret the factors and set `SUITABILITY` and `ATTRACTIVENESS` (factor and sign) for your context.
4. Run the pipeline again to get the v-scores and candidate counts.

## Layout

```
lausa_fa/config.py        model settings, dimension definitions, α and θ
lausa_fa/factor_model.py  input check, standardisation, PAF, varimax, factor scores
lausa_fa/scoring.py       Suitability, Attractiveness, v-scores, candidate counts
run_pipeline.py           command-line entry point
```

## License

MIT. See [LICENSE](LICENSE).
