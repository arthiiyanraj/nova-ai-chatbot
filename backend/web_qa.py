from backend.llm import get_llm
from backend.web_search import web_search
from langchain_core.prompts import ChatPromptTemplate


# =========================================================
# WEB SEARCH PROMPT
# =========================================================

WEB_SYSTEM_PROMPT = """
You are NOVA, a friendly general-purpose AI assistant.

Answer the user's question using the web search results provided below.

Rules:

1. Use the search results as the main source of current information.
2. Do not invent information.
3. If the search results do not contain enough information, say so clearly.
4. Give a direct and easy-to-understand answer.
5. Answer naturally like a helpful human.
6. Do not mention internal implementation details.

WEB SEARCH RESULTS:

{context}
"""


# =========================================================
# CREATE WEB PROMPT
# =========================================================

def create_web_prompt():

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                WEB_SYSTEM_PROMPT,
            ),
            (
                "human",
                "{question}",
            ),
        ]
    )


# =========================================================
# ASK WEB
# =========================================================

def ask_web(
    question,
    max_results=5,
):

    # -----------------------------------------------------
    # SEARCH WEB
    # -----------------------------------------------------

    results = web_search(
        question,
        max_results=max_results,
    )


    # -----------------------------------------------------
    # NO RESULTS
    # -----------------------------------------------------

    if not results:

        return {
            "answer": (
                "I couldn't find useful information "
                "from the web right now."
            ),
            "sources": [],
        }


    # -----------------------------------------------------
    # BUILD CONTEXT
    # -----------------------------------------------------

    context_parts = []


    for index, result in enumerate(
        results,
        start=1,
    ):

        title = result.get(
            "title",
            "",
        )

        body = result.get(
            "body",
            "",
        )

        href = result.get(
            "href",
            "",
        )

        context_parts.append(
            f"""
Source {index}

Title:
{title}

Information:
{body}

URL:
{href}
"""
        )


    context = "\n".join(
        context_parts
    )


    # -----------------------------------------------------
    # CREATE PROMPT
    # -----------------------------------------------------

    prompt = create_web_prompt()


    # -----------------------------------------------------
    # LOAD LLM
    # -----------------------------------------------------

    llm = get_llm()


    # -----------------------------------------------------
    # CREATE CHAIN
    # -----------------------------------------------------

    chain = prompt | llm


    # -----------------------------------------------------
    # CALL LLM
    # -----------------------------------------------------

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )


    # -----------------------------------------------------
    # COLLECT SOURCES
    # -----------------------------------------------------

    sources = []

    for result in results:

        title = result.get(
            "title",
            "",
        )

        href = result.get(
            "href",
            "",
        )

        if href:

            sources.append(
                {
                    "title": title,
                    "url": href,
                }
            )


    # -----------------------------------------------------
    # RETURN ANSWER + SOURCES
    # -----------------------------------------------------

    return {
        "answer": response.content,
        "sources": sources,
    }