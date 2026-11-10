from clapclap.query.embedding_fetcher.embeddingFetcher import EmbeddingFetcher
from clapclap.update.text_feature_extractor import TextFeatureExtractor

from clapclap.utils.log import logger


class TextEmbedding(EmbeddingFetcher):
    def __init__(self, text):
        super().__init__()
        self.text = text
        logger.debug(f"TextEmbedding created  text={text}")

    def get_embedding(self):
        extractor = TextFeatureExtractor()
        embeddings = extractor.clap([self.text])
        return embeddings[0]
