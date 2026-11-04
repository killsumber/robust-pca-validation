"""One adapter per method: fn(X, q) -> p x q loadings matrix (columns span the estimated subspace)."""
from .pca import pca
from .pcp_dfm import pcp_dfm
from .robpca import robpca
from .spherical_pca import spherical_pca
from .ddc_robpca import ddc_robpca
from .cellpca_robustcov import cellpca_robustcov

REGISTRY = {
    "PCA (scikit-learn)": pca,
    "PCP (dfm/pcp)": pcp_dfm,
    "ROBPCA (RobPy)": robpca,
    "Spherical PCA (RobPy)": spherical_pca,
    "DDC->ROBPCA (RobPy)": ddc_robpca,
    "CellPCA (robustcov)": cellpca_robustcov,
}
SHORT = {"pca": "PCA (scikit-learn)", "pcp": "PCP (dfm/pcp)", "robpca": "ROBPCA (RobPy)",
         "spca": "Spherical PCA (RobPy)", "ddc": "DDC->ROBPCA (RobPy)", "cellpca": "CellPCA (robustcov)"}
