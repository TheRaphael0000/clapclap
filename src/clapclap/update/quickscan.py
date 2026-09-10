import json
from pathlib import Path
import logging

from clapclap.utils import Timer

logger = logging.getLogger("QUICKSCAN")


class Quickscan:
    def __init__(self, scan_folder_path, state_path, force):
        self.scan_folder_path = scan_folder_path
        self.state_path = state_path
        self.force = force

    def load_state(self):
        logger.debug(f"loading state file: {self.state_path}")
        try:
            self.saved_state = json.load(open(self.state_path, "r"))
        except:
            logger.info(f"no state file: {self.state_path}, using empty state")
            self.saved_state = {}

    def save_state(self):
        logger.debug(f"saving state file: {self.state_path}")
        json.dump(self.saved_state, open(self.state_path, "w"))

    def scan(self):
        self.load_state()
        logger.debug(f"start scanning")
        with Timer("quickscan"):
            yield from self._scan(self.scan_folder_path)
        self.save_state()

    def _scan(self, folder):
        for f in Path(folder).iterdir():
            path = str(f.absolute())
            time = f.stat().st_mtime

            if self.force or path not in self.saved_state or time != self.saved_state[path]:
                is_dir = f.is_dir()
                if not is_dir:
                    yield f
                    continue
                yield from self._scan(f)
                if is_dir:
                    self.saved_state[path] = time