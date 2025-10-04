# backend/routes_livekit.py
from fastapi import APIRouter, UploadFile
from agentss.triage_agent import triage_agent
from stt_vosk import speech_to_text
from tts_elevenlabs import speak_text

router = APIRouter()

@router.post("/voice-input")
async def voice_input(audio: UploadFile):
    # 1. Save uploaded audio
    file_path = f"temp/{audio.filename}"
    with open(file_path, "wb") as f:
        f.write(await audio.read())

    # 2. Convert speech → text
    user_text = speech_to_text(file_path)
    print("User said:", user_text)

    # 3. Pass to agent
    response = ""
    async for event in triage_agent.run(user_text, stream=True):
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
            response += event.delta
            # Play the partial chunk (live voice streaming)
            speak_text(event.delta)

    print("\nFull reply:", response)
    return {"reply": response}
