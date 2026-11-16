import os
import pathlib

import filetype

from torch.utils.data import IterableDataset

from clapclap.utils.config import config
from clapclap.utils.logger import logger


class FilesystemDatasetAll(IterableDataset):
    def __init__(self):
        self.root_dir = pathlib.Path(config.DATA_ROOT_DIR)

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
