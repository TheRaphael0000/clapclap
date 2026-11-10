from fastapi import FastAPI, HTTPException, Request
import uvicorn
import traceback

from clapclap.db import DB
from clapclap.query.fetchers.dbEmbedding import DBEmbedding
from clapclap.query.queries.similarSongs import SimilarSongs
from clapclap.query.queries.similarArtists import SimilarArtists
from clapclap.serve.db_data import DBDATA
from clapclap.serve.dht_db import DHTDB
from clapclap.utils.log import logger


def create_app(with_dht):
    if with_dht:
        dht_node = DHTDB()
        app = FastAPI(lifespan=dht_node.lifespan)
    else:
        dht_node = None
        app = FastAPI()

    db_data = DBDATA()

    @app.get("/")
    async def route_info():
        info = {
            "up": True
        }
        if dht_node:
            info |= await dht_node.info()
        info |= db_data.info()

        return info

    @app.get("/similar_songs")
    async def similar_songs(request: Request, limit: int = 100, temperature: float = 0, songId: str = None, albumId: str = None, artistId: str = None):
        try:
            embedding = DBEmbedding(
                songId=songId,
                albumId=albumId,
                artistId=artistId
            ).get_embedding()
            query = SimilarSongs(
                embedding=embedding,
                limit=limit,
                temperature=temperature
            )
            return query.get_json()
        except Exception as e:
            logger.debug(e)
            raise HTTPException(status_code=404, detail=str(e))

    @app.get("/similar_artists")
    async def route_query(request: Request, limit: int = 100, songId: str = None, albumId: str = None, artistId: str = None):
        try:
            embedding = DBEmbedding(
                songId=songId,
                albumId=albumId,
                artistId=artistId
            ).get_embedding()
            query = SimilarArtists(
                embedding=embedding,
                limit=limit,
            )
            return query.get_json()
        except Exception as e:
            error_message = traceback.format_exc()
            logger.debug(error_message)
            raise HTTPException(status_code=404, detail=str(error_message))

    # create_app() return
    return app, dht_node


class API:
    def __init__(self, host, port):
        DB()  # to ensure connection to the db before starting the app
        self.host = host
        self.port = port
        self.no_dht = True
        self.app, self.dht_node = create_app(not self.no_dht)

    def start(self):
        logger.debug(f"host={self.host}, port={self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)
