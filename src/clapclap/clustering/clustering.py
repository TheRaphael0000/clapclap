import collections
import numpy as np
from sqlalchemy import select

from clapclap.clustering.smartnaming import SmartNaming
from clapclap.db import DB, Embedding
from clapclap.navidrome.navidrome import Navidrome
from clapclap.utils.types import GenresList
from clapclap.utils.log import logger


class ClusteringMethod:
    def __init__(self):
        pass

    def get_cluster_labels(self, embeddings):
        raise NotImplementedError()


class Clustering:
    method: ClusteringMethod

    def __init__(
            self, limit: int,
            save: bool,
            smart_naming: bool,
            smart_naming_size: int,
            smart_naming_sep: str,
            smart_naming_macro_genre: bool,
            prefix: str,
            method: ClusteringMethod,
            genres_list: GenresList,
            no_merge: bool
    ):
        self.db = DB()
        self.limit = limit
        self.save = save
        self.method = method
        self.smart_naming = smart_naming
        self.prefix = prefix
        self.genres_list = genres_list
        self.no_merge = no_merge

        if self.smart_naming:
            self.smart_naming = SmartNaming(
                smart_naming_size,
                smart_naming_sep,
                smart_naming_macro_genre,
                genres_list
            )

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

        logger.info("Computing smart-names")
        playlists = []
        for i, label in enumerate(np.unique(cluster_labels)):
            cluster_songIds = self.songIds[cluster_labels == label]

            if self.smart_naming:
                cluster_centroid = np.mean(
                    self.embeddings[cluster_labels == label], axis=0)
                name = self.smart_naming.get_name(centroid=cluster_centroid)
            else:
                name = f"C{i}"

            playlist_name = f"{self.prefix}{name}"
            playlist_songs = cluster_songIds.tolist()
            playlists.append((playlist_name, playlist_songs))

        if not self.no_merge:
            logger.info("Merging playlists with same name")
            playlists_ = collections.defaultdict(list)
            for playlist_name, playlist_songs in playlists:
                playlists_[playlist_name].extend(playlist_songs)
            playlists = list(playlists_.items())

        logger.info(f"Creating playlists")
        navidrome = Navidrome()
        for playlist_name, playlist_songs in playlists:
            navidrome.create_playlist(
                name=playlist_name, songIds=playlist_songs)
            logger.info(
                f"'{playlist_name}' created ({len(playlist_songs)} songs)")
        logger.info(f"{len(playlists)} playlists created ")
