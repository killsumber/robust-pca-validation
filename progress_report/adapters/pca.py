from sklearn.decomposition import PCA


def pca(X, q=2):
    """Classical PCA (lower bound)."""
    return PCA(q).fit(X).components_.T
