from linguai.services.search import SearchService
from linguai.text_utils import split_sentences

class QuestionAnsweringService:
    def __init__(self, search_service, qa_model, offline=False):
        self.search_service, self.qa_model, self.offline, self._pipeline = search_service, qa_model, offline, None
    def answer(self, text, question, use_transformer=False):
        hits = self.search_service.search(text, question, top_k=3)
        if not hits:
            return {"answer":"Não encontrei evidências relevantes no documento.", "evidence":[]}
        evidence = [h["text"] for h in hits]
        if use_transformer:
            try:
                from transformers import pipeline
                if self._pipeline is None:
                    self._pipeline = pipeline("question-answering", model=self.qa_model, tokenizer=self.qa_model, device=-1, model_kwargs={"local_files_only":self.offline})
                result = self._pipeline(question=question, context=" ".join(evidence))
                if result.get("answer") and float(result.get("score",0)) >= 0.05:
                    return {"answer":result["answer"], "evidence":evidence, "confidence":float(result["score"])}
            except Exception:
                pass
        sentences = [s for block in evidence for s in split_sentences(block)]
        scores = self.search_service._tfidf_scores(sentences, question) if sentences else []
        answer = sentences[int(scores.argmax())] if len(scores) and max(scores)>0 else evidence[0]
        return {"answer":answer, "evidence":evidence, "method":"Resposta extrativa com evidências"}
