from agents import Agent, AgentHooks, RunContextWrapper
import asyncio
import os
import threading

from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

speech_lock = asyncio.Lock()


elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


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
