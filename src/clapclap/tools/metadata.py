from tinytag import TinyTag

from clapclap.update.dataset import FilesystemDatasetAll
from clapclap.utils.log import logger

def get_tag(tinytag, tag):
    results = []
    if tag in tinytag.other:
        for value in tinytag.other[tag]:
            if value is None:
                continue
            results.append(value)
    return results



class Metadata:
    def __init__(self, fingerprint, replaygain):
        self.fingerprint = fingerprint
        self.replaygain = replaygain

        if not self.fingerprint and not self.replaygain:
            raise Exception("Please select at least one tool checker")
        self.dataset = FilesystemDatasetAll()


    def run(self):
        for subpath, fullpath, _, _, _ in self.dataset:
            tinytag = TinyTag.get(filename=fullpath)
            if self.fingerprint:
                tag = get_tag(tinytag, "acoustid_fingerprint")
                if len(tag) <= 0:
                    print(f"'{subpath}' - fingerprint missing")
            if self.replaygain:
                tag = get_tag(tinytag, "replaygain_track_gain")
                if len(tag) <= 0:
                    print(f"'{subpath}' - replaygain missing")