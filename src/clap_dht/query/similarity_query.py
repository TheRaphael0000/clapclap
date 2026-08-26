import logging

from sqlalchemy import select, func
from pgvector.sqlalchemy import avg
import numpy as np

from clap_dht.db import DB, Embedding
from clap_dht.query.query import Query

logger = logging.getLogger("QUERY")


class SimilarityQuery(Query):
    def __init__(self, limit, temperature, path = None, songId = None, albumId = None, artistId = None):
        super().__init__(temperature=temperature, limit=limit)
        logger.debug(f"Query created path={path} songId={songId} albumId={albumId} artistId={artistId}")
        self.path = path
        self.songId = songId
        self.albumId = albumId
        self.artistId = artistId


    def get(self):
        if self.path is not None:
            embedding = self.get_embedding_by_path(self.path)
        if self.songId is not None:
            embedding = self.get_embedding_by_songId(self.songId)
        if self.albumId is not None:
            embedding = self.get_embedding_by_albumId(self.albumId)
        if self.artistId is not None:
            embedding = self.get_embedding_by_artistId(self.artistId)
        if embedding is None:
            raise Exception("Embedding not found")
        results = self.query_similar(embedding)
        return results


    def get_embedding_by_path(self, path):
        with self.db as session:
            return session.scalar(select(Embedding.embedding).where(Embedding.path == path))
        
    def get_embedding_by_songId(self, songId):
        with self.db as session:
            return session.scalar(select(Embedding.embedding).where(Embedding.songId == songId))

    def get_embedding_by_albumId(self, albumId):
        with self.db as session:
            return session.scalar(select(avg(Embedding.embedding)).where(Embedding.albumId == albumId))
        
    def get_embedding_by_artistId(self, artistId):
        with self.db as session:
            return session.scalar(select(avg(Embedding.embedding)).where(Embedding.artistId == artistId))

    @staticmethod
    def count():
        with DB() as session:
            return session.query(Embedding.path).count()