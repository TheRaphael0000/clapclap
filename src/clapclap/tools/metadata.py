from tinytag import TinyTag
from clapclap.update.datasets import FilesystemDatasetAll


def get_tag(tinytag, tag):
    results = []
    if tag in tinytag.other:
        for value in tinytag.other[tag]:
            if value is None:
                continue
            results.append(value)
    return results


class Metadata:
    def __init__(self, no_fingerprint, no_replaygain):
        self.no_fingerprint = no_fingerprint
        self.no_replaygain = no_replaygain

        if self.no_fingerprint and self.no_replaygain:
            raise Exception("Please select at least one tool checker")
        self.dataset = FilesystemDatasetAll()

    def run(self):
        for subpath, fullpath, _, _, _ in self.dataset:
            tinytag = TinyTag.get(filename=fullpath)
            if not self.no_fingerprint:
                tag = get_tag(tinytag, "acoustid_fingerprint")
                if len(tag) <= 0:
                    print(f"'{subpath}' - fingerprint missing")
            if not self.no_replaygain:
                tag = get_tag(tinytag, "replaygain_track_gain")
                if len(tag) <= 0:
                    print(f"'{subpath}' - replaygain missing")
