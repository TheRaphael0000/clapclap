import logging

import torch
import transformers
from transformers import AutoTokenizer, ClapTextModelWithProjection
from torch.utils.data import DataLoader, Dataset
from clapclap.utils.musicbrainz_genres import musicbrainz_genres
from clapclap.utils.everynoise_genres import everynoise_genres
from clapclap.utils.macro_genres import macro_genres
from clapclap.utils.types import GenresList

from clapclap.utils import Timer
from clapclap.utils.consts import CLAP_MODEL, CLAP_PROCESSOR

transformers.logging.set_verbosity_error()
logger = logging.getLogger("UPDATER")


class TextFeatureExtractor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.debug(f"Embedding Projection Device: {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(CLAP_PROCESSOR)
        self.model = ClapTextModelWithProjection.from_pretrained(CLAP_MODEL).to(self.device)
        self.model.eval()

    def clap(self, texts):
        with Timer("tokenizer"):
            inputs = self.tokenizer(
                texts, 
                padding=True, 
                return_tensors="pt"
            )

        embeddings = []
        with Timer("clap projection"):
            inputs = inputs.to(self.device)
            outputs = self.model(**inputs)
            result = outputs.text_embeds.detach().cpu().numpy()
            for r in result:
                embeddings.append(r)
        return embeddings

class MacroGenreDataset(Dataset):
    def __init__(self):
        self.genres = macro_genres

    def __len__(self):
        return len(self.genres)

    def __getitem__(self, idx):
        return self.genres[idx]

class GenreDataset(Dataset):
    def __init__(self, genres_list: GenresList):
        genres = set()
        if genres_list == "everynoise" or genres_list == "all":
            genres |= set(everynoise_genres)
        if genres_list == "everynoise-100" or genres_list == "all":
            genres |= set(everynoise_genres[0:100])
        if genres_list == "everynoise-1000" or genres_list == "all":
            genres |= set(everynoise_genres[0:1000])
        if genres_list == "musicbrainz" or genres_list == "all":
            genres |= set(musicbrainz_genres)
        self.genres = list(genres)

    def __len__(self):
        return len(self.genres)

    def __getitem__(self, idx):
        return self.genres[idx]