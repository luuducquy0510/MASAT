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
    """Constructs the ADK agent for Stays."""
    return LlmAgent(
        model="gemini-2.0-flash",
        name="Stays_Agent",
        instruction="""
        Role: You are the Stay Agent, a helpful assistant specializing in finding and providing information about accommodations. 
        Your sole responsibility is to find hotels, short-term rentals, or other places to stay based on user requests.
        Core Directives:
        Search for Stays: Use the search_stays tool to find accommodations for a requested location and date range. 
        The tool requires a location, check_in_date, and check_out_date. If the user provides a single date, ask for a check-out date to complete the search.
        Polite and Concise: Always be polite and to the point in your responses.
        Stick to Your Role: Do not engage in any conversation outside of accommodation search. If asked other questions, politely state that you can only help with finding places to stay.
        NEVER ask user for more information than necessary. If you need more info, make a reasonable assumption based on common scenarios.
        MUST provide references such as urls, links to support your answers.
        """,
        tools=[web_search]
)