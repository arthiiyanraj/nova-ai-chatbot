from backend.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate


# ============================================================
# ROUTER PROMPT
# ============================================================

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


# ============================================================
# CREATE ROUTER PROMPT
# ============================================================

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


# ============================================================
# RULE-BASED PDF DETECTION
# ============================================================

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


# ============================================================
# RULE-BASED WEB DETECTION
# ============================================================

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


# ============================================================
# MAIN ROUTER
# ============================================================

def route_question(question):

    # --------------------------------------------------------
    # STEP 1
    # Check PDF keywords first
    # --------------------------------------------------------

    if detect_pdf_question(question):

        return "PDF"


    # --------------------------------------------------------
    # STEP 2
    # Check Web keywords
    # --------------------------------------------------------

    if detect_web_question(question):

        return "WEB"


    # --------------------------------------------------------
    # STEP 3
    # Use LLM for remaining questions
    # --------------------------------------------------------

    llm = get_llm()

    prompt = create_router_prompt()

    chain = prompt | llm


    response = chain.invoke(
        {
            "question": question,
        }
    )


    raw_route = (
        response.content
        .strip()
        .upper()
    )


    # --------------------------------------------------------
    # STEP 4
    # Validate LLM result
    # --------------------------------------------------------

    if raw_route == "PDF":

        return "PDF"


    if raw_route == "WEB":

        return "WEB"


    if raw_route == "GENERAL":

        return "GENERAL"


    # --------------------------------------------------------
    # STEP 5
    # Safe default
    # --------------------------------------------------------

    return "GENERAL"