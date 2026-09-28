from backend.llm import get_llm
from backend.prompts import create_chat_prompt

from backend.memory import (
    save_memory,
    get_memories,
    build_chat_history,
    detect_memory,
)

from backend.pdf_qa import ask_pdf
from backend.web_qa import ask_web
from backend.router import route_question

from backend.response_utils import get_response_text


def generate_answer(
    question,
    user_id,
    chat_messages,
    active_pdf_id=None,
):
    """
    Generate a NOVA answer using the existing
    GENERAL / WEB / PDF routing system.

    Returns:
        {
            "answer": str,
            "route": str,
            "web_sources": list
        }
    """

    question = question.strip()

    if not question:
        return {
            "answer": "",
            "route": "GENERAL",
            "web_sources": [],
        }

    # ========================================================
    # ROUTE
    # ========================================================

    route = route_question(question)

    web_sources = []

    # ========================================================
    # PDF
    # ========================================================

    if route == "PDF":

        if active_pdf_id:

            answer = ask_pdf(
                question,
                user_id,
                active_pdf_id,
                top_k=5,
            )

        else:

            answer = (
                "Please upload a PDF first "
                "or select an uploaded document."
            )

            route = "GENERAL"

    # ========================================================
    # WEB
    # ========================================================

    elif route == "WEB":

        web_result = ask_web(
            question,
            max_results=6,
        )

        answer = web_result["answer"]

        web_sources = web_result["sources"]

    # ========================================================
    # GENERAL
    # ========================================================

    else:

        llm = get_llm()

        prompt = create_chat_prompt()

        chain = prompt | llm

        # ----------------------------------------------------
        # Chat history
        # ----------------------------------------------------

        chat_history = build_chat_history(
            chat_messages
        )

        # ----------------------------------------------------
        # Long-term memory
        # ----------------------------------------------------

        memories = get_memories(
            user_id
        )

        if memories:

            memory_text = "\n".join(
                f"- {memory}"
                for memory in memories
            )

        else:

            memory_text = (
                "No saved memories."
            )

        # ----------------------------------------------------
        # Generate answer
        # ----------------------------------------------------

        response = chain.invoke(
            {
                "memories": memory_text,
                "chat_history": chat_history,
                "question": question,
            }
        )

        answer = get_response_text(
            response
        )

    # ========================================================
    # SAFETY
    # ========================================================

    if not answer:

        answer = (
            "I couldn't generate an answer "
            "right now. Please try again."
        )

    # ========================================================
    # MEMORY
    # ========================================================

    detected_memory = detect_memory(
        question
    )

    if detected_memory:

        save_memory(
            user_id,
            detected_memory,
        )

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "answer": answer,
        "route": route,
        "web_sources": web_sources,
    }