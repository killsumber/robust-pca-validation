"""Synthetic setting approximating the cellPCA paper (Centofanti, Hubert, Rousseeuw, arXiv:2408.13596).

This is OUR APPROXIMATION, not the authors' code. Refactored from setting_check.py
(paper_setting_check.py) without changing its numerical behaviour: same RNG calls in the same order.
"""
import numpy as np

# Two dominant eigenvalues per p; the third eigenvalue is 0.11 and the rest 0.10,
# exactly as in the original script (kept on purpose to reproduce earlier numbers).
DOMINANT_EIGENVALUES = {20: (9.57, 6.70), 200: (104.88, 73.42)}


def covariance(p, rng):
    """Return (Sigma, U): covariance with random orthonormal eigenvectors and its true 2-D subspace."""
    lam = np.r_[DOMINANT_EIGENVALUES[p], 0.11, np.full(p - 3, 0.10)]
    O, _ = np.linalg.qr(rng.normal(size=(p, p)))
    return (O * lam) @ O.T, O[:, :2]


def generate(p, gamma, seed, n=100, frac=0.20):
    """Data set for one run: n x p Gaussian sample, then each cell shifted by gamma*sigma_j with prob. frac."""
    rng = np.random.default_rng(seed)
    S, U = covariance(p, rng)
    X = rng.multivariate_normal(np.zeros(p), S, size=n)
    X = X + (rng.random((n, p)) < frac) * gamma * np.sqrt(np.diag(S))
    return X, U


SEED_BASE = 1000  # run s uses seed 1000 + s
