import logging

from sqlalchemy import select, func
import numpy as np

from clapclap.db import DB, Embedding
from clapclap.navidrome.navidrome import Navidrome

logger = logging.getLogger("QUERY")

class Query:
    def __init__(self, temperature, limit):
        self.limit = limit
        if temperature <= 0:
            self.temperature = None
        else:
            self.temperature = min(max(temperature, 1e-4), 1)
        self.db = DB()
        self.proximity_function = Embedding.embedding.cosine_distance
        self.order_by_factor = 1
        logger.debug(f"Query limit={limit}, temperature={temperature}")
        self.results = None

    def __str__(self):
        return self.get_text()

    def save_to_playlist(self, name):
        self.ensure_results()
        navidrome = Navidrome()
        ids = [embedding.songId for embedding, _ in self.results]
        navidrome.create_playlist(name=name, songIds=ids)

    def ensure_results(self):
        if self.results is None:
            self.results = self.get()

    def get_text(self):
        self.ensure_results()
        output = [f"{score:4f} - '{embedding.path}'" for embedding, score in self.results]
        return "\n".join(output)

    def get_json(self):
        self.ensure_results()
        output = [{"path": embedding.path, "songId": embedding.songId, "albumId": embedding.albumId, "artistId": embedding.artistId, "score": score} for embedding, score in self.results]
        return output

    def query_similar(self, embedding):
        with self.db as session:
            proximity_expr = self.proximity_function(embedding).label("metric")

            if self.temperature:
                db_size = session.scalar(select(func.count()).select_from(Embedding))
                # we don't want to query the whole database to do a real temperature softmax
                # so we are eye balling an additional number of samples ¯\_(ツ)_/¯
                # a not very scientific formula with a lot of magic numbers:
                query_limit = int((3 * self.limit) + (10 * max(self.temperature, 0.3) * (db_size ** 0.5)))
            else:
                query_limit = self.limit

            stmt = select(Embedding, proximity_expr).filter(proximity_expr > 0).order_by(self.order_by_factor * proximity_expr).limit(query_limit)
            results = session.execute(stmt).all()

            # softmax temperature
            if self.temperature:
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
            else:
                return results