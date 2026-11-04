import pandas as pd
from robpy.outliers import DDC
from robpy.pca import ROBPCA


def ddc_robpca(X, q=2):
    """Manual two-step: DDC flags deviating cells and imputes them, then ROBPCA on the imputed data."""
    df = pd.DataFrame(X)
    imputed = DDC().fit(df).impute(df, impute_outliers=True)
    return ROBPCA(n_components=q, random_seed=0).fit(pd.DataFrame(imputed).to_numpy()).components_[:, :q]
