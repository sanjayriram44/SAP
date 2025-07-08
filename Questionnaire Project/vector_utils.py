# vector_utils.py

import os
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.document_loaders import Docx2txtLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.models import embeddings_instance

DOCS_FOLDER = "docs"
VECTOR_DB_PATH = "vectorstore"

def load_documents():
    """Loads .docx and .pdf documents from the docs folder."""
    loaders = []
    for filename in os.listdir(DOCS_FOLDER):
        file_path = os.path.join(DOCS_FOLDER, filename)
        if filename.endswith(".docx"):
            loaders.append(Docx2txtLoader(file_path))
        elif filename.endswith(".pdf"):
            loaders.append(PyMuPDFLoader(file_path))

    documents = []
    for loader in loaders:
        try:
            documents.extend(loader.load())
        except Exception as e:
            print(f"Failed to load {loader}: {e}")
    return documents

def create_or_load_vectorstore(documents):
    """Creates or loads the Chroma vectorstore."""
    if os.path.exists(VECTOR_DB_PATH):
        return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings_instance)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    split_docs = text_splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings_instance,
        persist_directory=VECTOR_DB_PATH
    )
    return vectorstore

def build_rag_context(k: int = 4, query: str = "SAP Ariba sourcing discovery questions") -> str:
    """
    Load documents, create/load vectorstore, and return RAG context for a query.
    """
    documents = load_documents()
    vectorstore = create_or_load_vectorstore(documents)
    retriever = vectorstore.as_retriever(search_type="similarity", k=k)
    chunks = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in chunks)
