from datetime import date, datetime, timedelta

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StdioServerParameters
import json
import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch


load_dotenv()

SCRIPT_PATH = os.path.abspath("../mcp_tools.py")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # Hoặc gán trực tiếp nếu cần

def web_search(query: str, max_results: int = 3) -> list[dict]:
    """
    Perform a Tavily search and return a list of results.
    Each result includes the title, snippet, and URL.
    """
    tavily_search_tool = TavilySearch(max_results=max_results, topic="general")
    results = tavily_search_tool.invoke({"query": query})

    return results

def create_agent() -> LlmAgent:
    """Constructs the ADK agent for Activities."""
    return LlmAgent(
        model="gemini-2.0-flash",
        name="Activities_Agent",
        instruction="""
            Role: You are the Activities Plan Agent. You provide researched activity plans based on user requests.
            Tools: You are equipped with a web search tool.
            Directives:
            Search: Use the web search tool to find relevant, up-to-date information on the user's requested activity.
            Plan: Create a clear, detailed activity plan. Include locations, costs, hours, and tips.
            Format: Use headings and bullet points for readability. Be concise and direct.
            Engage: If the request is too vague, ask for more details like location, interests, or budget.
            Tone: Helpful, enthusiastic, and to the point.
            NEVER ask user for more information than necessary. If you need more info, make a reasonable assumption based on common scenarios.
            MUST provide references such as urls, links to support your answers.
        """,
        tools=[web_search]
)