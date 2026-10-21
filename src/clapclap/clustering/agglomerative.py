from sklearn.cluster import AgglomerativeClustering
import numpy as np

from clapclap.clustering.clustering import ClusteringMethod

from clapclap.utils.log import logger


class AgglomerativeClusteringMethod(ClusteringMethod):
    def __init__(self, k):
        super().__init__()
        self.k = k

    def get_cluster_labels(self, embeddings):
        kmeans = AgglomerativeClustering(
            n_clusters=self.k, metric="euclidean", linkage="average")
        cluster_labels = kmeans.fit_predict(embeddings)
        return cluster_labels
