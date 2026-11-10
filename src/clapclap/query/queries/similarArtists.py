from sqlalchemy import select, func, cast
import numpy as np
from pgvector.sqlalchemy import VECTOR

from clapclap.db import DB, Embedding
from clapclap.navidrome.navidrome import Navidrome
from clapclap.query.queries.query import Query
from clapclap.utils.log import logger


class SimilarArtists(Query):
    def __init__(self, embedding, limit: int):
        self.embedding = embedding
        self.limit = limit
        self.db = DB()
        self.order_by_factor = 1
        logger.debug(
            f"Query similar artists limit={limit}")
        self.results = None

    def __str__(self):
        return self.get_text()

    def ensure_results(self):
        if self.results is None:
            self.results = self.query_similar(self.embedding)

    def save_to_playlist(self, name: str):
        raise NotImplementedError()

    def get_text(self):
        self.ensure_results()
        output = [f"{distance_to_avg_embedding:4f} - '{artistId}'" for artistId,
                  distance_to_avg_embedding in self.results]
        return "\n".join(output)

    def get_json(self):
        self.ensure_results()
        output = [
            {
                "artistId": artistId,
                "score": distance_to_avg_embedding
            } for artistId, distance_to_avg_embedding in self.results
        ]
        return output

    def query_similar(self, embedding):
        logger.debug(f"query similar artists, limit: {self.limit}")
        with self.db as session:
            avg_embedding = func.avg(
                Embedding.embedding).label("avg_embedding")

            distance_to_avg_embedding = avg_embedding.op("<=>")(
                cast(embedding, VECTOR)
            ).label("dist")

            stmt = select(
                Embedding.artistId,
                distance_to_avg_embedding
            )
            stmt = stmt.group_by(Embedding.artistId)
            stmt = stmt.order_by(distance_to_avg_embedding)
            stmt = stmt.limit(self.limit)
            results = session.execute(stmt).all()

            return results
