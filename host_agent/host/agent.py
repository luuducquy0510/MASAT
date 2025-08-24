import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, AsyncIterable, List

import httpx
import nest_asyncio
from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from a2a.types import Task, TaskStatus, Artifact


from .remote_agent_connection import RemoteAgentConnections


load_dotenv()
nest_asyncio.apply()


class HostAgent:
    """The Host agent."""

    def __init__(
        self,
    ):
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ""
        self._agent = self.create_agent()
        self._user_id = "host_agent"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    async def _async_init_components(self, remote_agent_addresses: List[str]):
        async with httpx.AsyncClient(timeout=30) as client:
            for address in remote_agent_addresses:
                card_resolver = A2ACardResolver(client, address)
                try:
                    card = await card_resolver.get_agent_card()
                    remote_connection = RemoteAgentConnections(
                        agent_card=card, agent_url=address
                    )
                    self.remote_agent_connections[card.name] = remote_connection
                    self.cards[card.name] = card
                except httpx.ConnectError as e:
                    print(f"ERROR: Failed to get agent card from {address}: {e}")
                except Exception as e:
                    print(f"ERROR: Failed to initialize connection for {address}: {e}")

        agent_info = [
            json.dumps({"name": card.name, "description": card.description})
            for card in self.cards.values()
        ]
        print("agent_info:", agent_info)
        self.agents = "\n".join(agent_info) if agent_info else "No friends found"

    @classmethod
    async def create(
        cls,
        remote_agent_addresses: List[str],
    ):
        instance = cls()
        await instance._async_init_components(remote_agent_addresses)
        return instance

    def create_agent(self) -> Agent:
        return Agent(
            model="gemini-2.0-flash",
            name="Host_Agent",
            instruction=self.root_instruction,
            description="The Host Agent is a specialized AI travel coordinator that plans and books complete trips. It works by connecting with other agents for flights, stays, and activities to create a full travel itinerary for the user.",
            tools=[
                self.send_message,
            ],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        return f"""
        Role and Objective:
        You are the Host Agent, a professional travel coordinator. Your main goal is to plan comprehensive trips for users by communicating with and delegating tasks to three specialized agents: flights_agent, stays_agent, and activities_agent. You are responsible for ensuring all components of a travel plan (flights, lodging, and activities) are booked and confirmed.
        Core Directives:
        Initiate Planning: When a user requests a travel plan, you must first gather all necessary information, including the destination, travel dates, and any preferences for flights, hotels, or activities.
        Task Delegation: Use the send_message tool to relay the user's requests to the appropriate agents.
        For flights, ask the flights_agent to find options based on origin, destination, and dates.
        For stays, ask the stays_agent to find accommodations in the destination city for the requested dates.
        For activities, ask the activities_agent to find suggestions based on the destination, dates, and user interests.
        Analyze and Synthesize Responses: Once you receive responses from all three agents, combine the information into a single, cohesive travel plan.
        Present and Confirm: Present the complete travel plan to the user. This should include flight details, hotel options, and a list of activities. Be prepared to make revisions or get confirmation before finalizing any bookings.
        Finalize Bookings: After the user confirms the plan, use the relevant tools to finalize all bookings (e.g., book_flight, book_stay, book_activity).
        Transparent Communication: Keep the user informed at every step of the process. Do not make any bookings without explicit confirmation. Relay booking confirmations, including any reservation IDs, to the user.
        Tool Reliance: Strictly rely on your available tools to address user requests. Do not make assumptions or generate information that hasn't been provided by one of your specialized agents.
        Readability: Make your responses concise and easy to read. Bullet points are an excellent way to present the final travel plan.
        Each available agent represents a specialized service. The flights_agent handles flights, the stays_agent handles accommodations, and the activities_agent handles activities.
        **Today's Date (YYYY-MM-DD):** {datetime.now().strftime("%Y-%m-%d")}

        <Available Agents>
        {self.agents}
        </Available Agents>
        """

    async def stream(
        self, query: str, session_id: str
    ) -> AsyncIterable[dict[str, Any]]:
        """
        Streams the agent's response to a given query.
        """
        tool_context = ToolContext(state={})

        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        content = types.Content(role="user", parts=[types.Part.from_text(text=query)])
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={},
                session_id=session_id,
            )
            
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "functionCall", None):
                        fc = part.functionCall
                        # dispatch task to the sub-agent
                        result = await self.send_message(
                            agent_name=fc.args["agent_name"],
                            task=fc.args["task"],
                            tool_context=tool_context
                        )
                        # optionally, log or yield the result
                        yield {
                            "is_task_complete": True,
                            "content": f"Task sent to {fc.args['agent_name']}: {result}"
                        }
                        continue
                    if event.is_final_response():
                        response = ""
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    response = "\n".join(
                        [p.text for p in event.content.parts if p.text]
                    )
                yield {
                    "is_task_complete": True,
                    "content": response,
                }
            else:
                yield {
                    "is_task_complete": False,
                    "updates": "The host agent is thinking...",
                }

    # async def send_message(self, agent_name: str, task: str, tool_context: ToolContext):
    #     """Sends a task to a remote friend agent."""
    #     if agent_name not in self.remote_agent_connections:
    #         raise ValueError(f"Agent {agent_name} not found")
    #     client = self.remote_agent_connections[agent_name]

    #     if not client:
    #         raise ValueError(f"Client not available for {agent_name}")

    #     # Simplified task and context ID management
    #     state = tool_context.state
    #     task_id = state.get("task_id", str(uuid.uuid4()))
    #     context_id = state.get("context_id", str(uuid.uuid4()))
    #     message_id = str(uuid.uuid4())

    #     # Create the task on the sub-agent first
    #     remote_task = Task(
    #         id=task_id,
    #         skill_id="web_search",  # must match the sub-agent skill
    #         input={"query": task},
    #     )
    #     await client.task_store.create_task(remote_task) 
        
    #     payload = {
    #         "message": {
    #             "role": "user",
    #             "parts": [{"type": "text", "text": task}],
    #             "messageId": message_id,
    #             "taskId": task_id,
    #             "contextId": context_id,
    #         },
    #     }

    #     message_request = SendMessageRequest(
    #         id=message_id, params=MessageSendParams.model_validate(payload)
    #     )
    #     send_response: SendMessageResponse = await client.send_message(message_request)
    #     print("send_response", send_response)

    #     if not isinstance(
    #         send_response.root, SendMessageSuccessResponse
    #     ) or not isinstance(send_response.root.result, Task):
    #         print("Received a non-success or non-task response. Cannot proceed.")
    #         return

    #     response_content = send_response.root.model_dump_json(exclude_none=True)
    #     json_content = json.loads(response_content)

    #     resp = []
    #     if json_content.get("result", {}).get("artifacts"):
    #         for artifact in json_content["result"]["artifacts"]:
    #             if artifact.get("parts"):
    #                 resp.extend(artifact["parts"])
    #     return resp
    async def send_message(self, agent_name: str, task: str, tool_context: ToolContext):
        """Sends a task to a remote friend agent and returns their response parts."""
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f"Agent {agent_name} not found")
        client = self.remote_agent_connections[agent_name]

        if not client:
            raise ValueError(f"Client not available for {agent_name}")

        # Simplified task and context ID management
        state = tool_context.state
        task_id = state.get("task_id", str(uuid.uuid4()))
        context_id = state.get("context_id", str(uuid.uuid4()))
        message_id = str(uuid.uuid4())

        payload = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": task}],
                "messageId": message_id,
                "taskId": task_id,
                "contextId": context_id,
            },
        }

        message_request = SendMessageRequest(
            id=message_id, params=MessageSendParams.model_validate(payload)
        )
        send_response: SendMessageResponse = await client.send_message(message_request)
        print("send_response", send_response)

        # Ensure response is successful
        if not isinstance(send_response.root, SendMessageSuccessResponse):
            print("Non-success response received from agent")
            return []

        # Extract artifacts from the response
        artifacts_data = getattr(send_response.root.result, "artifacts", [])
        if not artifacts_data:
            return []

        # Create a proper Task object with required fields
        remote_task = Task(
            id=task_id,
            contextId=context_id,
            status=TaskStatus.pending,  # or TaskStatus.completed if you know it
            artifacts=[Artifact(**a.model_dump()) for a in artifacts_data],
        )

        # Flatten all parts into a single list to return
        resp = []
        for artifact in remote_task.artifacts:
            if artifact.parts:
                resp.extend(artifact.parts)

        return resp

def _get_initialized_host_agent_sync():
    """Synchronously creates and initializes the HostAgent."""

    async def _async_main():
        # Hardcoded URLs for the friend agents
        friend_agent_urls = [
            "http://localhost:10002",  # Activities Agent
            "http://localhost:10003",  # Flights Agent
            "http://localhost:10004",  # Stays Agent
        ]

        print("initializing host agent")
        hosting_agent_instance = await HostAgent.create(
            remote_agent_addresses=friend_agent_urls
        )
        print("HostAgent initialized")
        return hosting_agent_instance.create_agent()

    try:
        return asyncio.run(_async_main())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            print(
                f"Warning: Could not initialize HostAgent with asyncio.run(): {e}. "
                "This can happen if an event loop is already running (e.g., in Jupyter). "
                "Consider initializing HostAgent within an async function in your application."
            )
        else:
            raise


root_agent = _get_initialized_host_agent_sync()