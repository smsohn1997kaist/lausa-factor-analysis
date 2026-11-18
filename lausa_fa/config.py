"""Model settings. Edit this file to apply LAUSA to other data."""

# Factor extraction: principal axis factoring (PAF)
N_FACTORS = None      # None: Kaiser criterion (eigenvalues of the correlation matrix R >= 1)
PAF_EPS = 1e-5        # stop when sum_i |c_i^2(k+1) - c_i^2(k)| < PAF_EPS
PAF_MAX_ITER = 1000

# Varimax rotation with Kaiser normalisation
VARIMAX_NORMALIZE = True
VARIMAX_TOL = 1e-5
VARIMAX_MAX_ITER = 500

# Factor numbering and sign.
# By default, factors keep the extraction order (largest eigenvalue first) and the signs
# returned by the eigendecomposition. After inspecting loadings.csv, you can fix them here:
#   FACTOR_ORDER = [3, 1, 2, ...]   extracted factor (1-based) that becomes Factor_1, Factor_2, ...
#   FACTOR_SIGNS = [1, -1, 1, ...]  sign applied to each factor after reordering
FACTOR_ORDER = None
FACTOR_SIGNS = None

# Dimension scores: signed sums of factor scores.
# The defaults are the definitions used in the paper. For other data, interpret the factors
# from loadings.csv first and then set these.
SUITABILITY = {"Factor_2": -1, "Factor_3": 1, "Factor_4": 1}
ATTRACTIVENESS = {"Factor_1": 1, "Factor_5": 1, "Factor_6": 1}

# v = alpha * Suitability + (1 - alpha) * Attractiveness
ALPHAS = [0.0, 0.2, 0.25, 0.4, 0.5, 0.6, 0.75, 0.8, 1.0]
THETA = 2.0  # an areal unit is a candidate when v >= THETA
