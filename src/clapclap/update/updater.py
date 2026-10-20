import logging
import threading
import queue
import atexit

from sqlalchemy.dialects.postgresql import insert

from torch.utils.data import DataLoader

from clapclap.db import DB, Embedding
from clapclap.update.audio_feature_extractor import AudioFeatureExtractor
from clapclap.update.dataset import FilesystemDataset, NavidromeDataset, FilesystemDatasetAll
from clapclap.utils import Timer
from clapclap.utils.log import logger
from clapclap.utils.types import DataSource


class Updater:
    def __init__(self, batch_size, max_workers, force_process, full_scan, prefetch_factor, ignore_existing_fingerprint, source: DataSource):
        self.db = DB()

        if source == "navidrome":
            self.dataset = NavidromeDataset(force_process)
        elif source == "fs":
            self.dataset = FilesystemDataset(force_process, full_scan)
        else:
            raise Exception("Invalid source")

        self.dataloader = DataLoader(
            self.dataset, batch_size=batch_size, prefetch_factor=prefetch_factor, num_workers=1)
        self.loader_iter = iter(self.dataloader)

        atexit.register(self.stop_dataloader)

        self.audio_feature_extractor = AudioFeatureExtractor(
            "start", 150, max_workers, ignore_existing_fingerprint)
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

                i, subpaths, songIds, albumIds, artistIds, duration, results = data

                with Timer(f"Saving batch {data[0]}", info=True):
                    payload = [
                        {
                            "path": subpath,
                            "fingerprint": fingerprint,
                            "embedding": embedding,
                            "songId": songId if songId != "" else None,
                            "albumId": albumId if albumId != "" else None,
                            "artistId": artistId if artistId != "" else None,
                            "duration": duration if duration != "" else None,
                            "embedding_method": embedding_method,
                            "embedding_duration": embedding_duration,
                        }
                        for subpath, songId, albumId, artistId, duration, (fingerprint, embedding, embedding_method, embedding_duration) in zip(subpaths, songIds, albumIds, artistIds, duration, results)
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
        logger.info(
            f"Stating database update with: {type(self.dataset).__name__}")

        saver = threading.Thread(target=self.saver)
        saver.start()

        for i, batch in enumerate(self.loader_iter):
            with Timer(f"Processing batch {i}", info=True):
                results = self.audio_feature_extractor.process_batch(
                    batch["audio_bytes"], batch["subpath"])
                self.to_save_queue.put(
                    (i, batch["subpath"], batch["songId"], batch["albumId"], batch["artistId"], batch["duration"], results))

        self.to_save_queue.put(None)
        saver.join()
        logger.info(f"Update completed")
