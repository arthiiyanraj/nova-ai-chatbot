from ddgs import DDGS


# =========================================================
# WEB SEARCH
# =========================================================

def web_search(query, max_results=5):
    """
    Search the web and return search results.
    """

    results = []

    try:

        with DDGS() as ddgs:

            search_results = ddgs.text(
                query,
                max_results=max_results,
            )

            for result in search_results:

                results.append(
                    {
                        "title": result.get(
                            "title",
                            "",
                        ),
                        "body": result.get(
                            "body",
                            "",
                        ),
                        "href": result.get(
                            "href",
                            "",
                        ),
                    }
                )

    except Exception as error:

        print(
            f"Web search error: {error}"
        )

    return results