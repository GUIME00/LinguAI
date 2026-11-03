from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path(os.getenv("LINGUAI_DATA_DIR", "data"))
    embedding_model: str = os.getenv("LINGUAI_EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    summary_model: str = os.getenv("LINGUAI_SUMMARY_MODEL", "csebuetnlp/mT5_multilingual_XLSum")
    qa_model: str = os.getenv("LINGUAI_QA_MODEL", "deepset/xlm-roberta-base-squad2")
    zero_shot_model: str = os.getenv("LINGUAI_ZERO_SHOT_MODEL", "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
    spacy_model: str = os.getenv("LINGUAI_SPACY_MODEL", "pt_core_news_sm")
    offline: bool = os.getenv("LINGUAI_OFFLINE", "0") == "1"
    @property
    def database_path(self):
        return self.data_dir / "linguai.db"

settings = Settings()
