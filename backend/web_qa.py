from backend.llm import get_llm
from backend.web_search import web_search
from langchain_core.prompts import ChatPromptTemplate


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


def create_web_prompt():
    return ChatPromptTemplate.from_messages(
        [
            ("system", WEB_SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )


def get_response_text(response):
    """
    GeminiLLM returns a string.
    ChatOllama can return an AIMessage.
    This function supports both.
    """

    if isinstance(response, str):
        return response.strip()

    if hasattr(response, "content"):
        return str(response.content).strip()

    return str(response).strip()


def ask_web(question, max_results=5):

    # -----------------------------------------
    # STEP 1: Search the web
    # -----------------------------------------

    results = web_search(
        question,
        max_results=max_results,
    )

    if not results:
        return {
            "answer": (
                "I couldn't find useful information "
                "from the web right now."
            ),
            "sources": [],
        }

    # -----------------------------------------
    # STEP 2: Build search context
    # -----------------------------------------

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

    # -----------------------------------------
    # STEP 3: Create prompt
    # -----------------------------------------

    prompt = create_web_prompt()

    # -----------------------------------------
    # STEP 4: Get LLM
    # -----------------------------------------

    llm = get_llm()

    # -----------------------------------------
    # STEP 5: Create chain
    # -----------------------------------------

    chain = prompt | llm

    # -----------------------------------------
    # STEP 6: Generate answer
    # -----------------------------------------

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    # -----------------------------------------
    # STEP 7: Convert response to text
    # -----------------------------------------

    answer = get_response_text(
        response
    )

    # -----------------------------------------
    # STEP 8: Prepare sources
    # -----------------------------------------

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

    # -----------------------------------------
    # STEP 9: Return answer + sources
    # -----------------------------------------

    return {
        "answer": answer,
        "sources": sources,
    }