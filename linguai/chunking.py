from linguai.text_utils import split_sentences

def split_into_chunks(text, max_words=220, overlap_sentences=1):
    if max_words < 20:
        raise ValueError("max_words deve ser pelo menos 20.")
    sentences = split_sentences(text)
    chunks, current, count = [], [], 0
    for sentence in sentences:
        size = len(sentence.split())
        if current and count + size > max_words:
            chunks.append(" ".join(current))
            current = current[-overlap_sentences:] if overlap_sentences else []
            count = sum(len(s.split()) for s in current)
        current.append(sentence)
        count += size
    if current:
        candidate = " ".join(current)
        if not chunks or candidate != chunks[-1]:
            chunks.append(candidate)
    return chunks
