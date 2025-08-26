import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from tools import web_search
from google.adk.tools import google_search


load_dotenv()

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