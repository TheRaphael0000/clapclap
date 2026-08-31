import logging
import numpy as np
from sqlalchemy import select

from scipy.spatial.distance import cdist

from clapclap.db import DB, Embedding
from clapclap.navidrome.navidrome import Navidrome

logger = logging.getLogger("CLUSTERING")

class ClusteringMethod:
    def __init__(self):
        pass

    def get_cluster_labels(self, embeddings):
        raise NotImplementedError()


class Clustering:
    method: ClusteringMethod

    def __init__(self, limit: int, save: bool, smart_naming: bool, smart_naming_size: int, smart_naming_sep: str, prefix:str, method: ClusteringMethod):
        self.db = DB()
        self.limit = limit
        self.save = save
        self.method = method
        self.smart_naming = smart_naming
        self.smart_naming_size = smart_naming_size
        self.smart_naming_sep = smart_naming_sep
        self.prefix = prefix

    def process(self):
        logger.info("Loading embeddings")
        with self.db as session:
            stmt = select(Embedding.embedding, Embedding.songId)
            results = session.execute(stmt).all()
            self.embeddings, self.songIds = zip(*results)
            self.embeddings = np.array(self.embeddings)
            self.songIds = np.array(self.songIds)

        logger.info("Computing clusters")
        cluster_labels = self.method.get_cluster_labels(self.embeddings)

        if self.smart_naming:
            genres, genres_centroids = self.compute_genres_centroids()

        logger.info("Creating playlists")
        navidrome = Navidrome()
        for i, label in enumerate(np.unique(cluster_labels)):
            cluster_songIds = self.songIds[cluster_labels == label]

            if self.smart_naming:
                cluster_centroid = np.mean(self.embeddings[cluster_labels == label], axis=0)
                distances = cdist([cluster_centroid], genres_centroids, metric='cosine')[0]
                arg_sorted_distances = np.argsort(distances)
                selected_indices = arg_sorted_distances[0:self.smart_naming_size]
                selected_genres = genres[selected_indices]
                name = self.smart_naming_sep.join(selected_genres)
            else:
                name = f"C{i}"

            logger.info(f"{name}: {cluster_songIds.shape[0]} songs")
            navidrome.create_playlist(name=f"{self.prefix}{name}", songIds=cluster_songIds.tolist())



    def compute_genres_centroids(self):
        logger.info("Computing labels centroids")
        from clapclap.update.text_feature_extractor import TextFeatureExtractor, GenreDataset
        te = TextFeatureExtractor()
        from torch.utils.data import DataLoader

        ds = GenreDataset()
        dl = DataLoader(ds, batch_size=128)

        genres_embeddings = []
        genres = []
        for i, b in enumerate(dl):
            logger.debug(f"Batch {i}")
            genres.extend(b)
            # add quotes to ensure multi-word genre embeddings are correctly computed 
            b = [f'"{bi}"' for bi in b]
            genres_embeddings.extend(te.clap(b))

        return np.array(genres), np.array(genres_embeddings)
