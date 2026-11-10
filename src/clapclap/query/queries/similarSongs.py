from sqlalchemy import select, func
import numpy as np

from clapclap.db import DB, Embedding
from clapclap.navidrome.navidrome import Navidrome
from clapclap.query.queries.query import Query
from clapclap.utils.log import logger


class SimilarSongs(Query):
    def __init__(self, embedding, temperature: float, limit: int):
        logger.debug(
            f"Query similar songs limit={limit}, temperature={temperature}")
        self.embedding = embedding
        if temperature <= 0:
            self.temperature = None
        else:
            self.temperature = min(max(temperature, 1e-4), 1)
        self.limit = limit
        self.db = DB()
        self.results = None

    def __str__(self):
        return self.get_text()

    def ensure_results(self):
        if self.results is None:
            self.results = self.query_similar(self.embedding)

    def save_to_playlist(self, name: str):
        self.ensure_results()
        navidrome = Navidrome()
        ids = [embedding.songId for embedding, _ in self.results]
        navidrome.create_playlist(name=name, songIds=ids)

    def get_text(self):
        self.ensure_results()
        output = [f"{score:4f} - '{embedding.path}'" for embedding,
                  score in self.results]
        return "\n".join(output)

    def get_json(self):
        self.ensure_results()
        output = [
            {
                "path": embedding.path,
                "songId": embedding.songId,
                "albumId": embedding.albumId,
                "artistId": embedding.artistId,
                "score": score
            } for embedding, score in self.results
        ]
        return output

    def limit_by_temperature(self, session):
        if not self.temperature:
            return self.limit

        db_size = session.scalar(
            select(func.count()).select_from(Embedding))
        # we don't want to query the whole database to do a real temperature softmax
        # so we are eye balling an additional number of samples ¯\_(ツ)_/¯
        # a not very scientific formula with a lot of magic numbers:
        return int(
            (3 * self.limit) + (10 * max(self.temperature, 0.3) * (db_size ** 0.5)))

    def results_by_temperature(self, results):
        # softmax temperature
        if not self.temperature:
            return results

        distances = np.array([r.metric for r in results])
        similarities = -distances

        scaled_sims = similarities / self.temperature
        exp_sims = np.exp(scaled_sims - np.max(scaled_sims))
        probabilities = exp_sims / np.sum(exp_sims)

        sampled_indices = np.random.choice(
            len(results),
            size=self.limit,
            replace=False,
            p=probabilities
        )
        return [results[i] for i in sampled_indices]

    def query_similar(self, embedding):
        with self.db as session:
            proximity_expr = Embedding.embedding.cosine_distance(embedding)
            query_limit = self.limit_by_temperature(session)
            stmt = select(
                Embedding,
                proximity_expr
            )
            stmt = stmt.order_by(proximity_expr)
            stmt = stmt.limit(query_limit)
            results = session.execute(stmt).all()
            results = self.results_by_temperature(results)
            return results
