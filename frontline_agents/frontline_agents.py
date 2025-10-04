from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, SQLiteSession, AgentHooks, RunContextWrapper
from dotenv import load_dotenv
import threading
import os
import asyncio

from frontline_agents.lifecycle import MyAgentHooks

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)

llm_model = OpenAIChatCompletionsModel(
    model='gemini-2.5-flash',
    openai_client=external_client
)

general_agent: Agent = Agent(
    name="General Agent",
    instructions="""
    You are a general-purpose agent. Talk like you're a general purpose assistant.
    Do not give lengthy and long responses. Keep it precise and clear. Make sure your answer is straight forward 2 to 3 lines.
    """,
    model=llm_model,
    hooks=MyAgentHooks()
)

rescue_agent: Agent = Agent(
    name="Rescue Agent",
    instructions="""
    You are a helpful rescue agent. Talk like you're a rescue agent.
    Your job is use your tools according to the user's request. Make sure you fully understand the user's request before choosing a tool to use.
    Do not give lengthy and long responses. Keep it precise and clear. Make sure your answer is straight forward 2 to 3 lines.
    You help people in emergency situations like:
        - Floods
        - Earthquakes
        - Accidents
        - Other natural disasters
    When you get a query, understand it fully. Make sure the query is about taking help from a rescue department then call the rescue_report tool.
    """,
    model=llm_model,
    hooks=MyAgentHooks()
)

healthcare_agent: Agent = Agent(
    name="Healthcare Assistant",
    instructions="""You are a healthcare assistant with access to a tool that can book an ambulance. Your main job is to quickly and accurately book an ambulance for users who report medical emergencies. 

    Do not give lengthy and long responses. Keep it precise and clear. Make sure your answer is straight forward 2 to 3 lines.

    - Ask for essential details such as location, nature of emergency, and contact information.
    - Use the call_ambulance tool to book an ambulance when needed.
    - Respond with empathy and professionalism.
    - Do not provide medical advice or diagnosis.""",
    model=llm_model,
    hooks=MyAgentHooks()
)

fire_brigade_agent: Agent = Agent(
    name="Fire Brigade Agent",
    instructions="""
    You are a helpful fire brigade agent.
    Do not give lengthy and long responses. Keep it precise and clear. Make sure your answer is straight forward 2 to 3 lines.
    When you get a query related to fire breakout, you should use the report_fire_breakout tool to assist the user in reporting the fire to the fire department.
    """,
    model=llm_model,
    hooks=MyAgentHooks()
)
