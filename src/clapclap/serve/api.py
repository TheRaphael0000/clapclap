from enum import Enum
import logging
from fastapi import FastAPI, HTTPException, Request
import uvicorn

from clapclap.db import DB
from clapclap.query import SimilarityQuery
from clapclap.serve.db_data import DBDATA
from clapclap.serve.dht_db import DHTDB

logger = logging.getLogger("API")


class ProximityFunctions(str, Enum):
    max_inner_product="max_inner_product"
    cosine_distance="cosine_distance"
    l1_distance="l1_distance"

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
    async def route_query(request: Request, limit: int = 100, temperature: float = 0, songId: str = None, albumId: str = None, artistId: str = None):
        try:
            query = SimilarityQuery(limit=limit, temperature=temperature, songId=songId, albumId=albumId, artistId=artistId)
            return query.get_json()
        except Exception as e:
            logger.debug(e)
            raise HTTPException(status_code=404, detail=str(e))

    # create_app() return
    return app, dht_node


class API:
    def __init__(self, host, port):
        DB() # to ensure connection to the db before starting the app
        self.host = host
        self.port = port
        self.no_dht = True
        self.app, self.dht_node = create_app(not self.no_dht)

 
    def start(self):
        logger.debug(f"host={self.host}, port={self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)