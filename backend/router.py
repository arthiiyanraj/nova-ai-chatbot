from backend.llm import get_llm
from backend.response_utils import get_response_text

from langchain_core.prompts import ChatPromptTemplate


ROUTER_SYSTEM_PROMPT = """
You are the routing system of NOVA AI.

Choose exactly ONE route:

GENERAL
PDF
WEB

GENERAL:
- Casual conversation
- Greetings
- Programming
- Learning
- Explanations
- Writing
- General knowledge
- Everyday questions

PDF:
- Questions about an uploaded PDF
- Questions about a document
- Questions about a report
- Questions about a resume
- Questions about an uploaded file

WEB:
- Latest information
- Current information
- Today's information
- Recent information
- News
- Current events
- Current prices
- Current versions
- Current office holders
- Government information
- Political current facts
- Recent releases
- Live information
- Explicit web searches

Return ONLY:

GENERAL

or

PDF

or

WEB
"""


def create_router_prompt():

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                ROUTER_SYSTEM_PROMPT,
            ),
            (
                "human",
                "{question}",
            ),
        ]
    )


def detect_pdf_question(question):

    text = question.lower().strip()

    pdf_keywords = [

        "this pdf",
        "the pdf",
        "my pdf",
        "uploaded pdf",

        "this document",
        "the document",
        "my document",
        "uploaded document",

        "this report",
        "the report",
        "my report",
        "uploaded report",

        "this file",
        "the file",
        "my file",
        "uploaded file",

        "from the pdf",
        "from this pdf",
        "according to the pdf",
        "according to this pdf",

        "from the document",
        "from this document",
        "according to the document",
        "according to this document",

        "in the pdf",
        "in this pdf",
        "in the document",
        "in this document",

        "summarize this pdf",
        "summarise this pdf",

        "summarize the pdf",
        "summarise the pdf",

        "summarize this document",
        "summarise this document",

        "summarize the document",
        "summarise the document",

        "explain this pdf",
        "explain the pdf",

        "explain this document",
        "explain the document",

        "what does this pdf",
        "what does the pdf",

        "what does this document",
        "what does the document",
    ]

    return any(
        keyword in text
        for keyword in pdf_keywords
    )


def detect_web_question(question):

    text = question.lower().strip()

    web_keywords = [

        # Current / latest
        "latest",
        "current",
        "recent",
        "right now",
        "currently",

        # Date / time
        "today",
        "today's",
        "todays",
        "current date",
        "date today",
        "what date is it",
        "what is the date",

        # News
        "news",
        "breaking news",

        # Explicit web
        "search the web",
        "search online",
        "search internet",
        "web search",
        "search google",

        # Software
        "latest version",
        "current version",
        "latest release",
        "recent release",

        # Prices
        "current price",
        "latest price",
        "price today",

        # Government / office holders
        "who is the cm",
        "who is cm",
        "who is the chief minister",
        "chief minister of",

        "who is the prime minister",
        "prime minister of",

        "who is the president",
        "president of",

        "who is the governor",
        "governor of",

        "current government",
        "current government of",

        # Live information
        "live score",
        "live update",
        "live updates",

        # Weather
        "weather today",
        "weather now",
        "current weather",
    ]

    return any(
        keyword in text
        for keyword in web_keywords
    )


def route_question(question):

    # PDF has highest priority.
    if detect_pdf_question(question):
        return "PDF"

    # Current/live information next.
    if detect_web_question(question):
        return "WEB"

    # LLM fallback.
    llm = get_llm()

    prompt = create_router_prompt()

    chain = prompt | llm

    response = chain.invoke(
        {
            "question": question,
        }
    )

    route = get_response_text(
        response
    ).upper()

    if route == "PDF":
        return "PDF"

    if route == "WEB":
        return "WEB"

    return "GENERAL"