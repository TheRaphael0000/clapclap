
import logging
import numpy as np

from scipy.spatial.distance import cdist

import logging

logger = logging.getLogger("SMART_NAMING")

class SmartNaming:
    def __init__(self, size, sep, use_macro_genre, genres_list):
        self.size = size
        self.sep = sep
        self.genres_list = genres_list
        self.use_macro_genre = use_macro_genre

        from clapclap.update.text_feature_extractor import TextFeatureExtractor
        from clapclap.update.text_feature_extractor import GenreDataset
        self.te = TextFeatureExtractor()

        if use_macro_genre:
            from clapclap.update.text_feature_extractor import MacroGenreDataset
            macro_genre_dataset = MacroGenreDataset()
            logger.info(f"Computing centroids: Macro Genres ({len(macro_genre_dataset)} genres)")
            self.macro_genres, self.macro_genres_centroids = self.compute_genres_centroids(macro_genre_dataset)

        genre_dataset = GenreDataset(self.genres_list)
        logger.info(f"Computing centroids: {genres_list} ({len(genre_dataset)} genres)")
        self.genres, self.genres_centroids = self.compute_genres_centroids(genre_dataset)


    def compute_genres_centroids(self, dataset):
        from torch.utils.data import DataLoader
        dl = DataLoader(dataset, batch_size=128)
        genres = []
        genres_centroids = []
        for i, b in enumerate(dl):
            logger.debug(f"Batch {i}")
            genres.extend(b)
            # add quotes to ensure multi-word genre embeddings are correctly computed 
            b = [f'"{bi}"' for bi in b]
            genres_centroids.extend(self.te.clap(b))

        return np.array(genres), np.array(genres_centroids)
        

    def get_name(self, centroid):
        names = []
        
        if self.use_macro_genre:
            macro_distances = cdist([centroid], self.macro_genres_centroids, metric='cosine')[0]
            macro_genre = self.macro_genres[np.argmin(macro_distances)]
            names.append(macro_genre)

        distances = cdist([centroid], self.genres_centroids, metric='cosine')[0]
        arg_sorted_distances = np.argsort(distances)
        selected_indices = arg_sorted_distances[0:self.size]
        selected_genres = self.genres[selected_indices]
        sub_genres = self.sep.join(selected_genres)
        names.append(sub_genres)

        name = "/".join(names)
        return name