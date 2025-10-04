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

        """
        This runs when an agent finishes. It:
          - extracts text from output
          - synthesizes TTS using agent.voice_id
          - plays audio and prints text word-by-word synced to audio duration
        """
        # extract text safely from `output`
        if isinstance(output, str):
            text = output
        elif hasattr(output, "get") and isinstance(output, dict):
            # common pattern: {"text": "..."}
            text = output.get("text") or output.get("output") or str(output)
        else:
            try:
                text = str(output)
            except Exception:
                return

        text = text.strip()
        if not text:
            return

        # choose voice; fallback to triage/general voice if missing
        voice_id = getattr(agent, "voice_id", None) or "FGY2WhTYpPnrIDTdsKH5"

        # Synthesize in a thread (non-blocking for the event loop)
        def synth():
            return elevenlabs.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )

        # Use a lock so only one agent speaks at a time
        async with speech_lock:
            audio = await asyncio.to_thread(synth)

            # compute audio duration if available, else estimate (0.18s per word)
            words = text.split()
            duration = getattr(audio, "duration", None)
            if duration is None:
                duration = max(1.0, 0.18 * max(1, len(words)))

            # start playback in background thread (so we can print while it plays)
            threading.Thread(target=play, args=(audio,), daemon=True).start()

            # print words synced to duration (approx)
            delay = duration / max(1, len(words))
            for w in words:
                print(w + " ", end="", flush=True)
                await asyncio.sleep(delay)
            print()  # newline after done

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

general_agent.voice_id = "FGY2WhTYpPnrIDTdsKH5" # Laura
rescue_agent.voice_id = "TX3LPaxmHKxFdv7VOQHJ" # Liam
healthcare_agent.voice_id = "pFZP5JQG7iQjIQuC4Bku" # Lily
fire_brigade_agent.voice_id = "SOYHLrjzK2X1ezoPC6cr" # Harry

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