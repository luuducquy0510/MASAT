import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters


load_dotenv()
# Define how to connect to your flights MCP server
TARGET_FILE_PATH = os.path.abspath("stays_mcp/main.py")

stays_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[TARGET_FILE_PATH],
        )
    )
)

def create_agent() -> LlmAgent:
    """Constructs the ADK agent for Stays."""
    return LlmAgent(
        model="gemini-2.0-flash",
        name="Stays_Agent",
        instruction="""
        Role: You are the Stay Agent, a helpful assistant specializing in finding and providing information about accommodations. 
        Your sole responsibility is to find hotels, short-term rentals, or other places to stay based on user requests.
        Core Directives:
        Search for Stays: Use the web_search tool to find hotel information and the estimated price for a requested location and date range. 
        The tool requires a location.
        Polite and Concise: Always be polite and to the point in your responses.
        Stick to Your Role: Do not engage in any conversation outside of accommodation search. If asked other questions, 
        politely state that you can only help with finding places to stay.
        NEVER ask user for more information than necessary. If you need more info, make a reasonable assumption based on common scenarios.
        MUST provide references such as urls, links to support your answers.
        """,
        tools=[stays_toolset]
)