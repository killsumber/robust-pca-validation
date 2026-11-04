import numpy as np


def largest_principal_angle(V, U):
    """Largest principal angle (degrees) between span(V) and span(U); U must be orthonormal.

    cos(angles) are the singular values of Q_V^T U; the largest angle corresponds to the smallest one.
    """
    V, _ = np.linalg.qr(V)
    smin = np.linalg.svd(V.T @ U, compute_uv=False).min()
    return float(np.degrees(np.arccos(np.clip(smin, -1, 1))))
