"""Check that the refactored code reproduces the earlier gamma=4 numbers (fallback table) within sampling noise.

Sampling noise = 95% bootstrap interval of the median over the 25 runs. Also tests whether the generated
data depend on the BLAS/LAPACK thread count (multivariate_normal factorises Sigma, whose 0.10 eigenvalue is
repeated, so the factor is not unique and can differ between BLAS builds/machines).
"""
import subprocess
import sys

import numpy as np
import pandas as pd

FALLBACK_G4 = {("PCA (scikit-learn)", 20): 26.0, ("PCP (dfm/pcp)", 20): 10.7,
               ("PCA (scikit-learn)", 200): 16.6, ("PCP (dfm/pcp)", 200): 6.8}

d = pd.read_csv("results/angles_raw.csv")
rng = np.random.default_rng(0)
rows = []
for (m, p), ref in FALLBACK_G4.items():
    a = d[(d.method == m) & (d.p == p) & (d.gamma == 4)].angle_deg.to_numpy()
    boot = np.median(rng.choice(a, (5000, a.size)), axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    rows.append(dict(method=m, p=p, n_runs=a.size, median_now=round(np.median(a), 2), ci95_lo=round(lo, 2),
                     ci95_hi=round(hi, 2), fallback=ref, within_ci=bool(lo <= ref <= hi)))
out = pd.DataFrame(rows)
print(out.to_string(index=False))
out.to_csv("results/equivalence_gamma4.csv", index=False)

code = ("from scenarios.paper_setting import generate; import numpy as np; "
        "X,_=generate(200,4,1000); print(repr(float(X.sum())))")
for threads in ("1", "6"):
    env = {**__import__("os").environ, "OMP_NUM_THREADS": threads, "OPENBLAS_NUM_THREADS": threads}
    print("threads", threads, "sum(X) seed 1000, p=200:",
          subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True).stdout.strip())
