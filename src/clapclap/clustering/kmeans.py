from sklearn.cluster import KMeans
import numpy as np
import umap

from clapclap.clustering.clustering import ClusteringMethod

from clapclap.utils.log import logger


class KMeansMethod(ClusteringMethod):
    def __init__(self, no_reduction, k, max_iter, n_init):
        super().__init__()
        self.no_reduction = no_reduction
        self.k = k
        self.max_iter = max_iter
        self.n_init = n_init

    def get_cluster_labels(self, embeddings):
        logger.info("Normalize embeddings")
        embeddings = embeddings / \
            np.linalg.norm(embeddings, axis=1, keepdims=True)

        if not self.no_reduction:
            logger.info("UMAP reduction")
            reducer = umap.UMAP(n_components=10, metric="cosine")
            reduced_embeddings = reducer.fit_transform(embeddings)

        logger.info("Clustering")
        method = KMeans(n_clusters=self.k,
                        max_iter=self.max_iter, n_init=self.n_init)
        cluster_labels = method.fit_predict(embeddings)
        logger.info(np.histogram(cluster_labels, bins=self.k-1)[0])
        return cluster_labels
