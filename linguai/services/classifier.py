class ClassificationService:
    def __init__(self, model_name, offline=False):
        self.model_name, self.offline, self._pipeline = model_name, offline, None
    def classify(self, text, labels):
        labels=[x.strip() for x in labels if x.strip()]
        if len(labels)<2:
            raise ValueError("Informe pelo menos duas categorias.")
        from transformers import pipeline
        if self._pipeline is None:
            self._pipeline=pipeline("zero-shot-classification",model=self.model_name,tokenizer=self.model_name,device=-1,model_kwargs={"local_files_only":self.offline})
        result=self._pipeline(text[:5000],candidate_labels=labels,multi_label=False)
        return [{"label":l,"score":float(s)} for l,s in zip(result["labels"],result["scores"])]
