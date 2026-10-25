import numpy as np

from scipy.spatial.distance import cdist

from clapclap.utils.log import logger


class SmartNaming:
    def __init__(self, labels, sizes, label_sep, level_sep, reducer):
        self.labels = labels
        self.sizes = sizes
        self.label_sep = label_sep
        self.level_sep = level_sep
        self.reducer = reducer
        self.Xs = []
        self.Ys = []

        from clapclap.clustering.smartnaming.LabelDataset import LabelDataset
        from clapclap.update.text_feature_extractor import TextFeatureExtractor
        self.te = TextFeatureExtractor()

        for label in self.labels:
            if label.lower() == "none":
                continue
            label_dataset = LabelDataset(label)
            logger.info(
                f"Computing centroids: {label} ({len(label_dataset)} labels)")
            X, Y = self.compute_genres_centroids(label_dataset)
            self.Xs.append(X)
            self.Ys.append(Y)

    def compute_genres_centroids(self, dataset):
        from torch.utils.data import DataLoader
        dl = DataLoader(dataset, batch_size=128)
        X = []
        Y = []
        for i, b in enumerate(dl):
            logger.debug(f"Batch {i}")
            Y.extend(b)
            # add quotes to ensure multi-word genre embeddings are correctly computed
            b = [f'"{bi}"' for bi in b]
            X.extend(self.te.clap(b))

        if self.reducer:
            X = self.reducer.transform(X)

        return np.array(X), np.array(Y)

    def get_name(self, centroid):
        parts = []

        metric = 'cosine'
        if self.reducer:
            metric = 'euclidean'

        for X, Y, size in zip(self.Xs, self.Ys, self.sizes):
            distances = cdist([centroid], X, metric=metric)[0]
            arg_sorted_distances = np.argsort(distances)
            selected_indices = arg_sorted_distances[0:size]
            ys = Y[selected_indices]
            ys_joined = self.label_sep.join(ys)
            parts.append(ys_joined)

        name = self.level_sep.join(parts)

        return name
