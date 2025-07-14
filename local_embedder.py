from sentence_transformers import SentenceTransformer

class LocalEmbeddingFunction:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def __call__(self, texts):
        return self.model.encode(texts).tolist()
