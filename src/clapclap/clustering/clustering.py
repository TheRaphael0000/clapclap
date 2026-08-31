import logging
import numpy as np
from sqlalchemy import select

from clapclap.clustering.smartnaming import SmartNaming
from clapclap.db import DB, Embedding
from clapclap.navidrome.navidrome import Navidrome
from clapclap.utils.types import GenresList

logger = logging.getLogger("CLUSTERING")

class ClusteringMethod:
    def __init__(self):
        pass

    def get_cluster_labels(self, embeddings):
        raise NotImplementedError()


class Clustering:
    method: ClusteringMethod

    def __init__(self, limit: int, save: bool, smart_naming: bool, smart_naming_size: int, smart_naming_sep: str, smart_naming_macro_genre: bool, prefix:str, method: ClusteringMethod, genres_list: GenresList):
        self.db = DB()
        self.limit = limit
        self.save = save
        self.method = method
        self.smart_naming = smart_naming
        self.prefix = prefix
        self.genres_list = genres_list
        
        if self.smart_naming:
            self.smart_naming = SmartNaming(smart_naming_size, smart_naming_sep, smart_naming_macro_genre, genres_list)


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

        logger.info("Creating playlists")
        navidrome = Navidrome()
        for i, label in enumerate(np.unique(cluster_labels)):
            cluster_songIds = self.songIds[cluster_labels == label]

            if self.smart_naming:
                cluster_centroid = np.mean(self.embeddings[cluster_labels == label], axis=0)
                name = self.smart_naming.get_name(centroid=cluster_centroid)
            else:
                name = f"C{i}"

            logger.info(f"{name}: {cluster_songIds.shape[0]} songs")
            navidrome.create_playlist(name=f"{self.prefix}{name}", songIds=cluster_songIds.tolist())



