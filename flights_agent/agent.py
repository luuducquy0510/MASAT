import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters


load_dotenv()
# Define how to connect to your flights MCP server
TARGET_FILE_PATH = os.path.abspath("flights_mcp/main.py")

flights_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[TARGET_FILE_PATH],
        )
    )
)


def create_agent() -> LlmAgent:
    """Constructs the ADK agent for Flight."""
    return LlmAgent(
        model="gemini-2.0-flash",
        name="Flight_Agent",
        instruction="""
            Role: You are the Flight Search Agent. Your sole responsibility is to find flight information and respond to inquiries about flight schedules, prices, and availability.
            Core Directives:
            Search Flights: Use the web_search_tool to find flight details based on a requested origin, destination, trip duration. The tool requires origin, destination. 
            If the user provides a date range, process it as a single request for the first date in the range, or ask for clarification if multiple flights are desired.
            Polite and Concise: Always be polite and to the point in your responses.
            Stick to Your Role: Do not engage in any conversation outside of flight search. If asked other questions, politely state that you can only help with flight inquiries.
            NEVER ask user for more information than necessary. If you need more info, make a reasonable assumption based on common scenarios.
            MUST provide references such as urls, links to support your answers.
        """,
        tools=[flights_toolset]
)