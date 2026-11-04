# Progress report (HDDA, Team 4)

Experiments, figure and slides for the progress presentation. The code here is a
self-contained first version. It will later move into the `src/robust_pca_validation` package.

## Contents
| Path | What |
|---|---|
| `scenarios/paper_setting.py` | synthetic setting approximating the cellPCA paper (n=100, p∈{20,200}, 20% cells shifted by γσ_j) |
| `adapters/` | one function per method → p×2 loadings (PCA, PCP dfm/pcp, ROBPCA, spherical PCA, DDC→ROBPCA, CellPCA) |
| `metrics.py` | largest principal angle (degrees) |
| `r_bridge/` | R reference (cellWise::MacroPCA, authors' cellPCA) via Rscript + CSV, no rpy2 |
| `run_experiment.py`, `summarize.py`, `make_figure.py` | run grid → `results/summary.csv` → `results/fig_angles.png` |
| `slides/` | `progress_team4.pptx` / `.pdf`, speaker script for three speakers, Q&A notes |
| `VERSIONS.md` | exact versions, sha256 of third-party code, robustcov status, how to reproduce |

## Status (4 Nov 2026)
- The R reference reproduces the paper's behaviour in our setting: at γ = 6, R cellPCA is 4.0° / 3.8° vs PCA 43.9° / 25.2° (p = 20 / 200).
- robustcov is not installable from PyPI as of 4 Nov 2026, and its status is being clarified. The CellPCA numbers come from an earlier run and are labelled that way. The p = 20 discrepancy is a **lead, not a verdict**.

## Not in git
- `vendor/pcp_dfm.py` is downloaded on first use, with a sha256 check.
- `vendor/r_cellpca_download/` holds the authors' cellPCA R code, which has no licence statement. Download it yourself from
  https://wis.kuleuven.be/statdatascience/robust/software ("cellPCA … zipfile with R code").
