import os
from langchain_chroma import Chroma
# from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from .llms import get_embedding_openai

# Configuration du modèle de génération d'embeddings
# embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
embedding_function = get_embedding_openai()


def get_chroma_db():
    return Chroma(
        persist_directory=os.getenv("CHROMA_DB_DIRECTORY", "chroma_db"),
        embedding_function=embedding_function
    )