import os

from tavily import TavilyClient

from .ext import mcp

tavily_api_key = os.getenv("TAVILY_API_KEY", None)

@mcp.tool()
async def search_web(
        query: str,
):
    """Perform a web search based on the provided query.

    Args:
        query: The search query to perform on the web (e.g. "latest news", "weather today")
    """
    tavily_client = TavilyClient(api_key=tavily_api_key)
    response = tavily_client.search(query)
    return f"{response}"