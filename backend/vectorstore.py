from langchain_chroma import Chroma

from backend.embeddings import get_embeddings


# ============================================================
# VECTOR DATABASE PATH
# ============================================================

VECTOR_DB_PATH = "./data/chroma_db"


# ============================================================
# COLLECTION NAME
# ============================================================

def get_collection_name(
    user_id,
    document_id,
):

    return (
        f"nova_user_{user_id}_document_{document_id}"
    )


# ============================================================
# CREATE VECTOR STORE
# ============================================================

def create_vector_store(
    chunks,
    user_id,
    document_id,
):

    embeddings = get_embeddings()

    collection_name = get_collection_name(
        user_id,
        document_id,
    )

    vector_store = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=VECTOR_DB_PATH,
    )

    return vector_store


# ============================================================
# GET VECTOR STORE
# ============================================================

def get_vector_store(
    user_id,
    document_id,
):

    embeddings = get_embeddings()

    collection_name = get_collection_name(
        user_id,
        document_id,
    )

    vector_store = Chroma(
        collection_name=collection_name,
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings,
    )

    return vector_store


# ============================================================
# DELETE VECTOR STORE
# ============================================================

def delete_vector_store(
    user_id,
    document_id,
):

    collection_name = get_collection_name(
        user_id,
        document_id,
    )

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=collection_name,
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings,
    )

    vector_store.delete_collection()

    return True