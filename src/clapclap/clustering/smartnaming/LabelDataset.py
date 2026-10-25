from torch.utils.data import Dataset

from clapclap.utils.types import LabelList

from .labels.navidrome_genres import get_navidrome_genres
from .labels.stdin import get_stdin_labels
from .labels.musicbrainz_genres import musicbrainz_genres
from .labels.everynoise_genres import everynoise_genres
from .labels.main_genres import main_genres
from .labels.emotions import emotions


class LabelDataset(Dataset):
    def __init__(self, label_list: LabelList):
        genres = set()
        if label_list == "everynoise" or label_list == "all":
            genres |= set(everynoise_genres)
        if label_list == "everynoise-100" or label_list == "all":
            genres |= set(everynoise_genres[0:100])
        if label_list == "everynoise-1000" or label_list == "all":
            genres |= set(everynoise_genres[0:1000])
        if label_list == "musicbrainz" or label_list == "all":
            genres |= set(musicbrainz_genres)
        if label_list == "main_genres" or label_list == "all":
            genres |= set(main_genres)
        if label_list == "emotions" or label_list == "all":
            genres |= set(emotions)
        if label_list == "stdin" or label_list == "all":
            genres |= get_stdin_labels()
        if label_list == "navidrome" or label_list == "all":
            genres |= get_navidrome_genres()
        self.genres = list(genres)

    def __len__(self):
        return len(self.genres)

    def __getitem__(self, idx):
        return self.genres[idx]
