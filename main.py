from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, SQLiteSession, AgentHooks, RunContextWrapper
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
import os
import asyncio
import time
import threading

from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

from stt import listen_once

from frontline_agents.frontline_agents import general_agent, rescue_agent, healthcare_agent, fire_brigade_agent
from frontline_agents.lifecycle import MyAgentHooks

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

general_agent.voice_id = "FGY2WhTYpPnrIDTdsKH5" # Laura
rescue_agent.voice_id = "TX3LPaxmHKxFdv7VOQHJ" # Liam
healthcare_agent.voice_id = "pFZP5JQG7iQjIQuC4Bku" # Lily
fire_brigade_agent.voice_id = "SOYHLrjzK2X1ezoPC6cr" # Harry

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
    model=llm_model,
    hooks=MyAgentHooks()
)

async def main():

    greeting_audio = await asyncio.to_thread(
        elevenlabs.text_to_speech.convert,
        text="Frontline Emergency Services. What's the emergency?",
        voice_id=general_agent.voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )
    threading.Thread(target=play, args=(greeting_audio,), daemon=True).start()

    while True:
        choice = input("Voice or chat? (v/c): ").strip().lower()
        if choice == 'c':
            query = input("What's the emergency?")
        elif choice == 'v':
            query = listen_once()
            if query:
                print(f"User: {query}")
            if query.lower() in ["exit", "quit"]:
                break
        else:
            print("Invalid choice. Please enter 'v' for voice or 'c' for chat.")
            continue

        # Run conversation starting with triage agent.
        # The hooks will take care of voice playback + printing
        result = await Runner.run(
            starting_agent=triage_agent,
            input=query,
            session=session
        )

        # Print final text in plain form (voice + word sync already handled by hooks)
        print(f"\n[Final Output]: {result.final_output}")

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