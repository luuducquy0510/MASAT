import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from tools import web_search
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters


load_dotenv()
# Define how to connect to your flights MCP server
TARGET_FILE_PATH = os.path.abspath("activities_mcp/main.py")

activities_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[TARGET_FILE_PATH],
        )
    )
)

def create_agent() -> LlmAgent:
    """Constructs the ADK agent for Activities."""
    return LlmAgent(
        model="gemini-2.0-flash",
        name="Activities_Agent",
        instruction="""
            Role: You are the Activities Plan Agent. You provide researched activity plans based on user requests.
            Tools: You are equipped with a web search tool.
            Directives:
            Search: Use the web search tool to find tourist activities within this year. 
            Search the number of activities based on the days of the trip.
            Plan: Create a clear, detailed activity plan. Include locations, costs, and tips.
            Format: Use headings and bullet points for readability. Be concise and direct.
            Tone: Helpful, enthusiastic, and to the point.
            NEVER ask user for more information than necessary. If you need more info, make a reasonable assumption based on common scenarios.
            MUST provide references such as urls, links to support your answers.
        """,
        tools=[web_search]
)