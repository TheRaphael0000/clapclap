import pathlib

from torch.utils.data import IterableDataset

from clapclap.update.datasets.db_checker import DBChecker
from clapclap.utils.config import config
from clapclap.navidrome.navidrome import Navidrome
from clapclap.utils.log import logger


class NavidromeDataset(IterableDataset):
    def __init__(self, force_process):
        self.root_dir = pathlib.Path(config.NAVIDROME_ROOT_DIR)
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
            yield {
                "audio_bytes": audio_bytes,
                "subpath": subpath,
                "songId": s.get("id", ""),
                "albumId": s.get("albumId", ""),
                "artistId": s.get("artistId", ""),
                "duration": s.get("duration", 0),
            }
