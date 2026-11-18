"""Run LAUSA: attribute table -> PAF factor scores -> Suitability / Attractiveness -> v-scores.

Usage:
    python run_pipeline.py attributes.csv --out outputs
"""
import argparse
from pathlib import Path

import pandas as pd

from lausa_fa import config, factor_model, scoring


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("table", help="areal-unit attributes (.csv or .xlsx), one row per unit")
    parser.add_argument("--id-col", help="ID column (default: first column)")
    parser.add_argument("--exclude", nargs="*", default=[], help="columns to leave out of the model")
    parser.add_argument("--n-factors", type=int, help="number of factors (default: Kaiser criterion)")
    parser.add_argument("--out", default="outputs", help="output directory (default: outputs)")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    fm = factor_model.run(args.table, args.id_col, args.exclude, args.n_factors)
    fm["eigenvalues"].to_csv(out / "eigenvalues.csv")
    fm["loadings"].to_csv(out / "loadings.csv")
    fm["communalities"].to_csv(out / "communalities.csv")
    fm["variance"].to_csv(out / "factor_variance.csv")
    fm["scores"].to_csv(out / "factor_scores.csv")

    pd.set_option("display.width", 160)
    n_units, n_vars = len(fm["scores"]), len(fm["loadings"])
    print(f"units: {n_units}, attributes: {n_vars}, factors: {fm['loadings'].shape[1]}, "
          f"PAF iterations: {fm['n_iter']}")
    print("\nFactor variance:\n", fm["variance"].round(3))
    print("\nRotated loadings:\n", fm["loadings"].round(3))

    try:
        dims = scoring.dimension_scores(fm["scores"])
    except KeyError as err:
        print(f"\n{err}\nFactor outputs written to {out}/; v-scores skipped.")
        return
    v = scoring.v_scores(dims)
    pd.concat([dims, v], axis=1).to_csv(out / "v_scores.csv")
    counts = scoring.candidate_counts(v)
    counts.to_csv(out / "candidate_counts.csv")
    print(f"\nCandidates (v >= {config.THETA}):\n", counts.T)
    print(f"\nOutputs written to {out}/")


if __name__ == "__main__":
    main()
