def get_response_text(response):
    """
    Convert different LangChain/provider responses
    into normal text.

    GeminiLLM -> str
    ChatOllama -> AIMessage
    """

    if response is None:
        return ""

    if isinstance(response, str):
        return response.strip()

    content = getattr(response, "content", None)

    if content is not None:
        return str(content).strip()

    return str(response).strip()