from backend.llm import get_llm
from backend.web_search import web_search
from backend.response_utils import get_response_text

from langchain_core.prompts import ChatPromptTemplate


WEB_SYSTEM_PROMPT = """
You are NOVA, a friendly general-purpose AI assistant.

You are answering the user's question using web search results.

IMPORTANT:

The web search results are the source of truth for CURRENT information.

Do not answer current-information questions from your old model knowledge.

This includes:

- latest information
- current information
- today's information
- recent information
- news
- current office holders
- current government information
- current political information
- current software versions
- current prices
- recent releases
- live information

RULES:

1. Use the supplied search results.

2. Do not invent facts.

3. Do not assume that an old fact is still current.

4. Prefer official sources and reliable sources.

5. If the search results are insufficient,
   clearly say that the available search results
   do not provide enough information.

6. If sources disagree,
   explain the disagreement instead of inventing
   an answer.

7. Give the user a direct answer first.

8. Then provide a short explanation when useful.

9. Keep the answer simple and natural.

10. Do not mention internal implementation details.

11. Do not say that you personally browsed the internet.

12. For current government or political information,
    only use information supported by the supplied
    current search results.

WEB SEARCH RESULTS:

{context}
"""


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


def ask_web(
    question,
    max_results=6,
):

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

    context_parts = []

    for index, result in enumerate(
        results,
        start=1,
    ):

        context_parts.append(
            f"""
SOURCE {index}

TITLE:
{result["title"]}

INFORMATION:
{result["body"]}

URL:
{result["href"]}
"""
        )

    context = "\n".join(
        context_parts
    )

    prompt = create_web_prompt()

    llm = get_llm()

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    answer = get_response_text(
        response
    )

    if not answer:

        answer = (
            "I couldn't generate a reliable "
            "answer from the available web results."
        )

    sources = []

    for result in results:

        if result["href"]:

            sources.append(
                {
                    "title": result["title"],
                    "url": result["href"],
                }
            )

    return {
        "answer": answer,
        "sources": sources,
    }