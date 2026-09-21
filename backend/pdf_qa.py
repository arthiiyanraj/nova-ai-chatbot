from backend.llm import get_llm
from backend.retriever import search_pdf
from backend.rag_prompt import create_rag_prompt


# =========================================================
# ASK QUESTION FROM PDF
# =========================================================

def ask_pdf(
    question,
    user_id,
    document_id,
    top_k=3,
):

    # -----------------------------------------------------
    # SEARCH RELEVANT PDF CHUNKS
    # -----------------------------------------------------

    documents = search_pdf(
        question,
        user_id,
        document_id,
        top_k=top_k,
    )

    # -----------------------------------------------------
    # NO RELEVANT CONTENT
    # -----------------------------------------------------

    if not documents:

        return (
            "I couldn't find relevant information "
            "in your uploaded PDF."
        )

    # -----------------------------------------------------
    # BUILD PDF CONTEXT
    # -----------------------------------------------------

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    # -----------------------------------------------------
    # CREATE RAG PROMPT
    # -----------------------------------------------------

    prompt = create_rag_prompt()

    # -----------------------------------------------------
    # LOAD LOCAL LLM
    # -----------------------------------------------------

    llm = get_llm()

    # -----------------------------------------------------
    # CREATE LANGCHAIN CHAIN
    # -----------------------------------------------------

    chain = prompt | llm

    # -----------------------------------------------------
    # SEND CONTEXT + QUESTION TO LLM
    # -----------------------------------------------------

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    # -----------------------------------------------------
    # RETURN ANSWER
    # -----------------------------------------------------

    return response.content