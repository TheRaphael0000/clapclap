import pathlib

import filetype

from torch.utils.data import IterableDataset

from clapclap.update.datasets.db_checker import DBChecker
from clapclap.update.datasets.quickscan import Quickscan
from clapclap.utils.config import config
from clapclap.utils.logger import logger


class FilesystemDataset(IterableDataset):
    def __init__(self, force_process, full_scan):
        self.force_process = force_process
        self.root_dir = pathlib.Path(config.DATA_ROOT_DIR)

        self.quickscan = Quickscan(
            self.root_dir, config.DATA_QUICKSCAN_STATE, full_scan=full_scan)
        self.db_checker = DBChecker()

    def __iter__(self):
        for fullpath in self.quickscan.scan():
            subpath = str(fullpath.relative_to(self.root_dir))
            fullpath = str(fullpath)

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

            yield {
                "audio_bytes": audio_bytes,
                "subpath": subpath,
                "songId": "",
                "albumId": "",
                "artistId": "",
                "duration": "",
            }
