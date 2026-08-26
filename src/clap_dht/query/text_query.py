import logging

from clap_dht.query.query import Query
from clap_dht.update.text_feature_extractor import TextFeatureExtractor


logger = logging.getLogger("QUERY")

class TextQuery(Query):
    def __init__(self, temperature, limit, text):
        super().__init__(temperature=temperature, limit=limit)
        self.text = text
        logger.debug(f"TextQuery text={text}")

    def get_embedding_by_text(self):
        extractor = TextFeatureExtractor()
        embeddings = extractor.clap([self.text])
        return embeddings[0]

    def get(self):
        embedding = self.get_embedding_by_text()
        results = self.query_similar(embedding)
        return results