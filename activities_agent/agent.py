import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from tools import web_search
from google.adk.tools import google_search


load_dotenv()

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