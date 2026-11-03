import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from linguai.chunking import split_into_chunks

class SearchService:
    def __init__(self, embedding_model, offline=False):
        self.embedding_model, self.offline, self._model = embedding_model, offline, None
    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.embedding_model, local_files_only=self.offline)
        return self._model
    def search(self, text, query, top_k=5, use_embeddings=True):
        chunks = split_into_chunks(text)
        if not chunks:
            return []
        method = "Embeddings multilíngues"
        if use_embeddings:
            try:
                vectors = self._load_model().encode(chunks + [query], normalize_embeddings=True)
                scores = np.dot(vectors[:-1], vectors[-1])
            except Exception:
                scores = self._tfidf_scores(chunks, query)
                method = "TF-IDF (fallback lexical)"
        else:
            scores = self._tfidf_scores(chunks, query)
            method = "TF-IDF (fallback lexical)"
        order = np.argsort(scores)[::-1][:max(1, top_k)]
        return [{"text":chunks[int(i)], "score":float(scores[int(i)]), "method":method} for i in order if float(scores[int(i)]) > 0]
    @staticmethod
    def _tfidf_scores(chunks, query):
        try:
            matrix = TfidfVectorizer(strip_accents="unicode").fit_transform(chunks + [query])
            return cosine_similarity(matrix[-1], matrix[:-1]).ravel()
        except ValueError:
            return np.zeros(len(chunks))
