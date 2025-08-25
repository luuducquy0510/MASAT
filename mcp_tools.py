from fastmcp import FastMCP
from langchain_tavily import TavilySearch
import requests
# from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv


load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # Hoặc gán trực tiếp nếu cần
mcp = FastMCP("Tavily MCP Server")

@mcp.tool()
def web_search(query: str, max_results: int = 3) -> list[dict]:
    """
    Perform a Tavily search and return a list of results.
    Each result includes the title, snippet, and URL.
    """
    tavily_search_tool = TavilySearch(max_results=max_results, topic="general")
    results = tavily_search_tool.invoke({"query": query})

    return results

# @mcp.tool()
# def fetch_page_content(url: str) -> str:
#     """
#     Fetch and return the textual content of the specified URL.
#     """
#     try:
#         response = requests.get(url, timeout=60)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, "html.parser")
#         paragraphs = soup.find_all("p")
#         text_content = "\n".join(p.get_text() for p in paragraphs if p.get_text())
#         return text_content.strip()
#     except Exception as e:
#         return f"Error fetching content from {url}: {e}"
if __name__ == "__main__":
    mcp.run()