from sklearn.cluster import HDBSCAN
import numpy as np
import umap

from clapclap.clustering.clustering import ClusteringMethod

from clapclap.utils.log import logger


class HDBScanMethod(ClusteringMethod):
    def __init__(self):
        super().__init__()

    def get_cluster_labels(self, embeddings):
        logger.info("Normalize embeddings")
        embeddings = embeddings / \
            np.linalg.norm(embeddings, axis=1, keepdims=True)

        logger.info("UMAP reduction")
        reducer = umap.UMAP(n_components=10, metric="cosine")
        reduced_embeddings = reducer.fit_transform(embeddings)

        logger.info("HDBScan")
        method = HDBSCAN(min_cluster_size=15, metric="euclidean")

        cluster_labels = method.fit_predict(embeddings)
        unique = np.unique(cluster_labels)

        logger.info(np.histogram(cluster_labels, bins=len(unique))[0])
        return cluster_labels
