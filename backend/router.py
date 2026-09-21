from backend.llm import get_llm
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
- General questions
- Questions that do not need current information

PDF:
- Questions about an uploaded PDF
- Questions about a document
- Questions about a report
- Questions about a resume
- Questions about a file
- User says:
  my PDF
  uploaded PDF
  this PDF
  this document
  uploaded document
  this report
  this file
- User asks what a document contains
- User asks to summarize a document
- User asks about information inside a document

WEB:
- Latest information
- Current information
- Today's information
- News
- Current events
- Current prices
- Current versions
- Recent releases
- Live or changing information
- User explicitly asks to search the web

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
            ("system", ROUTER_SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )


def detect_pdf_question(question):
    text = question.lower().strip()

    pdf_keywords = [
        "this document",
        "the document",
        "my document",
        "uploaded document",
        "this pdf",
        "the pdf",
        "my pdf",
        "uploaded pdf",
        "this report",
        "the report",
        "my report",
        "uploaded report",
        "this file",
        "the file",
        "my file",
        "uploaded file",
        "document about",
        "pdf about",
        "report about",
        "summarize this document",
        "summarise this document",
        "summarize the document",
        "summarise the document",
        "summarize this pdf",
        "summarise this pdf",
        "summarize the pdf",
        "summarise the pdf",
        "according to the document",
        "according to this document",
        "according to the pdf",
        "according to this pdf",
        "from the document",
        "from this document",
        "from the pdf",
        "from this pdf",
        "in the document",
        "in this document",
        "in the pdf",
        "in this pdf",
        "what does this document",
        "what does the document",
        "what is this document",
        "what is the document",
    ]

    for keyword in pdf_keywords:
        if keyword in text:
            return True

    return False


def detect_web_question(question):
    text = question.lower().strip()

    web_keywords = [
        "latest",
        "current",
        "today",
        "today's",
        "recent",
        "news",
        "live",
        "search the web",
        "search online",
        "search internet",
        "web search",
        "current price",
        "latest price",
        "latest version",
        "current version",
        "recent release",
        "latest release",
    ]

    for keyword in web_keywords:
        if keyword in text:
            return True

    return False


def get_response_text(response):
    """
    Convert different LangChain response types
    into plain text.

    GeminiLLM returns a string.
    ChatOllama can return an AIMessage.
    """

    if isinstance(response, str):
        return response.strip()

    if hasattr(response, "content"):
        return str(response.content).strip()

    return str(response).strip()


def route_question(question):

    # -----------------------------------------
    # STEP 1: Check PDF
    # -----------------------------------------

    if detect_pdf_question(question):
        return "PDF"

    # -----------------------------------------
    # STEP 2: Check WEB
    # -----------------------------------------

    if detect_web_question(question):
        return "WEB"

    # -----------------------------------------
    # STEP 3: Ask LLM router
    # -----------------------------------------

    llm = get_llm()

    prompt = create_router_prompt()

    chain = prompt | llm

    response = chain.invoke(
        {
            "question": question,
        }
    )

    # -----------------------------------------
    # STEP 4: Convert response to text
    # -----------------------------------------

    raw_route = get_response_text(response).upper()

    # -----------------------------------------
    # STEP 5: Clean router response
    # -----------------------------------------

    if "PDF" in raw_route:
        return "PDF"

    if "WEB" in raw_route:
        return "WEB"

    if "GENERAL" in raw_route:
        return "GENERAL"

    # -----------------------------------------
    # STEP 6: Safe fallback
    # -----------------------------------------

    return "GENERAL"