from pathlib import Path
from pypdf import PdfReader
from docx import Document
from linguai.text_utils import normalize_text

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}

def extract_text(file_path):
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato não suportado: {suffix}")
    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8", errors="replace")
    elif suffix == ".pdf":
        text = "\\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    else:
        doc = Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        tables = [" | ".join(c.text.strip() for c in row.cells) for table in doc.tables for row in table.rows]
        text = "\\n".join(paragraphs + tables)
    result = normalize_text(text)
    if not result:
        raise ValueError("Não foi possível extrair texto. PDF digitalizado exige OCR.")
    return result


def extract_uploaded_file(uploaded_file):
    import tempfile
    from pathlib import Path

    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("Envie TXT, MD, PDF ou DOCX.")

    temp_path = None

    try:
        # Cria um arquivo temporário e fecha antes de tentar lê-lo.
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False
        ) as temp:
            temp.write(uploaded_file.getvalue())
            temp_path = temp.name

        # Agora o arquivo já está fechado e pode ser aberto no Windows.
        extracted_text = extract_text(temp_path)

        return extracted_text, uploaded_file.name

    finally:
        # Remove o arquivo temporário após a leitura.
        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink()
