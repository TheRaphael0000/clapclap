from sklearn.cluster import DBSCAN
import numpy as np

from clapclap.clustering.clustering import ClusteringMethod

from clapclap.utils.log import logger


class DBScanMethod(ClusteringMethod):
    def __init__(self, eps, min_samples):
        super().__init__()
        self.eps = eps
        self.min_samples = min_samples

    def get_cluster_labels(self, embeddings):
        logger.info("DBScan")
        method = DBSCAN(
            eps=self.eps, min_samples=self.min_samples, metric="euclidean")
        cluster_labels = method.fit_predict(embeddings)
        return cluster_labels
