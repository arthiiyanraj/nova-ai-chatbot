from backend.vectorstore import get_vector_store


# =========================================================
# SEARCH PDF
# =========================================================

def search_pdf(
    question,
    user_id,
    document_id,
    top_k=3,
):

    # -----------------------------------------------------
    # GET THE SELECTED PDF'S VECTOR STORE
    # -----------------------------------------------------

    vector_store = get_vector_store(
        user_id,
        document_id,
    )

    # -----------------------------------------------------
    # SEARCH SIMILAR CONTENT
    # -----------------------------------------------------

    documents = vector_store.similarity_search(
        question,
        k=top_k,
    )

    return documents