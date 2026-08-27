import os
import pathlib
import logging
import threading
import queue
import atexit

from sqlalchemy.dialects.postgresql import insert

from torch.utils.data import DataLoader

from clapclap.db import DB, Embedding
from clapclap.update.audio_feature_extractor import AudioFeatureExtractor
from clapclap.update.dataset import FilesystemDataset, NavidromeDataset

from clapclap.utils.config import config
from clapclap.utils import Timer

logger = logging.getLogger("UPDATER")


class Updater:
    def __init__(self, batch_size, max_workers, force_process, prefetch_factor, ignore_existing_fingerprint, navidrome):
        self.db = DB()

        if navidrome:
            self.dataset = NavidromeDataset(force_process)
        else:
            self.dataset = FilesystemDataset(force_process)
            
        self.dataloader = DataLoader(self.dataset, batch_size=batch_size, prefetch_factor=prefetch_factor, num_workers=1)
        self.loader_iter = iter(self.dataloader)
        
        atexit.register(self.stop_dataloader)
        
        self.audio_feature_extractor = AudioFeatureExtractor(max_workers, ignore_existing_fingerprint)
        self.to_save_queue = queue.Queue()


    def stop_dataloader(self):
        logger.info(f"Stopping DataLoader worker")
        if hasattr(self.loader_iter, '_workers'):
            for i, worker in enumerate(self.loader_iter._workers):
                if worker.is_alive():
                    worker.terminate()
                    logger.info(f"worker {i} terminated")
                    worker.join()

    def saver(self):
        with Timer("Saver"):
            while True:
                data = self.to_save_queue.get()
                if data is None:
                    logger.info(f"Stopping saver process")
                    return
                
                i, subpaths, songIds, albumIds, artistIds, results = data

                with Timer(f"Saving batch {i}", info=True):
                    payload = [
                        {
                            "path": subpath,
                            "fingerprint": fingerprint,
                            "embedding": embedding,
                            "songId": songId if songId != "" else None,
                            "albumId": albumId if albumId != "" else None,
                            "artistId": artistId if artistId != "" else None,
                        }
                        for subpath, songId, albumId, artistId, (fingerprint, embedding) in zip(subpaths, songIds, albumIds, artistIds, results)
                        if embedding is not None
                    ]

                    if len(payload) <= 0:
                        continue
                    
                    stmt = insert(Embedding).values(payload)
                    
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["path"],
                        set_={
                            "fingerprint": stmt.excluded.fingerprint,
                            "embedding": stmt.excluded.embedding,
                        },
                    )

                    with self.db as session:
                        session.execute(stmt)
                        session.commit()



    def start(self):
        logger.info(f"Stating database update with: {type(self.dataset)}")

        saver = threading.Thread(target=self.saver)
        saver.start()

        for i, batch in enumerate(self.loader_iter):
            with Timer(f"Processing batch {i}", info=True):
                results = self.audio_feature_extractor.process_batch(batch["audio_bytes"], batch["subpath"])
                
                self.to_save_queue.put((i, batch["subpath"], batch["songId"], batch["albumId"], batch["artistId"], results))

        self.to_save_queue.put(None)
        saver.join()
        logger.info(f"Update completed")


