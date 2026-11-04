from robpy.pca import PCALocantore


def spherical_pca(X, q=2):
    """RobPy spherical PCA (Locantore et al.), rowwise-robust baseline."""
    return PCALocantore(n_components=q).fit(X).components_[:, :q]
