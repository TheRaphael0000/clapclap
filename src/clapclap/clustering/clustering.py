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
            self,
            min_duration: int,
            reduction: bool,
            reduction_components: int,
            method: ClusteringMethod,
            prefix: str,
            no_smart_naming: bool,
            smart_naming_size: int,
            smart_naming_sep: str,
            smart_naming_no_macro_genre: bool,
            genres_list: GenresList,
            no_merge: bool,
            oddities: int,
            no_save: bool,
    ):
        self.db = DB()
        self.min_duration = min_duration
        self.reduction = reduction
        self.reduction_components = reduction_components
        self.method = method
        self.prefix = prefix
        self.no_smart_naming = no_smart_naming
        self.smart_naming_size = smart_naming_size
        self.smart_naming_sep = smart_naming_sep
        self.smart_naming_no_macro_genre = smart_naming_no_macro_genre
        self.genres_list = genres_list
        self.no_merge = no_merge
        self.oddities = oddities
        self.no_save = no_save

    def process(self):
        logger.info("Loading embeddings")
        with self.db as session:
            stmt = select(Embedding.embedding, Embedding.songId).where(
                Embedding.duration >= self.min_duration)
            results = session.execute(stmt).all()
            self.embeddings, self.songIds = zip(*results)
            self.embeddings = np.array(self.embeddings)
            self.songIds = np.array(self.songIds)

        logger.info("Normalizing embeddings")
        self.embeddings = self.embeddings / \
            np.linalg.norm(self.embeddings, axis=1, keepdims=True)

        reducer = None
        if self.reduction:
            import umap
            logger.info("UMAP reduction")
            reducer = umap.UMAP(
                n_components=self.reduction_components,
                metric="cosine"
            )
            self.embeddings = reducer.fit_transform(self.embeddings)

        logger.info("Computing clusters")
        cluster_labels = self.method.get_cluster_labels(self.embeddings)

        unique = np.unique(cluster_labels)
        logger.info(np.histogram(cluster_labels, bins=len(unique))[0])

        playlists = []
        if not self.no_smart_naming:
            logger.info("Computing smart-names")
            smart_naming = SmartNaming(
                self.smart_naming_size,
                self.smart_naming_sep,
                self.smart_naming_no_macro_genre,
                self.genres_list,
                reducer  # must compute the names in the reduced space if available
            )
            for label in np.unique(cluster_labels):
                cluster_songIds = self.songIds[cluster_labels == label]
                cluster_centroid = np.mean(
                    self.embeddings[cluster_labels == label], axis=0)
                name = smart_naming.get_name(centroid=cluster_centroid)
                playlist_name = f"{self.prefix}{name}"
                playlist_songs = cluster_songIds.tolist()
                playlists.append((playlist_name, playlist_songs))
        else:
            for label in np.unique(cluster_labels):
                cluster_songIds = self.songIds[cluster_labels == label]
                playlist_name = f"{self.prefix}C{label}"
                playlist_songs = cluster_songIds.tolist()
                playlists.append((playlist_name, playlist_songs))

        if not self.no_merge:
            logger.info("Merging clusters with same label")
            playlists_ = collections.defaultdict(list)
            for playlist_name, playlist_songs in playlists:
                playlists_[playlist_name].extend(playlist_songs)
            playlists = list(playlists_.items())

        if self.oddities > 0:
            logger.info("Segregating oddities")
            oddities = []
            playlists_ = [(f"{self.prefix}oddities", oddities)]
            for playlist_name, playlist_songs in playlists:
                if len(playlist_songs) <= self.oddities:
                    oddities.extend(playlist_songs)
                else:
                    playlists_.append((playlist_name, playlist_songs))
            playlists = playlists_

        if not self.no_save:
            logger.info(f"Creating playlists")
            navidrome = Navidrome()
            for playlist_name, playlist_songs in playlists:
                navidrome.create_playlist(
                    name=playlist_name, songIds=playlist_songs)
                logger.info(
                    f"'{playlist_name}' created ({len(playlist_songs)} songs)")
            logger.info(f"{len(playlists)} playlists created ")
