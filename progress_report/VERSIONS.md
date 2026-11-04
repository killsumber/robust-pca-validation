# Environment and provenance (run of 4 Nov 2026)

## System
- OS: Windows 11 Home 10.0.26200, 6 cores / 12 threads
- Python 3.13.5 (venv `../.venv`)
- R 4.6.2 (2026-10-29), installed with `winget install RProject.R --source winget`
  - user library `%LOCALAPPDATA%\R\win-library\4.6`
  - packages: cellWise 2.5.7, RobStatTM 1.0.11, rrcov 1.7.7, robustHD 0.8.4 (TopGear data only), MASS 7.3.66
- Slides rendered with Microsoft PowerPoint (COM export to PDF), then PyMuPDF 2.1 to PNG. LibreOffice is not installed.

## Python packages (pip freeze, main ones)
numpy 2.5.4 · scipy 1.18.1 · pandas 3.1.1 · scikit-learn 1.6.1 · matplotlib 3.11.2 · robpy 0.0.6 · fbpca 1.0 ·
python-pptx 1.0.2 · pymupdf 2.1. The full list is in the `pip freeze` output below.

```
cloudpickle==3.1.2 colorama==0.4.6 contourpy==1.4.0 cycler==0.12.1 fbpca==1.0 flatbuffers==25.12.19
fonttools==4.68.0 joblib==1.6.0 kiwisolver==1.5.1 lxml==6.1.3 matplotlib==3.11.2 networkx==3.7 numpy==2.5.4
onnxruntime==1.31.1 packaging==26.3 pandas==3.1.1 patsy==1.0.3 pillow==13.0.0 protobuf==7.36.2 psutil==7.2.2
pymupdf==2.1 pymupdf4llm==2.1 pymupdf_layout==2.1 pyparsing==3.3.3 python-dateutil==4.0.0 python-pptx==1.0.2
PyYAML==6.0.3 robpy==0.0.6 scikit-learn==1.6.1 scipy==1.18.1 seaborn==0.13.2 statsmodels==0.14.6
tabulate==0.10.0 threadpoolctl==3.7.0 tqdm==4.70.1 typing_extensions==4.16.0 tzdata==2026.6 xlsxwriter==3.3.1
```

## robustcov: NOT available (checked 4 Nov 2026)
| Check | Result |
|---|---|
| `pip index versions robustcov` (also with `--pre`) | `ERROR: No matching distribution found for robustcov` |
| `pip download robustcov --no-deps -d vendor/` | `Could not find a version that satisfies the requirement robustcov (from versions: none)` |
| `https://pypi.org/pypi/robustcov/json` | HTTP 404 (the whole project, not only 0.2.0) |
| `git ls-remote https://github.com/smiryusupov/robustcov` | asks for credentials (repo private, renamed or removed; cause unknown) |

We could not check `rc.CellPCA` or `rc.__version__` because nothing could be installed.
CellPCA numbers in this repo are the team's **earlier run with robustcov 0.2.0, not re-run**, stored in
`results/fallback_table.csv` and labelled that way everywhere. On slides this status is worded as
"not installable from PyPI as of 4 Nov 2026, status being clarified".

## Vendored / downloaded third-party code
| File | Source | sha256 | Licence note |
|---|---|---|---|
| `vendor/pcp_dfm.py` | https://raw.githubusercontent.com/dfm/pcp/main/pcp.py | `C888C28761F876E088D4FE7423E4715659DE2EA20C4F719B2E5858F206743F79` | licence not verified: not committed (in `.gitignore`); `adapters/pcp_dfm.py` downloads it on first use and refuses any file with a different sha256 |
| `vendor/r_cellpca_download/cellpca_r_code_and_example_script.zip` | https://wis.kuleuven.be/statdatascience/robust/papers/publications-2024/cellpca_r_code_and_example_script.zip (linked from the "Software" page of https://wis.kuleuven.be/statdatascience/robust) | `31A0692F31587EFC7D383E4542B5E290CC30EF922E8A62E1FC2B5FEC463907D3` | no licence statement in the files. Used locally as a black box via Rscript; do not copy into or ship with our package |
| `.../cellPCA_code.R` (from the zip) | same | `EF31C30D595BD282B588BDDCF526D9522FDB87426587250FE7A2135EE8447A0D` | read before running: it defines functions only, with no file, system or network access |

## Refactor equivalence (gamma = 4)
`legacy/setting_check.py` (the original script, kept unchanged for reference; it needs robustcov, which is unavailable) was refactored into `scenarios/`, `metrics.py` and `adapters/` with the same RNG call order.
Medians from this session compared with the earlier fallback table (95% bootstrap CI of the median, 25 runs):

| method | p | now | 95% CI | earlier | within CI |
|---|---|---|---|---|---|
| PCA | 20 | 27.02 | 23.03–31.37 | 26.0 | yes |
| PCP | 20 | 10.09 | 9.85–11.99 | 10.7 | yes |
| PCA | 200 | 16.32 | 16.00–17.10 | 16.6 | yes |
| PCP | 200 | 6.90 | 6.71–7.15 | 6.8 | yes |

The values are not bit-identical, even though the seeds and code are the same. The likely cause is a different numpy/LAPACK build on the earlier machine: `multivariate_normal` factorises Σ, whose 0.10 eigenvalue is repeated, so the factor is not unique. The BLAS thread count does not change the data here (checked in `check_equivalence.py`).
Setting details kept from the original script: the 3rd eigenvalue is **0.11** and the rest are 0.10; all shifts are positive (+γσ_j).

## R reference checks
- The TopGear MacroPCA example from the cellWise vignette is reproduced exactly (`results/topgear_check_output.txt`): data 296×11, cutoffOD 1.737869, cutoffSD 3.034854, 126 flagged cells. These are the same values the vignette prints.
- MacroPCA settings on the simulated data: `MacroPCA(X, k = 2, MacroPCApars = list(scale = FALSE, silent = TRUE))`, otherwise defaults. `scale = FALSE` is used because the true subspace refers to the unscaled covariance.
- cellPCA settings: `cellPCA(X, q = 2, trace = FALSE)`, the authors' defaults.

## How to reproduce
From the repository root (Python 3.12 or 3.13; R part needs R + the packages above, and the authors'
cellPCA zip placed in `vendor/r_cellpca_download/` as described in the table, since it is not in git):
```
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run_experiment.py --methods pca pcp robpca spca --seeds 25
.venv\Scripts\python.exe run_experiment.py --methods ddc --seeds 25
.venv\Scripts\python.exe r_bridge\run_r.py --method macropca --seeds 25
.venv\Scripts\python.exe r_bridge\run_r.py --method cellpca --seeds 25
.venv\Scripts\python.exe check_equivalence.py
.venv\Scripts\python.exe summarize.py
.venv\Scripts\python.exe make_figure.py
.venv\Scripts\python.exe slides\build_slides.py
.venv\Scripts\python.exe slides\check_numbers.py
powershell -File slides\render.ps1
```
The runners are resumable: rows already in `results/angles_raw*.csv` are skipped.
