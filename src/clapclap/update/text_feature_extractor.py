import torch
from transformers import AutoTokenizer, ClapTextModelWithProjection
from clapclap.utils import Timer
from clapclap.utils.consts import CLAP_MODEL, CLAP_PROCESSOR
from clapclap.utils.log import logger


class TextFeatureExtractor:
    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        logger.debug(f"Embedding Projection Device: {self.device}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                CLAP_PROCESSOR, local_files_only=True)
            self.model = ClapTextModelWithProjection.from_pretrained(
                CLAP_MODEL, local_files_only=True)
        except Exception as e:
            self.tokenizer = AutoTokenizer.from_pretrained(CLAP_PROCESSOR)
            self.model = ClapTextModelWithProjection.from_pretrained(
                CLAP_MODEL)

        self.model = self.model.to(self.device)
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
