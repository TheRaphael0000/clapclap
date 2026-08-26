from clapclap.db import DB
from clapclap.query.similarity_query import SimilarityQuery


class DBDATA:

    def __ini__(self):
        pass

    def info(self):
        embeddings = SimilarityQuery.count()
        return {
            "db": {
                "embeddings": embeddings,
            }
        }