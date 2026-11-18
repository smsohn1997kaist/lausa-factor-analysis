"""Principal axis factoring, varimax rotation and factor scores."""
import numpy as np
import pandas as pd

from . import config


def load_table(path, id_col=None, exclude=()):
    """Read a table of areal-unit attributes. Returns the numeric attributes indexed by ID.

    id_col defaults to the first column. Missing values must be handled beforehand.
    """
    df = pd.read_excel(path) if str(path).endswith((".xlsx", ".xls")) else pd.read_csv(path)
    id_col = id_col or df.columns[0]
    df = df.set_index(id_col).drop(columns=list(exclude), errors="ignore")
    df = df.select_dtypes("number")
    if df.index.duplicated().any():
        raise ValueError(f"duplicate IDs in column {id_col}")
    if df.isna().any().any():
        raise ValueError("the table contains missing values")
    return df


def standardize(x):
    """z-scores with the population standard deviation (ddof = 0)."""
    sd = x.std(ddof=0)
    if (sd == 0).any():
        raise ValueError(f"constant columns: {sd.index[sd == 0].tolist()}")
    return (x - x.mean()) / sd


def kaiser_n_factors(R):
    """Number of eigenvalues of the correlation matrix that are >= 1."""
    return int((np.linalg.eigvalsh(R) >= 1).sum())


def paf(R, n_factors, eps=config.PAF_EPS, max_iter=config.PAF_MAX_ITER):
    """Principal axis factoring on the correlation matrix R.

    Initial communalities are squared multiple correlations, c_i^2(0) = 1 - 1/r^ii.
    Each iteration replaces the diagonal of R with the current communalities (R*),
    takes the eigendecomposition R* = Q Lambda Q^T, sets L = Q_M Lambda_M^(1/2) for the
    M leading factors, and updates c_i^2 = sum_m l_im^2. Iteration stops when the total
    absolute change in communalities is below eps.
    """
    h2 = 1 - 1 / np.diag(np.linalg.inv(R))
    for k in range(1, max_iter + 1):
        R_star = R.copy()
        np.fill_diagonal(R_star, h2)
        lam, Q = np.linalg.eigh(R_star)
        idx = np.argsort(lam)[::-1][:n_factors]
        L = Q[:, idx] * np.sqrt(np.clip(lam[idx], 0, None))
        h2_new = (L ** 2).sum(axis=1)
        if np.abs(h2_new - h2).sum() < eps:
            if (h2_new > 1).any():
                print("warning: communality above 1 (Heywood case)")
            return L, h2_new, k
        h2 = h2_new
    raise RuntimeError(f"PAF did not converge in {max_iter} iterations")


def varimax(L, normalize=config.VARIMAX_NORMALIZE, tol=config.VARIMAX_TOL, max_iter=config.VARIMAX_MAX_ITER):
    """Varimax rotation. Returns the rotated loadings L V and the rotation matrix V."""
    p, m = L.shape
    if m < 2:
        return L.copy(), np.eye(m)
    h = np.sqrt((L ** 2).sum(axis=1, keepdims=True)) if normalize else np.ones((p, 1))
    A = L / h
    V = np.eye(m)
    d = 0.0
    for _ in range(max_iter):
        B = A @ V
        U, s, Wt = np.linalg.svd(A.T @ (B ** 3 - B @ np.diag((B ** 2).sum(axis=0)) / p))
        V = U @ Wt
        d_old, d = d, s.sum()
        if d_old != 0 and d / d_old < 1 + tol:
            break
    return (A @ V) * h, V


def factor_scores(Z, R, L):
    """Factor scores F = Z B^T with B = (L^T R^-1 L)^-1 L^T R^-1."""
    R_inv = np.linalg.inv(R)
    B = np.linalg.solve(L.T @ R_inv @ L, L.T @ R_inv)
    return Z @ B.T


def arrange(L, order=None, signs=None):
    """Apply FACTOR_ORDER (1-based) and FACTOR_SIGNS to the loading columns."""
    m = L.shape[1]
    order = list(range(m)) if order is None else [i - 1 for i in order]
    if sorted(order) != list(range(m)):
        raise ValueError(f"FACTOR_ORDER must be a permutation of 1..{m}")
    signs = np.ones(m) if signs is None else np.asarray(signs, dtype=float)
    if signs.shape != (m,) or not set(np.abs(signs)) <= {1.0}:
        raise ValueError(f"FACTOR_SIGNS must have {m} entries of 1 or -1")
    return L[:, order] * signs


def run(path, id_col=None, exclude=(), n_factors=None):
    """Table of attributes -> PAF -> varimax -> factor scores."""
    x = load_table(path, id_col, exclude)
    Z = standardize(x)
    R = np.corrcoef(Z.values, rowvar=False)
    eigenvalues = np.sort(np.linalg.eigvalsh(R))[::-1]
    m = n_factors or config.N_FACTORS or kaiser_n_factors(R)

    L, h2, n_iter = paf(R, m)
    L_rot, _ = varimax(L)
    L_rot = arrange(L_rot, config.FACTOR_ORDER, config.FACTOR_SIGNS)
    names = [f"Factor_{i}" for i in range(1, m + 1)]

    ss = (L_rot ** 2).sum(axis=0)
    p = L_rot.shape[0]
    return {
        "n_iter": n_iter,
        "eigenvalues": pd.Series(eigenvalues, index=range(1, p + 1), name="eigenvalue"),
        "loadings": pd.DataFrame(L_rot, index=x.columns, columns=names),
        "communalities": pd.Series(h2, index=x.columns, name="communality"),
        "variance": pd.DataFrame({"ss_loadings": ss, "proportion": ss / p,
                                  "cumulative": np.cumsum(ss) / p}, index=names),
        "scores": pd.DataFrame(factor_scores(Z.values, R, L_rot), index=x.index, columns=names),
    }
