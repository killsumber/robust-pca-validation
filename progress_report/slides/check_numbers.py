"""Cross-check: every number with a decimal point (or °) on the slides must appear in summary.csv,
fallback_table.csv, topgear_check_output.txt, or the small whitelist of setting constants."""
import re
import sys
from pathlib import Path

import pandas as pd
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
allowed = set()
for f in ("summary.csv", "fallback_table.csv"):
    d = pd.read_csv(ROOT / "results" / f)
    for c in d.select_dtypes("number").columns:
        allowed |= {f"{x:.1f}" for x in d[c].dropna()}
allowed |= set(re.findall(r"\d+\.\d+", (ROOT / "results" / "topgear_check_output.txt").read_text(errors="ignore")))
s = pd.read_csv(ROOT / "results" / "summary.csv")
pca = s[s.method == "PCA (scikit-learn)"].set_index(["p", "gamma"])["median"]
rc = s[s.method == "R cellPCA, authors' code (reference)"].set_index(["p", "gamma"])["median"]
allowed |= {f"{pca[(p, 6.0)] / rc[(p, 6.0)]:.1f}" for p in (20, 200)}  # gate ratios
allowed |= {"9.57", "6.70", "104.88", "73.42", "0.1", "0.11", "0.2.0", "1.2"}  # setting constants, version, 0.8^20
bad = []
for i, sl in enumerate(Presentation(ROOT / "slides" / "progress_team4.pptx").slides, 1):
    text = " ".join(sh.text_frame.text for sh in sl.shapes if sh.has_text_frame)
    text += " ".join(c.text for sh in sl.shapes if sh.has_table for r in sh.table.rows for c in r.cells)
    for num in re.findall(r"\d+\.\d+", text):
        if num not in allowed:
            bad.append((i, num))
print("unverified numbers:", bad or "none")
sys.exit(1 if bad else 0)
