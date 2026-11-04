from robpy.pca import ROBPCA


def robpca(X, q=2):
    """RobPy ROBPCA (rowwise-robust baseline). RobPy stores components_ as p x k."""
    return ROBPCA(n_components=q, random_seed=0).fit(X).components_[:, :q]
