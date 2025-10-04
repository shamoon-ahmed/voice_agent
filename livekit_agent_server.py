from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, AgentSession
from frontline_agents.triage_agent import agent as triage_agent
from agents import Runner
from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

eleven = ElevenLabs(api_key=ELEVEN_API_KEY)


async def entry(ctx: JobContext):
    """Called when a new voice session starts."""
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create the voice session
    session = AgentSession(
        llm="google/gemini-2.5-flash",
        tts="elevenlabs/eleven_multilingual_v2:alice",
    )

    # ✅ Start the session — attach the room here
    await session.start(
        room=ctx.room,
        agent=triage_agent,
    )

    # ❌ Remove this line (deprecated):
    # await ctx.wait_for_disconnection()

    # session.start() will now handle waiting internally


async def run_agent_conversation(query: str) -> str:
    print("User said:", query)
    result = await Runner.run(starting_agent=triage_agent, input=query)
    return result.final_output


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entry))
