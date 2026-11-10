from clapclap.db import DB
from clapclap.query.fetchers.dbEmbedding import DBEmbedding


class DBDATA:

    def __ini__(self):
        pass

    def info(self):
        embeddings = DBEmbedding.count()
        return {
            "db": {
                "embeddings": embeddings,
            }
        }
