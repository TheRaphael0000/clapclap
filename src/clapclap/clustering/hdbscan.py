from sklearn.cluster import HDBSCAN

from clapclap.clustering.clustering import ClusteringMethod

from clapclap.utils.logger import logger


class HDBScanMethod(ClusteringMethod):
    def __init__(self):
        super().__init__()

    def get_cluster_labels(self, embeddings):
        logger.info("HDBScan")
        method = HDBSCAN(min_cluster_size=15, metric="euclidean")
        cluster_labels = method.fit_predict(embeddings)
        return cluster_labels
