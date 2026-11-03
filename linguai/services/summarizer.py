import math
from sklearn.feature_extraction.text import TfidfVectorizer
from linguai.text_utils import split_sentences

class Summarizer:
    def extractive(self, text, ratio=0.25):
        if not 0 < ratio <= 1:
            raise ValueError("ratio deve estar entre 0 e 1.")
        sentences = split_sentences(text)
        if len(sentences) <= 2:
            return " ".join(sentences)
        try:
            matrix = TfidfVectorizer(lowercase=True, strip_accents="unicode", token_pattern=r"(?u)\\b\\w\\w+\\b").fit_transform(sentences)
            scores = matrix.sum(axis=1).A1
        except ValueError:
            scores = [len(s.split()) for s in sentences]
        scores[0] *= 1.08
        count = max(1, min(len(sentences), math.ceil(len(sentences) * ratio)))
        selected = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)[:count]
        return " ".join(sentences[i] for i in sorted(selected))

    def abstractive(self, text, model_name, offline=False):
        from transformers import pipeline
        summarizer = pipeline("summarization", model=model_name, tokenizer=model_name, device=-1, model_kwargs={"local_files_only": offline})
        result = summarizer(text[:10000], max_length=180, min_length=35, do_sample=False, truncation=True)
        return result[0]["summary_text"]
