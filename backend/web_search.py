from ddgs import DDGS


def web_search(query, max_results=6):
    """
    Search the web using DuckDuckGo.

    Returns:
        list[dict]
    """

    results = []

    try:

        with DDGS() as ddgs:

            search_results = ddgs.text(
                query,
                max_results=max_results,
            )

            for result in search_results:

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

                if not title and not body:
                    continue

                results.append(
                    {
                        "title": title.strip(),
                        "body": body.strip(),
                        "href": href.strip(),
                    }
                )

    except Exception as error:

        print(
            f"Web search error: {error}"
        )

    return results