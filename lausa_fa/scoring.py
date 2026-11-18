"""Suitability, Attractiveness and v-scores from factor scores."""
import pandas as pd

from . import config


def weighted_sum(scores, weights):
    missing = [f for f in weights if f not in scores.columns]
    if missing:
        raise KeyError(f"factors not in the model: {missing}; check SUITABILITY and ATTRACTIVENESS")
    return sum(sign * scores[factor] for factor, sign in weights.items())


def dimension_scores(scores):
    return pd.DataFrame({
        "suitability": weighted_sum(scores, config.SUITABILITY),
        "attractiveness": weighted_sum(scores, config.ATTRACTIVENESS),
    }, index=scores.index)


def v_scores(dims, alphas=config.ALPHAS):
    """v(alpha) = alpha * Suitability + (1 - alpha) * Attractiveness, one column per alpha."""
    return pd.DataFrame({
        f"v_{a:.2f}": a * dims["suitability"] + (1 - a) * dims["attractiveness"] for a in alphas
    }, index=dims.index)


def candidate_counts(v, theta=config.THETA):
    """Number of areal units with v >= theta for each alpha."""
    return (v >= theta).sum().rename("n_candidates").to_frame()
