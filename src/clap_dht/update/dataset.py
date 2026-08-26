import os
import pathlib

from sqlalchemy import exists, select
import filetype

from torch.utils.data import IterableDataset

from clap_dht.db import DB, Embedding
from clap_dht.utils.config import config

import logging

from clap_dht.navidrome.navidrome import Navidrome
logger = logging.getLogger("UPDATER")

class DBChecker:
    def __init__(self):
        self.db = DB()

    def check(self, subpath):
        with self.db as session:
            is_exist = session.scalar(select(exists().where(Embedding.path == subpath)))
            if is_exist:
                return True
        return False


class NavidromeDataset(IterableDataset):
    def __init__(self, force_process):
        self.root_dir = pathlib.Path(config.NAVIDROME_ROOTDIR)
        self.force_process = force_process
        self.db_checker = DBChecker()

    def __iter__(self):
        navidrome = Navidrome()
        for s in navidrome.songs_iterator():
            fullpath = pathlib.Path(s["path"])
            subpath = str(fullpath.relative_to(self.root_dir))
            fullpath = str(fullpath)

            if not self.force_process:
                if self.db_checker.check(subpath):
                    logger.debug(f"Skipped (already in db): '{subpath}'")
                    continue

            audio_bytes = navidrome.download(songId=s["id"])
            logger.info(f"Loaded: '{subpath}'")
            yield audio_bytes, subpath, s["id"], s["albumId"], s["artistId"]


class FilesystemDatasetAll(IterableDataset):
    def __init__(self):
        self.root_dir = pathlib.Path(config.DATA_ROOTDIR)

    def __iter__(self):
        for fullpath in pathlib.Path(self.root_dir).rglob("*"):
            subpath = str(fullpath.relative_to(self.root_dir))
            fullpath = str(fullpath)

            if not os.path.isfile(fullpath):
                continue

            # filetype is smart and only read a few bytes
            if not filetype.is_audio(fullpath):
                logger.debug(f"Skipped (not audio): '{subpath}'")
                continue

            yield subpath, fullpath, None, None, None


class FilesystemDataset(IterableDataset):
    def __init__(self, force_process):
        self.root_dir = pathlib.Path(config.DATA_ROOTDIR)
        self.force_process = force_process
        self.db_checker = DBChecker()

    def __iter__(self):
        for fullpath in pathlib.Path(self.root_dir).rglob("*"):
            subpath = str(fullpath.relative_to(self.root_dir))
            fullpath = str(fullpath)

            if not os.path.isfile(fullpath):
                continue

            if not self.force_process:
                if self.db_checker.check(subpath):
                    logger.debug(f"Skipped (already in db): '{subpath}'")
                    continue

            # filetype is smart and only read a few bytes
            if not filetype.is_audio(fullpath):
                logger.debug(f"Skipped (not audio): '{subpath}'")
                continue

            audio_bytes = open(fullpath, "rb").read()

            logger.info(f"Loaded: '{subpath}'")
            yield audio_bytes, subpath, None, None, None