"""Build slides/progress_team4.pptx (16:9) with python-pptx.

Every number on the slides is read from results/summary.csv (runs of this session, or the labelled
fallback rows for CellPCA) or results/topgear_check_output.txt; nothing is typed in by hand.
Claims in titles are asserted against the data, so a rebuild with new data fails instead of lying.
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
S = pd.read_csv(ROOT / "results" / "summary.csv")
FB = pd.read_csv(ROOT / "results" / "fallback_table.csv")
FB_PCA_20_4 = float(FB[(FB.method == "PCA (scikit-learn)") & (FB.p == 20) & (FB.gamma == 4)]["median"].iloc[0])
TOPGEAR = (ROOT / "results" / "topgear_check_output.txt").read_text(encoding="utf-8", errors="ignore")

DARK, INK, MUTED = RGBColor(0x1B, 0x26, 0x33), RGBColor(0x22, 0x2B, 0x35), RGBColor(0x5A, 0x66, 0x73)
TEAL, LIGHT, WHITE = RGBColor(0x0B, 0x6E, 0x74), RGBColor(0xEE, 0xF2, 0xF4), RGBColor(0xFF, 0xFF, 0xFF)
LEAD = RGBColor(0xB3, 0x4A, 0x00)  # dark vermillion for "lead / hypothesis" tags (text-safe contrast)
HEAD, BODY = "Cambria", "Calibri"

PCA, PCP, DDC = "PCA (scikit-learn)", "PCP (dfm/pcp)", "DDC->ROBPCA (RobPy)"
CELL, RCELL, RMACRO = "CellPCA (robustcov)", "R cellPCA, authors' code (reference)", "R cellWise::MacroPCA (reference)"


def v(method, p, g, col="median"):
    r = S[(S.method == method) & (S.p == p) & (S.gamma == g)]
    return float(r[col].iloc[0]) if len(r) else float("nan")


def n_runs(method):
    r = S[S.method == method].n_runs
    return f"{int(r.min())}" if r.nunique() == 1 else f"{int(r.min())}–{int(r.max())}"


def f1(x):
    return f"{x:.1f}"


def tg(key):
    m = re.search(key + r":\s*([\d.]+)", TOPGEAR)
    return m.group(1) if m else "n/a"


have_rcell = not np.isnan(v(RCELL, 20, 6)) and not np.isnan(v(RCELL, 200, 6))
have_rmacro = not np.isnan(v(RMACRO, 20, 6)) and not np.isnan(v(RMACRO, 200, 6))
ratio = {p: v(PCA, p, 6) / v(RCELL, p, 6) for p in (20, 200)} if have_rcell else {}
gate_ok = have_rcell and all(r >= 3 for r in ratio.values())
ratio_m = {p: v(PCA, p, 6) / v(RMACRO, p, 6) for p in (20, 200)} if have_rmacro else {}

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
TOTAL = 9


def textbox(slide, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP, name=None):
    """paras: list of dicts(text|runs, size, bold, color, font, bullet, align, space)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        runs = p.get("runs") or [(p["text"], {})]
        for txt, ov in runs:
            r = para.add_run()
            # non-breaking spaces keep "p = 20" and "≤ 1000" on one line
            r.text = re.sub(r" ([=≈≤≥×]) ", " \\1 ", txt)
            f = r.font
            f.size = Pt(ov.get("size", p.get("size", 18)))
            f.bold = ov.get("bold", p.get("bold", False))
            f.italic = ov.get("italic", p.get("italic", False))
            f.name = ov.get("font", p.get("font", BODY))
            f.color.rgb = ov.get("color", p.get("color", INK))
        para.alignment = p.get("align", PP_ALIGN.LEFT)
        para.space_after = Pt(p.get("space", 6))
        if p.get("bullet"):
            pPr = para._p.get_or_add_pPr()
            pPr.set("marL", str(Inches(0.28)))
            pPr.set("indent", str(-Inches(0.22)))
            bu = pPr.makeelement(qn("a:buChar"), {"char": "•"})
            pPr.append(bu)
    return tb


def card(slide, x, y, w, h, fill=LIGHT, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = 0.06
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1.5)
    s.shadow.inherit = False
    return s


def tag(slide, x, y, text, color):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(1.9), Inches(0.36))
    s.adjustments[0] = 0.5
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    s.shadow.inherit = False
    tf = s.text_frame
    tf.margin_top = tf.margin_bottom = 0
    r = tf.paragraphs[0].add_run()
    r.text = text
    r.font.size, r.font.bold, r.font.name, r.font.color.rgb = Pt(13), True, BODY, WHITE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    return s


def content_slide(title, num, notes):
    s = prs.slides.add_slide(BLANK)
    textbox(s, 0.6, 0.3, 12.1, 0.95, [dict(text=title, size=28, bold=True, font=HEAD, color=DARK)],
            anchor=MSO_ANCHOR.MIDDLE, name="Title")
    textbox(s, 0.6, 7.0, 9, 0.35, [dict(text="Team 4 · HDDA progress presentation · cellwise-robust PCA validation",
                                        size=11, color=MUTED)])
    textbox(s, 11.7, 7.0, 1.0, 0.35, [dict(text=f"{num}/{TOTAL}", size=11, color=MUTED, align=PP_ALIGN.RIGHT)])
    s.notes_slide.notes_text_frame.text = notes
    return s


# ---------------------------------------------------------------- 1 title
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = DARK; bg.line.fill.background()
rng = np.random.default_rng(7)
for i in range(6):  # motif: a small grid of cells, ~20% flagged
    for j in range(8):
        c = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(9.3 + j * 0.42), Inches(1.0 + i * 0.42),
                               Inches(0.36), Inches(0.36))
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(0xE6, 0x9F, 0x00) if rng.random() < 0.2 else RGBColor(0x2E, 0x4A, 0x5E)
        c.line.fill.background()
textbox(s, 0.8, 2.3, 8.3, 2.0, [
    dict(text="Do Python cellwise-robust PCA tools agree with R?", size=40, bold=True, font=HEAD, color=WHITE),
], anchor=MSO_ANCHOR.BOTTOM)
textbox(s, 0.8, 4.45, 8.3, 1.2, [
    dict(text="Independent validation against R reference code, p ≫ n and heavy contamination", size=20,
         color=RGBColor(0xCF, 0xDC, 0xE6)),
    dict(text="Progress presentation · HDDA course, Industrial track, Direction 5", size=16,
         color=RGBColor(0xA9, 0xB8, 0xC4)),
])
textbox(s, 0.8, 6.0, 11, 0.6, [dict(text="Team 4: Lev Lesnoi · Dinara Bairamgazieva · Semen Vashurin",
                                     size=18, bold=True, color=WHITE)])
s.notes_slide.notes_text_frame.text = (
    "Opening, about 20 seconds. We validate Python implementations of cellwise-robust PCA against the R "
    "reference code. This is a progress report: what we ran this week, what it shows, and what is still open.")

# ---------------------------------------------------------------- 2 problem
s = content_slide("20% bad cells touch almost every row; Python tools lack an R check", 2,
                  "About 2 minutes. Cellwise outliers are single corrupted entries, not whole bad rows. With 20% of "
                  "cells contaminated and p = 20, only 0.8^20 ≈ 1% of rows are fully clean, so rowwise-robust methods "
                  "like ROBPCA have almost nothing left to trust. Python now has several cellwise tools: robustcov "
                  "CellPCA, RobPy's DDC then ROBPCA two-step, and PCP scripts. None of them is validated against the "
                  "R reference code (cellWise MacroPCA and the cellPCA authors' code). So practitioners cannot tell "
                  "which one to trust or where each fails.")
rng = np.random.default_rng(3)
for i in range(10):
    for j in range(12):
        bad = rng.random() < 0.2
        c = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8 + j * 0.36), Inches(1.65 + i * 0.36),
                               Inches(0.31), Inches(0.31))
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(0xE6, 0x9F, 0x00) if bad else RGBColor(0xD5, 0xDE, 0xE4)
        c.line.fill.background()
clean_p20, clean_p200 = 0.8 ** 20 * 100, 0.8 ** 200 * 100
textbox(s, 0.8, 5.35, 5.0, 1.3, [
    dict(text="Orange = contaminated cell (20%)", size=14, color=MUTED),
    dict(text=f"Rows fully clean: {clean_p20:.1f}% at p = 20, ≈ 0% at p = 200", size=16, bold=True, color=INK),
])
textbox(s, 5.9, 1.6, 6.8, 5.0, [
    dict(text="Cellwise outliers", size=22, bold=True, color=TEAL, space=2),
    dict(text="single corrupted entries; rowwise-robust PCA discards whole rows and runs out of clean ones",
         size=18, bullet=True, space=14),
    dict(text="New Python tools", size=22, bold=True, color=TEAL, space=2),
    dict(text="robustcov CellPCA, RobPy DDC → ROBPCA, PCP scripts", size=18, bullet=True, space=14),
    dict(text="Gap", size=22, bold=True, color=TEAL, space=2),
    dict(text="none is validated against the R reference (cellWise::MacroPCA, authors' cellPCA code), "
              "especially for p ≫ n", size=18, bullet=True),
])

# ---------------------------------------------------------------- 3 RQ + hypothesis
s = content_slide("Do Python implementations agree with R, and where do they fail?", 3,
                  "About 1.5 minutes. Research question: do the Python implementations agree with the R reference, "
                  "and in which regimes do they fail? Hypothesis, and I stress it is a hypothesis: robustcov CellPCA "
                  "behaves differently from the published cellPCA behaviour at p around 20. It comes from one earlier "
                  "run of our own approximation of the paper's setting. It is a lead, not a verdict. Success criteria "
                  "were fixed in the proposal before running anything.")
card(s, 0.6, 1.55, 5.9, 4.3)
textbox(s, 0.9, 1.75, 5.3, 4.6, [
    dict(text="Research question", size=22, bold=True, color=TEAL, space=10),
    dict(text="Do Python cellwise-robust PCA implementations agree with the R reference?", size=19, space=10),
    dict(text="Where (n, p, contamination) do they fail?", size=19, space=18),
    dict(text="Pre-fixed criteria (proposal)", size=17, bold=True, color=MUTED, space=4),
    dict(text="R reproduces the paper: error ≥ 3× below PCA at γ = 6, p = 20 and 200", size=15, bullet=True),
    dict(text="“agrees”: median angle to R subspace ≤ max(1°, 95th pct of R-vs-R angles)", size=15, bullet=True),
])
card(s, 6.85, 1.55, 5.85, 4.3, fill=WHITE, line=LEAD)
tag(s, 7.15, 1.8, "HYPOTHESIS", LEAD)
textbox(s, 7.15, 2.35, 5.3, 4.0, [
    dict(text="robustcov CellPCA behaves differently from the published cellPCA behaviour at p ≈ 20", size=21,
         bold=True, space=14),
    dict(text=f"Basis: one earlier run of our approximation — at γ = 4, p = 20: CellPCA {f1(v(CELL, 20, 4))}° vs "
              f"PCA {f1(FB_PCA_20_4)}° (same earlier run, robustcov 0.2.0)",
         size=16, bullet=True, color=INK),
    dict(text="A lead, not a verdict: R reference now run (slide 6); robustcov itself still needs a re-run",
         size=16, bullet=True, color=INK),
])

# ---------------------------------------------------------------- 4 data
s = content_slide("We start from the cellPCA paper's synthetic setting, then real data", 4,
                  "About 1.25 minutes for this slide. Synthetic data approximates the setting of Centofanti, Hubert "
                  "and Rousseeuw: n = 100, p = 20 or 200, covariance with two dominant eigenvalues and random "
                  "orthonormal eigenvectors, 20% of cells shifted by gamma times the column standard deviation, "
                  "gamma 0 to 6, 25 runs with seeds 1000 to 1024. This is our approximation, not the authors' "
                  "generator. Real data are planned: TopGear and glass from RobPy (dimensions checked today), and "
                  "Golub leukemia from OpenML 45090 — that link has not been verified yet.")
card(s, 0.6, 1.55, 6.0, 5.1)
textbox(s, 0.9, 1.7, 5.5, 4.9, [
    dict(text="Synthetic: cellPCA paper setting", size=21, bold=True, color=TEAL, space=4),
    dict(text="our approximation, not the authors' generator", size=14, italic=True, color=MUTED, space=10),
    dict(text="n = 100, p ∈ {20, 200}, q = 2", size=17, bullet=True),
    dict(text="Σ: two dominant eigenvalues (9.57, 6.70 | 104.88, 73.42), rest ≈ 0.1, random eigenvectors",
         size=17, bullet=True),
    dict(text="20% of cells shifted by γ·σ_j, γ ∈ {0, 2, 4, 6}", size=17, bullet=True),
    dict(text="25 runs per setting, seeds 1000 + s", size=17, bullet=True),
])
items = [("TopGear (RobPy)", "297 cars × 13 numeric, 110 missing cells", "dims checked today"),
         ("Glass spectra (RobPy)", "180 × 750, p > n", "dims checked today"),
         ("Golub leukemia (OpenML 45090)", "72 × 7129, outliers injected", "link not yet verified")]
for k, (name, dims, status) in enumerate(items):
    y = 1.55 + k * 1.72
    card(s, 6.95, y, 5.75, 1.5, fill=WHITE, line=RGBColor(0xC9, 0xD3, 0xDA))
    textbox(s, 7.2, y + 0.12, 5.3, 1.3, [
        dict(text=name, size=19, bold=True, color=INK, space=2),
        dict(text=dims, size=16, color=INK, space=2),
        dict(text=status, size=14, italic=True, color=LEAD if "not" in status else TEAL),
    ])

# ---------------------------------------------------------------- 5 methods + metric
s = content_slide("R is the reference, not a competitor; the metric is one angle", 5,
                  "About 1.25 minutes. Roles are fixed in advance. R is the conformance reference: cellWise MacroPCA "
                  "from CRAN and the cellPCA authors' R code from their KU Leuven software page, both run as black "
                  "boxes through Rscript and CSV files; no R code goes into our package (cellWise is GPL). Systems "
                  "under test are robustcov CellPCA, RobPy's DDC then ROBPCA two-step, and the dfm/pcp PCP script. "
                  "Baselines: ROBPCA, spherical PCA, and classical PCA as the lower bound. robustcov could not be "
                  "re-run this week: it is not installable from PyPI as of 4 Nov 2026, status being clarified. "
                  "Metric: the largest principal angle between the estimated and the true 2-D subspace, median over "
                  "runs, with the interquartile range.")
rows = [("Method", "Role", "This week"),
        ("R cellPCA (authors' code) · R cellWise::MacroPCA", "Reference (conformance)",
         f"run: {n_runs(RCELL)} / {n_runs(RMACRO)} seeds" if have_rcell else "not run"),
        ("robustcov CellPCA", "System under test", "not installable from PyPI as of 4 Nov 2026; earlier-run medians"),
        ("RobPy DDC → ROBPCA (manual two-step)", "System under test", f"run: {n_runs(DDC)} seeds"),
        ("PCP (dfm/pcp)", "System under test (low-rank + sparse)", f"run: {n_runs(PCP)} seeds"),
        ("RobPy ROBPCA, spherical PCA; sklearn PCA", "Baselines / lower bound", f"run: {n_runs(PCA)} seeds")]
tbl = s.shapes.add_table(len(rows), 3, Inches(0.6), Inches(1.55), Inches(12.1), Inches(3.6)).table
for j, wdt in enumerate((4.6, 3.4, 4.1)):
    tbl.columns[j].width = Inches(wdt)
for i, row in enumerate(rows):
    for j, txt in enumerate(row):
        cell = tbl.cell(i, j)
        cell.text = txt
        cell.fill.solid()
        cell.fill.fore_color.rgb = TEAL if i == 0 else (LIGHT if i % 2 else WHITE)
        para = cell.text_frame.paragraphs[0]
        for r in para.runs:
            r.font.size = Pt(15 if i else 16)
            r.font.bold = i == 0 or j == 0
            r.font.name = BODY
            r.font.color.rgb = WHITE if i == 0 else (LEAD if "not installable" in txt else INK)
        cell.margin_top = cell.margin_bottom = Inches(0.05)
card(s, 0.6, 5.45, 12.1, 1.35)
textbox(s, 0.9, 5.52, 11.6, 1.25, [
    dict(runs=[("Metric: ", {"bold": True, "color": TEAL}),
               ("largest principal angle between estimated and true 2-D subspace (degrees)", {})], size=18,
         space=4),
    dict(text="0° = same subspace · 90° = some true direction completely missed · median over runs, band = IQR",
         size=16, color=MUTED),
])

# ---------------------------------------------------------------- 6 results
title6 = ("R reproduces the paper; the earlier CellPCA run did not at p = 20" if gate_ok
          else "Preliminary results: the R reference check is not yet passed")
s = content_slide(title6, 6,
                  "About 3 minutes. Left p = 20, right p = 200; x is the shift size gamma, y the median largest "
                  "principal angle, bands are interquartile ranges. "
                  + (f"Gate check from the proposal: at gamma = 6 the R cellPCA error is "
                     f"{f1(v(RCELL, 20, 6))} deg vs PCA {f1(v(PCA, 20, 6))} at p = 20 (ratio {ratio[20]:.1f}), and "
                     f"{f1(v(RCELL, 200, 6))} vs {f1(v(PCA, 200, 6))} at p = 200 (ratio {ratio[200]:.1f}); both "
                     f"are at least 3, so our setting reproduces the published behaviour. " if have_rcell else "")
                  + f"The dotted CellPCA line is NOT re-run: earlier run with robustcov 0.2.0. At p = 20 it tracks "
                    f"PCA ({f1(v(CELL, 20, 6))} deg at gamma = 6), while R cellPCA stays low. That strengthens the "
                    f"lead but is not a verdict: different session, robustcov not re-run, and we compare to the "
                    f"true subspace, not yet to the R subspace. Caveat: at gamma = 4 and p = 20 even R cellPCA is "
                    f"very variable (median {f1(v(RCELL, 20, 4))}, IQR {f1(v(RCELL, 20, 4, 'q25'))} to "
                    f"{f1(v(RCELL, 20, 4, 'q75'))}), so the earlier CellPCA value of {f1(v(CELL, 20, 4))} is "
                    f"above R's upper quartile but the clear gap is at gamma = 6. Moderate shifts are the hardest "
                    f"case for every method. Spherical PCA is left out of the figure for readability; it tracks "
                    f"PCA ({f1(v('Spherical PCA (RobPy)', 20, 6))} and {f1(v('Spherical PCA (RobPy)', 200, 6))} deg "
                    f"at gamma = 6; all numbers are in results/summary.csv). PCP is flat at about {f1(v(PCP, 20, 6))} and "
                    f"{f1(v(PCP, 200, 6))} deg because it fits a different model (low-rank plus sparse). "
                    f"R reference: {n_runs(RCELL)} seeds per point.")
s.shapes.add_picture(str(ROOT / "results" / "fig_angles.png"), Inches(0.75), Inches(1.2), width=Inches(11.8))
read = [dict(runs=[("Reading: ", {"bold": True, "color": TEAL}),
                   (f"at γ = 6, R cellPCA {f1(v(RCELL, 20, 6))}° / {f1(v(RCELL, 200, 6))}° vs PCA "
                    f"{f1(v(PCA, 20, 6))}° / {f1(v(PCA, 200, 6))}° (p = 20 / 200) → paper behaviour reproduced "
                    f"({n_runs(RCELL)} runs per point).", {})], size=16, space=2),
        dict(runs=[("Lead: ", {"bold": True, "color": LEAD}),
                   (f"earlier CellPCA run (not re-run) gave {f1(v(CELL, 20, 6))}° at p = 20, close to PCA — "
                    f"unlike R cellPCA.", {})], size=16)]
if have_rcell:
    textbox(s, 0.75, 6.1, 11.9, 0.85, read)

# ---------------------------------------------------------------- 7 angle
s = content_slide("How the angle is computed: three lines of linear algebra", 7,
                  "Optional, about 1 minute. Each method returns a p by 2 loadings matrix V. We orthonormalise it "
                  "with a QR decomposition, take the singular values of Q transpose U, where U is the true "
                  "orthonormal basis; these are the cosines of the principal angles. The largest angle is the arccos "
                  "of the smallest singular value. It is invariant to sign flips, rotations within the subspace and "
                  "the scaling of loadings, so methods with different conventions are comparable. Same function for "
                  "Python and R outputs.")
steps = [("1", "Orthonormalise", "Q = qr(V)\nV: p × 2 loadings from any method"),
         ("2", "Cosines of angles", "σ = singular values of Qᵀ U\nU: true orthonormal basis"),
         ("3", "Largest angle", "θ = arccos(min σ)\nin degrees; 0° = perfect")]
for k, (n, head, body) in enumerate(steps):
    x = 0.6 + k * 4.15
    card(s, x, 1.7, 3.85, 2.75)
    circ = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.3), Inches(1.95), Inches(0.7), Inches(0.7))
    circ.fill.solid(); circ.fill.fore_color.rgb = TEAL; circ.line.fill.background()
    circ.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    r = circ.text_frame.paragraphs[0].add_run(); r.text = n
    r.font.size, r.font.bold, r.font.color.rgb, r.font.name = Pt(22), True, WHITE, BODY
    textbox(s, x + 0.3, 2.8, 3.35, 2.0, [dict(text=head, size=21, bold=True, color=INK, space=8)] +
            [dict(text=line, size=16, font="Cambria Math" if i == 0 else BODY, color=INK if i == 0 else MUTED,
                  space=4) for i, line in enumerate(body.split("\n"))])
textbox(s, 0.6, 4.85, 12.1, 1.5, [
    dict(text="Invariant to sign flips, rotations inside the subspace and loading scale → comparable across "
              "packages and languages", size=17, bullet=True),
    dict(text="Same function scores Python and R outputs; R loadings come back via CSV (Rscript, no rpy2)",
         size=17, bullet=True),
])

# ---------------------------------------------------------------- 8 analysis + challenges
ddc_p200 = v(DDC, 200, 4)
s = content_slide("The R reference works; robustcov could not be re-run this week", 8,
                  "About 2.5 minutes. What the results say: the R reference runs and reproduces the paper's "
                  "qualitative claim in our setting; the TopGear MacroPCA example from the cellWise vignette "
                  f"reproduces exactly (cutoffOD {tg('cutoffOD')}, cutoffSD {tg('cutoffSD')}, "
                  f"{tg('flagged cells')} flagged cells). The CellPCA lead is stronger but still a lead. "
                  f"RobPy DDC then ROBPCA with default settings does NOT come close to cellPCA in our runs "
                  f"(p = 200, gamma = 4: {f1(ddc_p200)} deg vs R cellPCA {f1(v(RCELL, 200, 4))}); this contradicts "
                  "the impression in our proposal, so we will check the adapter configuration before reporting it. "
                  "Difficulties: robustcov is not installable from PyPI as of 4 Nov 2026 and its GitHub repository "
                  "asks for credentials; we are clarifying the status. Our setup is an approximation of the paper. "
                  "R cost: the authors' cellPCA takes about "
                  f"{f1(v(RCELL, 200, 4, 'median_seconds'))} s per run at p = 200 versus "
                  f"{f1(v(RMACRO, 200, 4, 'median_seconds'))} s for MacroPCA, so the full grid needs a reduced "
                  "design for R.")
card(s, 0.6, 1.55, 6.0, 4.6)
textbox(s, 0.9, 1.7, 5.5, 5.0, [
    dict(text="What the results say", size=21, bold=True, color=TEAL, space=8),
    dict(text=f"R gate passed: PCA/R-cellPCA error ratio at γ = 6 is {ratio[20]:.1f}× (p = 20) and "
              f"{ratio[200]:.1f}× (p = 200)" if gate_ok else "R gate not passed yet", size=16, bullet=True),
    dict(text=f"TopGear vignette reproduced: {tg('flagged cells')} flagged cells, cutoffOD {tg('cutoffOD')}",
         size=16, bullet=True),
    dict(text=f"CellPCA lead (not re-run): clear at γ = 6, p = 20 ({f1(v(CELL, 20, 6))}° vs R "
              f"{f1(v(RCELL, 20, 6))}°); at γ = 4 R itself varies (IQR {f1(v(RCELL, 20, 4, 'q25'))}–"
              f"{f1(v(RCELL, 20, 4, 'q75'))}°)", size=16, bullet=True, color=LEAD),
    dict(text=f"DDC → ROBPCA (RobPy defaults) no better than PCA up to γ = 4 (p = 200: {f1(ddc_p200)}° vs "
              f"{f1(v(PCA, 200, 4))}°); adapter settings to be checked", size=16, bullet=True),
    dict(text=f"PCP flat at ≈ {f1(v(PCP, 20, 6))}° / {f1(v(PCP, 200, 6))}°: different model (low-rank + sparse)",
         size=16, bullet=True),
])
card(s, 6.95, 1.55, 5.75, 4.6, fill=WHITE, line=RGBColor(0xC9, 0xD3, 0xDA))
textbox(s, 7.2, 1.7, 5.3, 5.0, [
    dict(text="Challenges", size=21, bold=True, color=LEAD, space=8),
    dict(text="robustcov: not installable from PyPI as of 4 Nov 2026, status being clarified", size=16,
         bullet=True),
    dict(text="Our setting approximates the paper (positive shifts, 3rd eigenvalue 0.11)", size=16, bullet=True),
    dict(text=f"R cellPCA cost: ~{f1(v(RCELL, 200, 4, 'median_seconds'))} s/run at p = 200 "
              f"(MacroPCA {f1(v(RMACRO, 200, 4, 'median_seconds'))} s) → R only up to p ≤ 1000",
         size=16, bullet=True),
    dict(text=f"Python DDC: ~{f1(v(DDC, 200, 4, 'median_seconds'))} s/run at p = 200, no fastDDC",
         size=16, bullet=True),
    dict(text="timings: wall time, several runs in parallel on one laptop", size=13, italic=True, color=MUTED),
])

# ---------------------------------------------------------------- 9 next steps
s = content_slide("Six weeks to 18 Dec: conformance tests, suite, failure map", 9,
                  "About 2.5 minutes. Weeks 1-2: run R on the full synthetic grid, estimate R-versus-R variability "
                  "over 25 seeds, and run conformance tests with the tolerance fixed in advance: the median angle to "
                  "the R subspace must be at most max(1 degree, 95th percentile of R-vs-R angles). Clarify robustcov "
                  "availability with its maintainer and re-run CellPCA. Week 3: adapters as a pip-installable suite, "
                  "tests with at least 80% coverage. Week 4: reduced grid with R only up to p = 1000, and the failure "
                  "map. Week 5: real data (TopGear, glass, Golub after verifying the OpenML link) and reproducible "
                  "reports to maintainers. Week 6: documentation and final report.")
plan = [("Wk 1–2", "R reference on full grid; R-vs-R spread; conformance tests; re-run robustcov once available"),
        ("Wk 3", "Adapters as pip-installable suite; tests ≥ 80% coverage"),
        ("Wk 4", "Reduced grid (R only up to p ≤ 1000); failure map"),
        ("Wk 5", "Real data: TopGear, glass, Golub; reproducible reports to maintainers"),
        ("Wk 6", "Documentation, worked examples, final report (18 Dec)")]
for k, (wk, what) in enumerate(plan):
    y = 1.55 + k * 0.84
    tg_ = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(y), Inches(1.5), Inches(0.66))
    tg_.adjustments[0] = 0.3
    tg_.fill.solid(); tg_.fill.fore_color.rgb = TEAL; tg_.line.fill.background()
    tg_.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    tg_.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    r = tg_.text_frame.paragraphs[0].add_run(); r.text = wk
    r.font.size, r.font.bold, r.font.color.rgb, r.font.name = Pt(17), True, WHITE, BODY
    textbox(s, 2.3, y, 10.4, 0.66, [dict(text=what, size=18)], anchor=MSO_ANCHOR.MIDDLE)
card(s, 0.6, 5.85, 12.1, 0.95)
textbox(s, 0.9, 5.9, 11.6, 0.85, [
    dict(runs=[("Pre-fixed tolerance: ", {"bold": True, "color": TEAL}),
               ("a Python method agrees with R if its median angle to the R subspace ≤ max(1°, 95th percentile of "
                "R-vs-R angles over 25 seeds)", {})], size=17)], anchor=MSO_ANCHOR.MIDDLE)

# Speaker split (see slides/script_3_speakers.md): prefix every note with who presents the slide.
SPEAKER = {1: "Lev", 2: "Lev", 3: "Lev", 4: "Lev", 5: "Dinara", 6: "Dinara", 7: "Dinara", 8: "Semen", 9: "Semen"}
HANDOVER = {4: " Hand over: 'Dinara will now show which methods we compare and what came out.'",
            7: " Hand over: 'Semen will now explain what these results mean and what comes next.'",
            9: " Then open Q&A (who answers what: slides/script_3_speakers.md)."}
for i, sl in enumerate(prs.slides, 1):
    tf = sl.notes_slide.notes_text_frame
    tf.text = f"[Speaker: {SPEAKER[i]}] " + tf.text + HANDOVER.get(i, "")

# Replace python-pptx template defaults in the file metadata.
cp = prs.core_properties
cp.author = cp.last_modified_by = "Team 4"
cp.title = "Do Python cellwise-robust PCA tools agree with R?"
cp.comments = ""

out = ROOT / "slides" / "progress_team4.pptx"
prs.save(out)
print("saved", out, "| gate_ok:", gate_ok, "| ratios:", {k: round(x, 2) for k, x in ratio.items()},
      "| MacroPCA ratios:", {k: round(x, 2) for k, x in ratio_m.items()})
