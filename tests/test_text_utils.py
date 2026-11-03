from linguai.text_utils import normalize_text, split_sentences, word_count

def test_normalize_text():
    assert normalize_text("  Olá   mundo\r\n\r\n\r\nNLP ") == "Olá mundo\n\nNLP"

def test_split_sentences():
    assert len(split_sentences("NLP é útil. Vamos estudar! Texto em português?")) == 3

def test_word_count():
    assert word_count("NLP é muito interessante!") == 4
