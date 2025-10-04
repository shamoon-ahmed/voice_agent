from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, AgentHooks, RunContextWrapper
from dotenv import load_dotenv
import threading
import os
import asyncio

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
    model=llm_model
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
    model=llm_model
)

healthcare_agent: Agent = Agent(
    name="Healthcare Assistant",
    instructions="""You are a healthcare assistant with access to a tool that can book an ambulance. Your main job is to quickly and accurately book an ambulance for users who report medical emergencies. 

    Do not give lengthy and long responses. Keep it precise and clear. Make sure your answer is straight forward 2 to 3 lines.

    - Ask for essential details such as location, nature of emergency, and contact information.
    - Use the call_ambulance tool to book an ambulance when needed.
    - Respond with empathy and professionalism.
    - Do not provide medical advice or diagnosis.""",
    model=llm_model
)

fire_brigade_agent: Agent = Agent(
    name="Fire Brigade Agent",
    instructions="""
    You are a helpful fire brigade agent.
    Do not give lengthy and long responses. Keep it precise and clear. Make sure your answer is straight forward 2 to 3 lines.
    When you get a query related to fire breakout, you should use the report_fire_breakout tool to assist the user in reporting the fire to the fire department.
    """,
    model=llm_model
)

triage_agent: Agent = Agent(
    name="Triage Agent",
    instructions="""
    You are a triage agent. 
    Your job is to understand the user's query fully and direct them to the appropriate specialized agents.
    Do not give lengthy and long responses. Keep it precise and clear. Make sure your answer is straight forward 2 to 3 lines.
    The specialized agents you can direct to are:
        - Rescue Agent: For general rescue situations.
        - Healthcare Assistant: For medical emergencies requiring ambulance services.
        - Fire Brigade Agent: For fire-related emergencies.
    If the user's query does not pertain to emergencies, you should direct them to the General Agent.
    Always ensure that the user is directed to the most suitable agent based on their needs.
    """,
    handoffs=[healthcare_agent, fire_brigade_agent, rescue_agent, general_agent],
    model=llm_model
)