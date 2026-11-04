"""Two-panel figure (p=20, p=200): median largest principal angle vs gamma, IQR bands.

Okabe-Ito colours (validated for CVD separation) + distinct markers/line styles + legend, so identity
never depends on colour alone. R references are black/grey dashed lines. The fallback CellPCA line is
dotted with hollow markers and no band (only medians are available from the earlier run).
"""
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "fig_angles.png"

STYLE = {  # method -> (label, colour, marker, linestyle, linewidth, hollow)
    "PCA (scikit-learn)": ("PCA", "#0072B2", "o", "-", 2.2, False),
    "ROBPCA (RobPy)": ("ROBPCA", "#56B4E9", "s", "-", 2.2, False),
    "DDC->ROBPCA (RobPy)": ("DDC→ROBPCA", "#E69F00", "D", "-", 2.2, False),
    "PCP (dfm/pcp)": ("PCP", "#009E73", "^", "-", 2.2, False),
    "CellPCA (robustcov)": ("CellPCA (earlier run, not re-run)", "#D55E00", "v", ":", 2.6, True),
    "R cellWise::MacroPCA (reference)": ("R MacroPCA (ref.)", "#666666", "P", "-.", 3.0, False),
    "R cellPCA, authors' code (reference)": ("R cellPCA (ref.)", "#000000", "X", "--", 3.2, False),
}


def main():
    s = pd.read_csv(ROOT / "results" / "summary.csv")
    plt.rcParams.update({"font.size": 16, "axes.titlesize": 18, "axes.labelsize": 17,
                         "legend.fontsize": 14, "xtick.labelsize": 15, "ytick.labelsize": 15})
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6), sharey=True)
    handles = {}
    for ax, p in zip(axes, (20, 200)):
        for m, (lab, col, mk, ls, lw, hollow) in STYLE.items():
            d = s[(s.method == m) & (s.p == p)].sort_values("gamma")
            if d.empty:
                continue
            n = int(d.n_runs.min()) if d.n_runs.nunique() == 1 else f"{int(d.n_runs.min())}–{int(d.n_runs.max())}"
            (h,) = ax.plot(d.gamma, d["median"], color=col, marker=mk, ls=ls, lw=lw, ms=9,
                           mfc="white" if hollow else col, mew=2, zorder=3)
            if d["q25"].notna().any():
                ax.fill_between(d.gamma, d.q25, d.q75, color=col, alpha=0.15, lw=0, zorder=1)
            handles[m] = (h, lab if n == 25 else f"{lab} (n={n})")
        ax.set_title(f"p = {p}  (n = 100, 20% cells shifted)")
        ax.set_xlabel(r"cell shift $\gamma$ (in units of $\sigma_j$)")
        ax.set_xticks([0, 2, 4, 6])
        ax.grid(axis="y", color="#dddddd", lw=0.8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0].set_ylabel("largest principal angle (°)\nmedian, band = IQR")
    axes[0].set_ylim(bottom=0)
    hs = [handles[m] for m in STYLE if m in handles]
    fig.legend([h for h, _ in hs], [l for _, l in hs], loc="lower center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, 0.0), handlelength=3)
    fig.tight_layout(rect=(0, 0.16, 1, 1))
    fig.savefig(OUT, dpi=300)
    print("saved", OUT)


if __name__ == "__main__":
    main()
