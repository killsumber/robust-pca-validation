"""R bridge (Rscript + CSV, no rpy2): export the SAME generated data sets, fit in R, read loadings back,
compute the same angle metric, append rows to results/angles_raw_r.csv.

Example:  python r_bridge/run_r.py --method macropca --gammas 4 6 --seeds 10
CSV exchange happens in an ASCII-only temp dir because Rscript on Windows can mishandle non-ASCII paths.
"""
import argparse
import csv
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from metrics import largest_principal_angle  # noqa: E402
from scenarios.paper_setting import SEED_BASE, generate  # noqa: E402

RSCRIPT = os.environ.get("RSCRIPT", r"C:\Program Files\R\R-4.6.2\bin\Rscript.exe")
RLIB = os.environ.get("RLIB", str(Path(os.environ.get("LOCALAPPDATA", "")) / "R" / "win-library" / "4.6"))
CELLPCA_CODE = ROOT / "vendor" / "r_cellpca_download" / "extracted" / "cellPCA_R_code_and_example_script" / "cellPCA_code.R"
NAMES = {"macropca": "R cellWise::MacroPCA (reference)", "cellpca": "R cellPCA, authors' code (reference)"}
OUT = ROOT / "results" / "angles_raw_r.csv"
FIELDS = ["method", "p", "gamma", "seed", "angle_deg", "seconds", "status"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", choices=list(NAMES), required=True)
    ap.add_argument("--ps", nargs="+", type=int, default=[20, 200])
    ap.add_argument("--gammas", nargs="+", type=float, default=[0, 2, 4, 6])
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--procs", type=int, default=6, help="parallel Rscript processes")
    a = ap.parse_args()

    work = Path(tempfile.gettempdir()) / "hdda_rbridge"
    (work / "in").mkdir(parents=True, exist_ok=True)
    (work / "out").mkdir(exist_ok=True)
    shutil.copy(ROOT / "r_bridge" / "fit_r.R", work / "fit_r.R")
    if a.method == "cellpca":
        shutil.copy(CELLPCA_CODE, work / "cellPCA_code.R")

    done = set()
    if OUT.exists():
        with OUT.open() as f:
            done = {(r["method"], int(r["p"]), float(r["gamma"]), int(r["seed"])) for r in csv.DictReader(f)}
    jobs, files, truth = [], [], {}
    for g in a.gammas:
        for p in a.ps:
            for s in range(a.seeds):
                seed = SEED_BASE + s
                if (NAMES[a.method], p, g, seed) in done:
                    continue
                X, U = generate(p, g, seed)
                fx = work / "in" / f"X_p{p}_g{g:g}_s{seed}.csv"
                np.savetxt(fx, X, delimiter=",", fmt="%.17g")
                jobs.append((p, g, seed, fx)); files.append(fx); truth[fx] = U
    print(f"{len(jobs)} R jobs ({a.method})", flush=True)

    # Split files across parallel Rscript processes, keeping gamma order (largest-priority first).
    chunks = [files[i::a.procs] for i in range(a.procs)]
    procs = []
    for i, ch in enumerate(c for c in chunks if c):
        lst = work / f"list_{a.method}_{i}.txt"
        lst.write_text("\n".join(str(f) for f in ch))
        cmd = [RSCRIPT, str(work / "fit_r.R"), a.method, str(lst), str(work / "out")]
        if a.method == "cellpca":
            cmd.append(str(work / "cellPCA_code.R"))
        procs.append(subprocess.Popen(cmd, env={**os.environ, "RLIB": RLIB},
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
    for pr in procs:
        log = pr.communicate()[0]
        if pr.returncode != 0:
            print("Rscript failed:", log[-2000:], flush=True)

    new = not OUT.exists()
    with OUT.open("a", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        for p, g, seed, fx in jobs:
            base = work / "out" / f"{fx.stem}_{a.method}"
            if base.with_suffix(".csv").exists():
                V = np.loadtxt(base.with_suffix(".csv"), delimiter=",", ndmin=2)
                row = dict(angle_deg=largest_principal_angle(V, truth[fx]), status="ok",
                           seconds=round(float(base.with_suffix(".time").read_text()), 3))
            else:
                err = base.with_suffix(".err")
                row = dict(angle_deg=float("nan"), seconds="", status="error: " + (
                    err.read_text().strip()[:200] if err.exists() else "no output (Rscript failed)"))
            w.writerow(dict(method=NAMES[a.method], p=p, gamma=g, seed=seed, **row))
    print("done", flush=True)


if __name__ == "__main__":
    main()
