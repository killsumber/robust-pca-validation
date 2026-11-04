# Q&A preparation: Team 4 progress presentation

All numbers below come from `results/summary.csv` (this session, 4 Nov 2026) or the labelled fallback table.

**1. Isn't this "just a wrapper" around existing packages?**
No. The adapters are the smallest part. The deliverable is the validation itself:
- a fixed protocol (scenarios, a metric, and tolerances set before running);
- an R reference run as a black box on the *same* datasets;
- a failure map and reproducible reports to maintainers.

Nobody has published this comparison for the Python tools. Even a "they all agree with R" result is new information for users.

**2. What exactly is the angle metric?**
1. Orthonormalise the estimated p×2 loadings (QR).
2. Take the singular values of Qᵀ U, where U is the true basis. These are the cosines of the principal angles.
3. Report the largest angle, arccos of the smallest singular value.

0° means the same subspace; 90° means some true direction is completely missed. The metric ignores sign flips, rotations within the subspace and loading scale, so it compares packages with different conventions fairly.

**3. Why does PCP behave so differently: flat, but never near 0°?**
PCP fits a different model, low-rank plus sparse, with a fixed penalty λ = 1/√max(n, p). It is not a robust estimate of a covariance's eigenvectors. Because the outlying cells go into the sparse part, it is insensitive to the shift size. However, the low-rank part does not target the true covariance subspace, which is why it plateaus at about 10.1° (p = 20) and 6.9° (p = 200). It is a different estimand, not a bug.

**4. What if R shows the same behaviour as CellPCA?**
Then the finding is "robustcov agrees with R", and that is still a deliverable together with the suite and the failure map; the proposal anticipated this case. So far, R cellPCA does *not* behave like the earlier CellPCA run at p = 20, γ = 6: 4.0° vs 44.0°. But robustcov has not been re-run, so this remains a lead.

**5. So is robustcov CellPCA wrong?**
We cannot say that yet:
- The CellPCA numbers are from an earlier run (robustcov 0.2.0). The package is not installable from PyPI as of 4 Nov 2026, and its status is being clarified.
- We compared to the true subspace, not yet to the R subspace with the pre-fixed tolerance.
- At γ = 4, p = 20, R cellPCA itself is highly variable (median 16.5°, IQR 6.7–30.0°).

The difference is clear only at γ = 6.

**6. Why p = 20 and p = 200?**
These are the two dimensions in the cellPCA paper's simulation, so we can check the published claim directly: at n = 100 they span p < n and p > n. Our earlier lead also concerns exactly the p = 20 case. The broader grid (p up to 7129, with R only up to p ≤ 1000) comes next.

**7. What are the limits of your simulation?**
- It is our approximation of the paper's setting, not the authors' generator. The third eigenvalue is 0.11, the rest 0.10.
- Shifts are always positive (+γσ_j).
- There is a single contamination pattern: 20% of cells, uniformly at random.
- The latest R/DDC timings are wall-clock with parallel jobs.

The R reference still reproduces the paper's qualitative claim in our setting: error at γ = 6 is 10.8× below PCA at p = 20 and 6.7× at p = 200. So the setting is not grossly off.

**8. Licensing: cellWise is GPL. Does that affect your package?**
We use R strictly as a black box: Rscript plus CSV files, no rpy2 and no R code copied into our package. The R reference is an optional dependency. The authors' cellPCA zip has no licence statement, so we run it locally and do not redistribute it.

**9. Why does RobPy's DDC → ROBPCA do so poorly? Your proposal said it was comparable to CellPCA.**
With RobPy defaults, DDC → ROBPCA is no better than PCA up to γ = 4 (p = 200: 17.2° vs 16.3°). At p = 20, γ = 6 its IQR is very wide (13.2–56.6°). This contradicts our proposal's impression, which came from earlier, less systematic runs. Before reporting it as a RobPy issue we will check our adapter configuration: DDC thresholds, imputation, and ROBPCA settings.

**10. Is the R reference fast enough for the full grid?**
Not for all of it. The authors' cellPCA took about 5.5 s per run at p = 200 (MacroPCA 0.4 s, wall time with parallel jobs). Its cost grows with p, so we planned R runs only up to p ≤ 1000, with fastDDC where needed. Python DDC is already about 40 s per run at p = 200, because RobPy has no fastDDC.

### Statements that are still hypotheses or unverified
- "robustcov CellPCA behaves differently from published cellPCA at p ≈ 20": a lead, not re-run.
- Golub data at OpenML 45090: the link has not been opened or verified yet.
- The DDC → ROBPCA weakness may be our adapter configuration, not RobPy itself.
