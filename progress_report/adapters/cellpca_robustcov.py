"""robustcov CellPCA adapter. robustcov was not installable from PyPI on 4 Nov 2026 (see VERSIONS.md),
so calling this raises ImportError and the runner records the method as 'not available'."""
import numpy as np


def cellpca_robustcov(X, q=2):
    import robustcov as rc  # deferred: package currently unavailable
    C = np.asarray(rc.CellPCA(n_components=q).fit(X).components_)
    p = X.shape[1]
    return (C.T if C.shape[1] == p else C)[:, :q]  # same orientation handling as setting_check.py
