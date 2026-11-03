import pytest
from linguai.services.summarizer import Summarizer

def test_extractive_summary_selects_original_sentences():
    text=("A inteligência artificial transforma a educação. "
          "Escolas usam plataformas digitais para apoiar estudantes. "
          "Professores continuam essenciais na aprendizagem. "
          "A privacidade dos dados precisa ser protegida. "
          "A formação docente é importante para o uso responsável.")
    result=Summarizer().extractive(text,0.4)
    assert result
    assert all(sentence in text for sentence in result.split(". ") if sentence)

def test_invalid_ratio():
    with pytest.raises(ValueError):
        Summarizer().extractive("Texto de teste.",0)
