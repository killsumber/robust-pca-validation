"""Combine per-run angles (Python + R) with the labelled fallback table into results/summary.csv."""
from pathlib import Path

import pandas as pd

R = Path(__file__).resolve().parent / "results"
FALLBACK_LABEL = "earlier run, robustcov 0.2.0, not re-run"


def write_fallback():
    """Fallback medians supplied by the team (earlier run with robustcov 0.2.0). Used ONLY for CellPCA,
    the one method that could not be re-run; PCA/PCP values are kept for the equivalence check."""
    vals = {  # (p, gamma): (PCA, CellPCA, PCP)
        (20, 0): (3.4, 3.5, 4.9), (20, 2): (9.8, 10.2, 10.1), (20, 4): (26.0, 32.5, 10.7), (20, 6): (43.8, 44.0, 10.7),
        (200, 0): (3.2, 3.2, 3.7), (200, 2): (8.7, 5.4, 6.6), (200, 4): (16.6, 4.8, 6.8), (200, 6): (25.4, 4.7, 6.8)}
    rows = []
    for (p, g), (pca, cell, pcp) in vals.items():
        for m, v in (("PCA (scikit-learn)", pca), ("CellPCA (robustcov)", cell), ("PCP (dfm/pcp)", pcp)):
            rows.append(dict(method=m, p=p, gamma=float(g), median=v, n_runs=25, source=FALLBACK_LABEL))
    pd.DataFrame(rows).to_csv(R / "fallback_table.csv", index=False)


def summarize():
    frames = [pd.read_csv(f) for f in (R / "angles_raw.csv", R / "angles_raw_r.csv") if f.exists()]
    d = pd.concat(frames, ignore_index=True)
    d["gamma"] = d["gamma"].astype(float)
    ok = d[d.status == "ok"]
    g = ok.groupby(["method", "p", "gamma"]).angle_deg
    s = pd.DataFrame({"median": g.median(), "q25": g.quantile(0.25), "q75": g.quantile(0.75),
                      "n_runs": g.size(), "median_seconds": ok.groupby(["method", "p", "gamma"]).seconds.median()}
                     ).reset_index()
    s["source"] = "this session (4 Nov 2026)"
    errs = d[d.status != "ok"].groupby(["method", "p", "gamma"]).size().rename("n_errors").reset_index()
    s = s.merge(errs, how="left", on=["method", "p", "gamma"]).fillna({"n_errors": 0})
    fb = pd.read_csv(R / "fallback_table.csv")
    fb = fb[fb.method == "CellPCA (robustcov)"]
    s = pd.concat([s, fb], ignore_index=True).sort_values(["p", "method", "gamma"])
    s.round(2).to_csv(R / "summary.csv", index=False)
    return s


if __name__ == "__main__":
    write_fallback()
    s = summarize()
    print(s.round(2).to_string(index=False))
