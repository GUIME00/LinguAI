import re

class EntityService:
    def __init__(self, model_name, offline=False):
        self.model_name, self.offline, self._nlp = model_name, offline, None
    def _load(self):
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load(self.model_name)
            except (ImportError, OSError):
                self._nlp = False
        return self._nlp if self._nlp is not False else None
    def extract(self, text):
        nlp = self._load()
        if nlp:
            doc = nlp(text[:1000000])
            return [{"text":e.text,"label":e.label_,"start":e.start_char,"end":e.end_char} for e in doc.ents]
        patterns = [("EMAIL",r"\\b[\\w.+-]+@[\\w.-]+\\.[A-Za-z]{2,}\\b"),("URL",r"https?://[^\\s]+"),("DATE",r"\\b\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}\\b"),("MONEY",r"\\bR\\$\\s?\\d+(?:[.,]\\d{2})?\\b")]
        out=[]
        for label,pattern in patterns:
            for m in re.finditer(pattern,text):
                out.append({"text":m.group(),"label":label,"start":m.start(),"end":m.end()})
        return sorted(out,key=lambda x:x["start"])
