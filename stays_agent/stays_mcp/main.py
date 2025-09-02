import os
from fastmcp import FastMCP
from langchain_tavily import TavilySearch
from dotenv import load_dotenv


load_dotenv()
mcp = FastMCP()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  

@mcp.tool()
def web_search(query: str, max_results: int = 3) -> list[dict]:
    """
    Perform a Tavily search and return a list of results.
    Each result includes the title, snippet, and URL.
    """
    tavily_search_tool = TavilySearch(max_results=max_results, topic="general")
    results = tavily_search_tool.invoke({"query": query})

    return results


if __name__ == "__main__":
    mcp.run(transport="stdio")