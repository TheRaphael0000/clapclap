import logging

from sklearn.cluster import KMeans
import numpy as np

from clapclap.clustering.clustering import ClusteringMethod

logger = logging.getLogger("KMEANS")

class KMeansClustering(ClusteringMethod):
    def __init__(self, k):
        super().__init__()
        self.k = k


    def get_cluster_labels(self, embeddings):
        kmeans = KMeans(n_clusters=self.k)
        cluster_labels = kmeans.fit_predict(embeddings)
        logger.info(np.histogram(cluster_labels, bins=self.k-1)[0])
        return cluster_labels