from sklearn.cluster import KMeans
import numpy as np

from clapclap.clustering.clustering import ClusteringMethod

from clapclap.utils.log import logger


class KMeansMethod(ClusteringMethod):
    def __init__(self, k: int, max_iter: int, n_init):
        super().__init__()
        self.k = k
        self.max_iter = max_iter
        self.n_init = n_init

    def get_cluster_labels(self, embeddings):
        logger.info("K-Means")
        method = KMeans(
            n_clusters=self.k,
            max_iter=self.max_iter,
            n_init=self.n_init,
            random_state=67
        )
        cluster_labels = method.fit_predict(embeddings)
        return cluster_labels
