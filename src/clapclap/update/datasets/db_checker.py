from sqlalchemy import exists, select
from clapclap.db import DB, Embedding


class DBChecker:
    def __init__(self):
        self.db = DB()

    def check(self, subpath):
        with self.db as session:
            is_exist = session.scalar(
                select(exists().where(Embedding.path == subpath)))
            if is_exist:
                return True
        return False
