from backend.llm import get_llm
from backend.retriever import search_pdf
from backend.rag_prompt import create_rag_prompt
from backend.response_utils import get_response_text


def ask_pdf(
    question,
    user_id,
    document_id,
    top_k=5,
):

    documents = search_pdf(
        question,
        user_id,
        document_id,
        top_k=top_k,
    )

    if not documents:
        return (
            "I couldn't find relevant information "
            "in your uploaded PDF."
        )

    context = "\n\n".join(
        document.page_content
        for document in documents
        if document.page_content
    )

    if not context.strip():
        return (
            "I couldn't find readable information "
            "in your uploaded PDF."
        )

    prompt = create_rag_prompt()

    llm = get_llm()

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    answer = get_response_text(response)

    if not answer:
        return (
            "I couldn't generate an answer "
            "from the uploaded PDF."
        )

    return answer