# Speaker script: Team 4 progress presentation (15 min)

| Part | Speaker | Slides | Time |
|---|---|---|---|
| 1 | **Lev** | 1–4: title, problem, question and hypothesis, data | ~4.5 min |
| 2 | **Dinara** | 5–7: methods and metric, results, how the angle is computed | ~5.5 min |
| 3 | **Semen** | 8–9: analysis and challenges, next steps, then opens Q&A | ~4.5 min |

The **bold** sentence at the end of each part is the hand-over. The next speaker switches the slide.
All numbers match the slides and `results/summary.csv`; do not round them differently when speaking.

---

## Part 1: Lev (slides 1–4)

**Slide 1: Title** (~20 s)
> Good afternoon. We are Team 4: Dinara Bairamgazieva, Semen Vashurin and I, Lev Lesnoi. Our project is in the industrial track: we independently validate Python tools for cellwise-robust PCA against the R reference code. Today we report what we ran this week, what it shows, and what is still open.

**Slide 2: 20% bad cells touch almost every row** (~2 min)
> First, the problem. Classical robust PCA assumes that whole rows are bad: a broken sensor, a wrong patient record. In high-dimensional data the damage is usually different. Single cells are corrupted, and these are called cellwise outliers.
>
> The grid on the left shows why this matters. Orange cells are contaminated, 20% of them, at random. With 20 variables, only 1.2% of the rows are completely clean; with 200 variables, practically none. A rowwise-robust method like ROBPCA throws away suspicious rows, so it has almost nothing left to work with.
>
> Python now has several tools that are meant to handle this: robustcov's CellPCA, the DDC-then-ROBPCA pipeline in RobPy, and several PCP scripts. The reference implementations are in R: MacroPCA in the cellWise package and the cellPCA code from its authors. None of the Python tools has been checked against them, especially when p is larger than n. So a practitioner cannot tell which tool to trust.

**Slide 3: Research question and hypothesis** (~1.5 min)
> Our research question has two parts: do the Python implementations agree with the R reference, and where, in terms of n, p and contamination, do they fail?
>
> The success criteria were fixed in the proposal, before we ran anything. First, a sanity check: the R reference must reproduce the paper, meaning its error at shift size 6 must be at least three times lower than PCA, for p = 20 and p = 200. If not, our setup is wrong. Second, a Python method "agrees" with R if its median angle to the R subspace is at most the larger of 1 degree and the 95th percentile of R-versus-R angles.
>
> On the right is our hypothesis, and I want to stress that it is a hypothesis. In one earlier run, CellPCA from robustcov gave 32.5 degrees at p = 20, worse than plain PCA at 26.0 degrees, although the paper reports good behaviour for both p. This is a lead, not a verdict.

**Slide 4: Data** (~1 min)
> For data, we start with the synthetic setting of the cellPCA paper. Note that this is our approximation, not the authors' generator. n is 100, p is 20 or 200, the covariance has two dominant eigenvalues with random eigenvectors, and 20% of cells are shifted by gamma times the column's standard deviation, with gamma from 0 to 6, and 25 runs per setting.
>
> Next come three real datasets: TopGear and the glass spectra from RobPy, whose dimensions we checked today, and the Golub leukemia data from OpenML. We have not verified that link yet.
>
> **Dinara will now show which methods we compare and what came out.**

---

## Part 2: Dinara (slides 5–7)

**Slide 5: R is the reference, not a competitor** (~1.25 min)
> Thank you, Lev. Every method has a fixed role. The R code, MacroPCA and the authors' cellPCA, is the reference for conformance, not a competitor. We call it as a black box through Rscript and CSV files, so no R code goes into our package.
>
> The systems under test are robustcov's CellPCA, RobPy's DDC-then-ROBPCA, and the PCP implementation from dfm/pcp. Baselines are ROBPCA, spherical PCA, and classical PCA as the lower bound.
>
> One important point: robustcov is not installable from PyPI as of 4 November, and we are clarifying its status. So for CellPCA we only show medians from our earlier run, clearly marked.
>
> The metric is one number: the largest principal angle between the estimated and the true two-dimensional subspace. Zero degrees means the same subspace; 90 degrees means a true direction is completely missed.

**Slide 6: Results** (~3 min)
> Here is the main result. The left panel is p = 20 and the right is p = 200. On the x-axis is the shift size gamma; on the y-axis is the median angle, and the bands are interquartile ranges over 25 runs.
>
> Look first at the black dashed line, the authors' cellPCA in R. At gamma = 6 it gives 4.0 degrees at p = 20 and 3.8 degrees at p = 200, while PCA, in dark blue, reaches 43.9 and 25.2 degrees. That is our pre-fixed check, and it passes: R reproduces the behaviour reported in the paper, so our setting is not broken. MacroPCA, the grey line, passes too.
>
> Now the dotted orange line, CellPCA from our earlier run, which we could not re-run. At p = 200 it stays low, like R. But at p = 20 it goes up with PCA, to 44.0 degrees at gamma = 6, while R cellPCA stays at 4.0. So the lead got stronger. It is still not a verdict: robustcov was not re-run, and we compared to the true subspace, not yet to the R subspace.
>
> One caveat: at gamma = 4 and p = 20 even R cellPCA varies a lot, with an interquartile range from 6.7 to 30.0 degrees. Moderate shifts are the hardest case for every method.
>
> Finally, the green line, PCP, is flat but never close to zero, about 10.1 and 6.9 degrees. It fits a different model, low-rank plus sparse, so it estimates something slightly different.

**Slide 7: How the angle is computed** (~1 min; shorten if behind schedule)
> Briefly, how the number is computed. We orthonormalise each method's loadings with a QR decomposition. The singular values of Q-transposed times the true basis are the cosines of the principal angles. The largest angle is the arccosine of the smallest one.
>
> It does not depend on sign flips, rotations inside the subspace or the scaling of loadings, so we can compare packages and even languages fairly. The same function scores both the Python and the R outputs.
>
> **Semen will now explain what these results mean and what comes next.**

---

## Part 3: Semen (slides 8–9 + opening Q&A)

**Slide 8: The R reference works; robustcov could not be re-run** (~2.5 min)
> Thank you, Dinara. What do the results say? First, the R reference works. The error ratio between PCA and R cellPCA at gamma = 6 is 10.8 at p = 20 and 6.7 at p = 200. We also reproduced the TopGear example from the cellWise vignette exactly: 126 flagged cells and the same cutoffs as in the vignette.
>
> Second, the CellPCA lead: it is clear at gamma = 6 and p = 20, 44.0 versus 4.0 degrees, but it remains a lead until robustcov is re-run.
>
> Third, a surprise: RobPy's DDC-then-ROBPCA with default settings is no better than PCA up to gamma = 4. At p = 200 it gives 17.2 degrees versus 16.3 for PCA. Before we call it a RobPy problem, we will check our own adapter settings.
>
> Fourth, PCP is flat because it is a different model.
>
> The challenges are on the right. robustcov is not installable from PyPI as of 4 November, and we are clarifying why. Our setting is an approximation of the paper. And computation cost matters: R cellPCA takes about 5.5 seconds per run at p = 200, against 0.4 seconds for MacroPCA, and Python DDC takes about 40 seconds, because RobPy has no fast DDC option. These are wall-clock times with several runs in parallel.

**Slide 9: Next steps** (~2 min)
> We have six weeks until the final on 18 December.
> - In weeks one and two, we run R on the full grid, measure R-versus-R variability, and run the conformance tests with the tolerance shown at the bottom. We will also re-run CellPCA as soon as robustcov is available again.
> - In week three, the adapters become a pip-installable suite, with at least 80% test coverage.
> - In week four, we run a reduced grid, with R only up to p = 1000, and build the failure map.
> - In week five come the real data: TopGear, glass and Golub. We will also send reproducible reports to the maintainers.
> - Week six is documentation and the final report.
>
> To sum up: the R reference is running and reproduces the paper, the CellPCA question is a sharper lead now, and the next step is a formal conformance test against R. Thank you. We are happy to take questions.

---

## Who answers which question (see `QA.md`)

| Question topic (QA.md #) | Answers |
|---|---|
| Why this is not "just a wrapper" (1); why p = 20 and 200 (6) | Lev |
| What if R shows the same (4); is robustcov wrong (5) | Lev |
| Angle metric (2); why PCP is different (3); simulation limits (7) | Dinara |
| GPL / license (8); DDC → ROBPCA weakness (9); R cost (10) | Semen |
| Anything unexpected | the speaker of that slide; others add briefly |
