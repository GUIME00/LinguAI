import hashlib
import streamlit as st
import pandas as pd
from linguai.config import settings
from linguai.database import Database
from linguai.ingestion import extract_uploaded_file
from linguai.services.summarizer import Summarizer
from linguai.services.search import SearchService
from linguai.services.question_answering import QuestionAnsweringService
from linguai.services.entities import EntityService
from linguai.services.classifier import ClassificationService

st.set_page_config(page_title="LinguAI", page_icon="🧠", layout="wide")
settings.data_dir.mkdir(parents=True, exist_ok=True)
db=Database(settings.database_path)
summarizer=Summarizer()
searcher=SearchService(settings.embedding_model,settings.offline)
qa=QuestionAnsweringService(searcher,settings.qa_model,settings.offline)
entities=EntityService(settings.spacy_model,settings.offline)

st.title("🧠 LinguAI")
st.caption("Plataforma local de análise e compreensão de documentos com NLP")
with st.sidebar:
    st.subheader("Configurações")
    st.write("Execução: local · Banco: SQLite")
    st.write("Modo offline:", "ativado" if settings.offline else "desativado")
    page=st.radio("Navegação",["Documentos","Analisar documento","Histórico","Sobre"])

if page=="Documentos":
    st.header("Biblioteca de documentos")
    upload=st.file_uploader("Importar documento",type=["txt","md","pdf","docx"])
    if upload:
        try:
            text,name=extract_uploaded_file(upload)
            digest=hashlib.sha256(text.encode("utf-8")).hexdigest()
            doc_id=db.add_document(name,text,digest)
            st.success(f"Documento registrado · ID {doc_id} · {len(text):,} caracteres")
        except Exception as exc:
            st.error(f"Falha ao importar: {exc}")
    docs=db.list_documents()
    if docs: st.dataframe(pd.DataFrame(docs),use_container_width=True,hide_index=True)
    else: st.info("Importe seu primeiro documento para começar.")

elif page=="Analisar documento":
    st.header("Análise de documento")
    docs=db.list_documents()
    if not docs: st.warning("Importe um documento primeiro.")
    else:
        opts={f'{d["id"]} — {d["name"]} ({d["chars"]:,} caracteres)':d["id"] for d in docs}
        selected=st.selectbox("Documento",list(opts))
        doc=db.get_document(opts[selected])
        tabs=st.tabs(["Resumo","Busca semântica","Perguntas e respostas","Entidades","Classificação"])
        with tabs[0]:
            mode=st.radio("Método",["Extrativo (leve, pronto para uso)","Transformer abstrativo (mais pesado)"],horizontal=True)
            ratio=st.slider("Proporção do resumo extrativo",0.10,0.60,0.25,0.05)
            if st.button("Gerar resumo"):
                try:
                    with st.spinner("Gerando resumo..."):
                        if mode.startswith("Extrativo"):
                            result=summarizer.extractive(doc["content"],ratio); method="TF-IDF extrativo"
                        else:
                            result=summarizer.abstractive(doc["content"],settings.summary_model,settings.offline); method=settings.summary_model
                    db.add_summary(doc["id"],method,result); st.session_state["summary_result"]=result
                except Exception as exc: st.error(f"Erro no resumo: {exc}")
            if st.session_state.get("summary_result"):
                st.text_area("Resumo",st.session_state["summary_result"],height=230)
                st.download_button("Baixar resumo",st.session_state["summary_result"],"linguai_resumo.txt")
        with tabs[1]:
            query=st.text_input("O que deseja encontrar?")
            neural=st.checkbox("Usar embeddings multilíngues (requer modelo local)",value=True)
            if st.button("Pesquisar") and query.strip():
                with st.spinner("Buscando trechos..."):
                    results=searcher.search(doc["content"],query,5,neural)
                for i,item in enumerate(results,1):
                    st.markdown(f'**Trecho {i} · score {item["score"]:.3f} · {item["method"]}**')
                    st.write(item["text"]); st.divider()
                if not results: st.info("Nenhum trecho relevante encontrado.")
        with tabs[2]:
            question=st.text_input("Faça uma pergunta sobre o documento")
            transformer_qa=st.checkbox("Usar modelo Transformer de QA (mais pesado)",value=False)
            if st.button("Responder") and question.strip():
                with st.spinner("Localizando evidências..."):
                    result=qa.answer(doc["content"],question,transformer_qa)
                st.markdown("**Resposta**"); st.write(result["answer"])
                st.markdown("**Evidências do documento**")
                for item in result["evidence"]: st.info(item)
                db.add_question(doc["id"],question,result["answer"],"\\n---\\n".join(result["evidence"]))
        with tabs[3]:
            if st.button("Extrair entidades"):
                with st.spinner("Analisando entidades..."): found=entities.extract(doc["content"])
                if found: st.dataframe(pd.DataFrame(found),use_container_width=True,hide_index=True)
                else: st.info("Nenhuma entidade encontrada. Instale o modelo spaCy de português para reconhecimento completo.")
        with tabs[4]:
            labels=st.text_input("Categorias separadas por vírgula","tecnologia, educação, saúde, economia, meio ambiente")
            if st.button("Classificar"):
                try:
                    with st.spinner("Classificando localmente..."):
                        result=ClassificationService(settings.zero_shot_model,settings.offline).classify(doc["content"],labels.split(","))
                    st.dataframe(pd.DataFrame(result),use_container_width=True,hide_index=True)
                except Exception as exc: st.error(f"Falha na classificação: {exc}")

elif page=="Histórico":
    st.header("Histórico")
    docs=db.list_documents()
    if not docs: st.info("Nenhum documento cadastrado.")
    else:
        opts={f'{d["id"]} — {d["name"]}':d["id"] for d in docs}
        doc_id=db_id=opts[st.selectbox("Documento",list(opts))]
        history=db.history(doc_id)
        a,b=st.columns(2)
        with a:
            st.subheader("Resumos")
            for item in history["summaries"]:
                with st.expander(f'{item["created_at"]} · {item["method"]}'): st.write(item["summary"])
        with b:
            st.subheader("Perguntas")
            for item in history["questions"]:
                with st.expander(f'{item["created_at"]} · {item["question"]}'):
                    st.write(item["answer"]); st.caption("Evidências"); st.write(item["evidence"])
else:
    st.header("Sobre o LinguAI")
    st.write("Plataforma de NLP para documentos: sumarização, busca por embeddings, QA com evidências, NER e classificação zero-shot.")
    st.info("Documentos e histórico ficam em SQLite local. Na primeira execução, modelos podem ser baixados e armazenados em cache. PDFs digitalizados exigem OCR, ainda não incluído.")
