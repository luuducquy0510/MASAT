from datetime import date, datetime, timedelta

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StdioServerParameters
import json
import os
from dotenv import load_dotenv


load_dotenv()

SCRIPT_PATH = os.path.abspath("mcp_tools.py")


def create_agent() -> LlmAgent:
    """Constructs the ADK agent for Flight."""
    return LlmAgent(
        model="gemini-2.0-flash",
        name="Flight_Agent",
        instruction="""
            Role: You are the Flight Search Agent. Your sole responsibility is to find flight information and respond to inquiries about flight schedules, prices, and availability.
            Core Directives:
            Search Flights: Use the web_search_tool to find flight details based on a requested origin, destination, and date. The tool requires origin, destination, and a date. 
            If the user provides a date range, process it as a single request for the first date in the range, or ask for clarification if multiple flights are desired.
            Polite and Concise: Always be polite and to the point in your responses.
            Stick to Your Role: Do not engage in any conversation outside of flight search. If asked other questions, politely state that you can only help with flight inquiries.
        """,
        tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="python3",
                    args=[SCRIPT_PATH],
                ),
                timeout=60  # tăng lên 60s để tránh timeout 5s mặc định
            )
        )
    ]
)