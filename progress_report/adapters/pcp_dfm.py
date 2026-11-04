"""PCP (Candes et al.) via dfm/pcp.

pcp.py is not stored in this repository (its licence is not yet verified). On first use it is downloaded
from the pinned URL into vendor/pcp_dfm.py and accepted only if its sha256 matches the version we ran.
"""
import hashlib
import importlib.util
import urllib.request
from pathlib import Path

import numpy as np

PCP_URL = "https://raw.githubusercontent.com/dfm/pcp/main/pcp.py"
PCP_SHA256 = "c888c28761f876e088d4fe7423e4715659de2ea20c4f719b2e5858f206743f79"
PCP_PATH = Path(__file__).resolve().parents[1] / "vendor" / "pcp_dfm.py"


def _ensure_pcp_file():
    if PCP_PATH.exists() and hashlib.sha256(PCP_PATH.read_bytes()).hexdigest() == PCP_SHA256:
        return
    with urllib.request.urlopen(PCP_URL, timeout=30) as r:
        blob = r.read()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != PCP_SHA256:
        raise RuntimeError(f"dfm/pcp pcp.py changed upstream (sha256 {digest}, expected {PCP_SHA256}); "
                           "review the new version before updating PCP_SHA256.")
    PCP_PATH.parent.mkdir(exist_ok=True)
    PCP_PATH.write_bytes(blob)


_ensure_pcp_file()
_spec = importlib.util.spec_from_file_location("pcp_dfm_vendor", PCP_PATH)
_pcp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pcp)


def pcp_dfm(X, q=2):
    """Low-rank + sparse decomposition of median-centred X; loadings = top right singular vectors of L.

    Settings (maxiter=300, exact SVD, median centring) are the ones used in setting_check.py.
    """
    L, _, _ = _pcp.pcp(X - np.median(X, 0), maxiter=300, svd_method="exact")
    return np.linalg.svd(L, full_matrices=False)[2][:q].T
