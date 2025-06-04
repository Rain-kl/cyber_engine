from .ext import mcp


@mcp.tool()
async def search_web(
        query: str,
):
    """ Perform a web search based on the provided query.

    Args:
        query: The search query to perform on the web (e.g. "latest news", "weather today")
    """

    return f"Performing web search for: {query}"  # Placeholder response, implement actual search logic here
