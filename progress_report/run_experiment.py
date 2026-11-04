"""Run Python methods on the paper-setting grid; append one row per (method, p, gamma, seed) to a CSV.

Resumable: rows already in the CSV are skipped. Example:
    python run_experiment.py --methods pca pcp --gammas 4 --seeds 25
"""
import os

# One BLAS thread per worker process; parallelism comes from the process pool.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import csv
import time
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "results" / "angles_raw.csv"
FIELDS = ["method", "p", "gamma", "seed", "angle_deg", "seconds", "status"]


def one_run(method, p, gamma, seed, q=2):
    warnings.filterwarnings("ignore")
    from adapters import REGISTRY
    from metrics import largest_principal_angle
    from scenarios.paper_setting import generate
    X, U = generate(p, gamma, seed)
    t0 = time.perf_counter()
    try:
        V = REGISTRY[method](X, q)
        ang, status = largest_principal_angle(V, U), "ok"
    except Exception as e:  # recorded, never silently dropped
        ang, status = float("nan"), f"error: {type(e).__name__}: {e}"[:200]
    return dict(method=method, p=p, gamma=gamma, seed=seed, angle_deg=ang,
                seconds=round(time.perf_counter() - t0, 3), status=status)


def done_keys():
    if not RAW.exists():
        return set()
    with RAW.open() as f:
        return {(r["method"], int(r["p"]), float(r["gamma"]), int(r["seed"])) for r in csv.DictReader(f)}


def main():
    from adapters import SHORT
    from scenarios.paper_setting import SEED_BASE
    ap = argparse.ArgumentParser()
    ap.add_argument("--methods", nargs="+", default=["pca", "pcp", "robpca", "spca"], choices=list(SHORT))
    ap.add_argument("--ps", nargs="+", type=int, default=[20, 200])
    ap.add_argument("--gammas", nargs="+", type=float, default=[0, 2, 4, 6])
    ap.add_argument("--seeds", type=int, default=25, help="number of runs; seeds 1000..1000+n-1")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    a = ap.parse_args()

    done = done_keys()
    jobs = [(SHORT[m], p, g, SEED_BASE + s) for g in a.gammas for p in a.ps for m in a.methods
            for s in range(a.seeds) if (SHORT[m], p, g, SEED_BASE + s) not in done]
    print(f"{len(jobs)} jobs, {a.workers} workers", flush=True)
    RAW.parent.mkdir(exist_ok=True)
    new = not RAW.exists()
    with RAW.open("a", newline="") as f, ProcessPoolExecutor(a.workers) as ex:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        futs = [ex.submit(one_run, *j) for j in jobs]
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            w.writerow(r)
            f.flush()
            if r["status"] != "ok" or i % 20 == 0:
                print(i, r, flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
