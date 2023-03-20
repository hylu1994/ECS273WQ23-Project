from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn import preprocessing
import numpy as np

# def perform_PCA(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
def perform_PCA(X, comp):
    pca = PCA(n_components=comp)
    pca.fit(X)  # Learn the projection matrix
    Z = pca.transform(X) # Project the given data with the learnt projection matrix
    return Z

# def perform_TSNE(X: np.ndarray, perplexity: int = 5) -> np.ndarray:
def perform_TSNE(X, perplexity=5):
    scaler = preprocessing.StandardScaler()
    X = scaler.fit_transform(X)

    tsne = TSNE(n_components=2, perplexity=perplexity)
    Z = tsne.fit_transform(X)
    return Z