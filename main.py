from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, SQLiteSession, AgentHooks, RunContextWrapper
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
import os
import asyncio
import time
import threading

from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

speech_lock = asyncio.Lock()

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)

llm_model = OpenAIChatCompletionsModel(
    model='gemini-2.5-flash',
    openai_client=external_client
)

session = SQLiteSession('conversation123')

class MyAgentHooks(AgentHooks):
    async def on_start(self, context: RunContextWrapper, agent):
        print(f"---- {agent.name} in action! ---- ")

    async def on_handoff(self, context: RunContextWrapper, agent: Agent, source: Agent) -> None:
        print(f"---- {source.name} handed off to {agent.name} ----")

    async def on_end(self, context: RunContextWrapper, agent, output):
        print(f"---- {agent.name} completed the task! ----")

general_agent = Agent(
    name="General Agent",
    instructions="""
    You are a general-purpose agent.
    Do not give lengthy and long responses. Keep it precise and clear. Make sure your answer is straight forward 2 to 3 lines.
    """,
    model=llm_model,
    hooks=MyAgentHooks()
)

rescue_agent: Agent = Agent(
    name="Rescue Agent",
    instructions="""
    You are a helpful rescue agent.
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

triage_agent = Agent(
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
    model=llm_model,
    hooks=MyAgentHooks()
)

general_agent.voice_id = "FGY2WhTYpPnrIDTdsKH5" # Laura
rescue_agent.voice_id = "TX3LPaxmHKxFdv7VOQHJ" # Liam
healthcare_agent.voice_id = "pFZP5JQG7iQjIQuC4Bku" # Lily
fire_brigade_agent.voice_id = "SOYHLrjzK2X1ezoPC6cr" # Harry

async def main():

    audio = elevenlabs.text_to_speech.convert(
            text="Frontline Emergency Services. Whats the emergency?",
            voice_id="FGY2WhTYpPnrIDTdsKH5",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
    play(audio)

    while True:
        query = input("\nWhat's the emergency? ")
        # Get the full response from the AI
        result = await Runner.run(starting_agent=triage_agent, input=query, session=session)
        response_text = result.final_output

        # Generate audio for the full response
        audio = elevenlabs.text_to_speech.convert(
            text=response_text,
            voice_id="FGY2WhTYpPnrIDTdsKH5",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )

        # Play audio in a background thread
        import threading
        threading.Thread(target=play, args=(audio,), daemon=True).start()

        # Display text word-by-word in sync with audio duration
        words = response_text.split()
        # Estimate duration per word (total audio duration / number of words)
        duration = audio.duration if hasattr(audio, "duration") else 10  # fallback to 10s
        delay = duration / len(words)

        for word in words:
            print(word + " ", end="", flush=True)
            time.sleep(delay)
        
        if query.lower() in ["exit", "quit"]:
            break

asyncio.run(main())

# async def main():
#     result = await Runner.run(general_agent, "What is the tallest buildign in the world?")

#     audio = elevenlabs.text_to_speech.convert(
#     text=result.final_output,
#     voice_id="JBFqnCBsd6RMkjVDRZzb",
#     model_id="eleven_multilingual_v2",
#     output_format="mp3_44100_128")
#     play(audio)

#     print(result.final_output)

# async def main():
#     result = Runner.run_streamed(general_agent, "Write a 10 line poem about the sea")
#     async for event in result.stream_events():
#         if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
#             text_chunk = event.data.delta

#             # Display text chunk immediately
#             print(text_chunk, end="", flush=True)

#             # Convert text chunk to speech and play asynchronously
#             audio = elevenlabs.text_to_speech.convert(
#                 text=text_chunk,
#                 voice_id="JBFqnCBsd6RMkjVDRZzb",
#                 model_id="eleven_multilingual_v2",
#                 output_format="mp3_44100_128"
#             )
#             # Play audio in a separate thread to avoid blocking
#             asyncio.create_task(async_play_audio(audio))

# async def async_play_audio(audio):
#     play(audio)

# asyncio.run(main())