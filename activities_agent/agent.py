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