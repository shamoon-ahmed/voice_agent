from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from livekit.agents import Agent as LivekitAgent
from dotenv import load_dotenv
import os

load_dotenv()

# Give LiveKit an explicit label
label = "Frontline Triage Agent"

# Load keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# External LLM client (Gemini)
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)

# Define the LLM model
llm_model = OpenAIChatCompletionsModel(
    model='gemini-2.5-flash',
    openai_client=external_client
)

# --- Sub Agents ---
general_agent = Agent(
    name="General Agent",
    instructions="""
    You are a general-purpose agent. Keep responses short, precise, and direct (2–3 lines max).
    """,
    model=llm_model
)

rescue_agent = Agent(
    name="Rescue Agent",
    instructions="""
    You help people in emergencies like floods, earthquakes, or accidents. Keep responses short and professional.
    Use the rescue_report tool when appropriate.
    """,
    model=llm_model
)

healthcare_agent = Agent(
    name="Healthcare Assistant",
    instructions="""
    You are a healthcare assistant that helps users book ambulances for medical emergencies.
    Ask for location, nature of emergency, and contact. Be empathetic and concise.
    """,
    model=llm_model
)

fire_brigade_agent = Agent(
    name="Fire Brigade Agent",
    instructions="""
    You help report fire-related emergencies to the fire department. Respond clearly and quickly.
    """,
    model=llm_model
)

# --- Triage Agent ---
triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    You are a triage agent.
    Understand the user's situation and hand them off to the most appropriate agent:
    - Rescue Agent → for general rescue
    - Healthcare Assistant → for medical emergencies
    - Fire Brigade Agent → for fire emergencies
    - General Agent → for non-emergency or general help
    Keep answers short and natural (2–3 lines).
    """,
    handoffs=[healthcare_agent, fire_brigade_agent, rescue_agent, general_agent],
    model=llm_model
)

# --- Wrap for LiveKit compatibility ---
class LivekitTriageAgent(LivekitAgent):
    label = label

    async def on_text(self, message: str) -> str:
        """
        This is what LiveKit will call when the user speaks.
        It forwards the query to your multi-agent system.
        """
        print(f"🗣️ User: {message}")

        result = await Runner.run(
            starting_agent=triage_agent,
            input=message
        )

        reply = result.final_output or "Sorry, I couldn’t process that."
        print(f"🤖 Triage Agent: {reply}")
        return reply


# Export instance for livekit_agent_server.py
agent = LivekitTriageAgent(instructions = "You are a Triage Agent. Direct users to the right help.")
