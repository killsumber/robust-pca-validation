import argparse, urllib.request, warnings
import numpy as np
from sklearn.decomposition import PCA
import robustcov as rc
warnings.filterwarnings("ignore")
urllib.request.urlretrieve("https://raw.githubusercontent.com/dfm/pcp/main/pcp.py", "pcp_dfm.py")
import pcp_dfm

def angle(V, U):
    V, _ = np.linalg.qr(V)
    return float(np.degrees(np.arccos(np.clip(np.linalg.svd(V.T @ U, compute_uv=False).min(), -1, 1))))
def top_right_vectors(L, k=2):
    return np.linalg.svd(L, full_matrices=False)[2][:k].T
def covariance(p, rng):
    lam = np.r_[(9.57, 6.70) if p == 20 else (104.88, 73.42), 0.11, np.full(p - 3, 0.10)]
    O, _ = np.linalg.qr(rng.normal(size=(p, p)))
    return (O * lam) @ O.T, O[:, :2]
def cellpca_loadings(X, q, p):
    C = np.asarray(rc.CellPCA(n_components=q).fit(X).components_)
    return (C.T if C.shape[1] == p else C)[:, :q]
def run(p, gamma, n=100, q=2, reps=25, frac=0.20):
    res = {"PCA": [], "CellPCA (robustcov)": [], "PCP (dfm/pcp)": []}
    for s in range(reps):
        rng = np.random.default_rng(1000 + s)
        S, U = covariance(p, rng)
        X = rng.multivariate_normal(np.zeros(p), S, size=n)
        X = X + (rng.random((n, p)) < frac) * gamma * np.sqrt(np.diag(S))
        res["PCA"].append(angle(PCA(q).fit(X).components_.T, U))
        res["CellPCA (robustcov)"].append(angle(cellpca_loadings(X, q, p), U))
        L, _, _ = pcp_dfm.pcp(X - np.median(X, 0), maxiter=300, svd_method="exact")
        res["PCP (dfm/pcp)"].append(angle(top_right_vectors(L), U))
    print(f"p={p:3d} gamma={gamma}: median angle  " + "  ".join(f"{k} {np.median(v):5.1f}" for k, v in res.items()), flush=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--all", action="store_true"); a = ap.parse_args()
    for p in (20, 200):
        for g in ((0, 2, 4, 6) if a.all else (4,)):
            run(p, g)
