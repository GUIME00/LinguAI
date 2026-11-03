# LinguAI — NLP local para documentos

Plataforma modular para importar documentos, resumir, pesquisar, responder perguntas com evidências, extrair entidades, classificar textos e manter histórico. Não usa APIs pagas. Modelos pré-treinados podem ser baixados uma vez e executados localmente.

## Requisitos
Windows 10/11 64-bit. Python 3.11 ou 3.12 recomendado. 8 GB RAM como ponto de partida; 16 GB recomendado para Transformers. Python 3.13 pode ter incompatibilidades com wheels do PyTorch.

## Instalação (PowerShell)
Na pasta do projeto:
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python -m spacy download pt_core_news_sm
```
Se `py -3.12` não existir, instale Python 3.12 ou tente `py -3.11`. Se a instalação de `torch` falhar, use o seletor oficial: https://pytorch.org/get-started/locally/

## Executar
```powershell
python -m streamlit run app.py
```
Abra `http://localhost:8501` se o navegador não abrir automaticamente.

## Testes
```powershell
python -m pytest -q
```

## Modelos locais configurados
- Embeddings: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Sumarização abstrativa: `csebuetnlp/mT5_multilingual_XLSum`
- QA: `deepset/xlm-roberta-base-squad2`
- Zero-shot: `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`
- Entidades: spaCy `pt_core_news_sm`

Edite `.env` para trocar modelos. Na primeira execução, os modelos serão baixados do Hugging Face e armazenados em cache; depois, `LINGUAI_OFFLINE=1` exige que já estejam no cache.

## Funcionalidades e limites
- TXT, MD, PDF com texto embutido e DOCX.
- Sumarização extrativa TF-IDF pronta sem modelo neural; abstrativa opcional por Transformer.
- Busca por embeddings; fallback lexical TF-IDF se o modelo não carregar.
- QA recupera trechos e responde com evidências; modo Transformer opcional.
- NER com spaCy; fallback detecta e-mails, URLs, datas e valores monetários.
- Classificação zero-shot local.
- Histórico SQLite em `data/linguai.db`.

PDFs digitalizados exigem OCR, não incluído nesta versão. Resumos e respostas de modelos podem omitir ou alterar detalhes; revise-os. Documentos ficam localmente no banco SQLite. Proteja a pasta `data` se houver conteúdo confidencial.
