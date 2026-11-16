from .embedding_fetcher import EmbeddingFetcher
from clapclap.update.extractor import TextFeatureExtractor
from clapclap.utils.logger import logger


class TextEmbedding(EmbeddingFetcher):
    def __init__(self, text):
        super().__init__()
        self.text = text
        logger.debug(f"TextEmbedding created  text={text}")

    def get_embedding(self):
        extractor = TextFeatureExtractor()
        embeddings = extractor.clap([self.text])
        return embeddings[0]
