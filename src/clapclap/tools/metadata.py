from tinytag import TinyTag

from clapclap.update.dataset import FilesystemDatasetAll

import logging
logger = logging.getLogger("METADATA")

class Metadata:
    def __init__(self, fingerprint, replaygain):
        self.fingerprint = fingerprint
        self.replaygain = replaygain

        if not self.fingerprint and not self.replaygain:
            raise Exception("Please select at least one tool checker")
        self.dataset = FilesystemDatasetAll()

    def fingerprint_in_tags(self, file):
        tags = TinyTag.get(filename=file)
        possible_keys = ["acoustid_fingerprint"]

        for pk in possible_keys:
            if pk in tags.other:
                for base64_value in tags.other[pk]:
                    if base64_value is None:
                        continue
                    return base64_value
        return None

    def run(self):
        for subpath, fullpath in self.dataset:
            if self.fingerprint:
                if self.fingerprint_in_tags(fullpath) is None:
                    logger.info(f"fingerprint missing for {subpath}")