from langchain_ollama import OllamaEmbeddings


EMBEDDING_MODEL = "nomic-embed-text"


def get_embeddings():
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL
    )