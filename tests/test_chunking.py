from linguai.chunking import split_into_chunks

def test_chunking_returns_multiple_chunks():
    text=" ".join([f"Esta é a frase número {i} sobre processamento de linguagem natural." for i in range(1,15)])
    chunks=split_into_chunks(text,max_words=35,overlap_sentences=1)
    assert len(chunks)>1
    assert all(x.strip() for x in chunks)

def test_empty_input():
    assert split_into_chunks("") == []
