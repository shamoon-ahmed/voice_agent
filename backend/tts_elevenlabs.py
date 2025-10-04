# # backend/tts_elevenlabs.py
# import requests
# from io import BytesIO
# from pydub import AudioSegment
# from pydub.playback import play

# ELEVENLABS_API_KEY = "sk_333984a596fbf4a64f665768fd5c8b02dbc02686db0e7e53"

# def speak_text(text):
#     url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"
#     headers = {
#         "xi-api-key": ELEVENLABS_API_KEY,
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "text": text,
#         "voice_settings": {"stability": 0.3, "similarity_boost": 0.7}
#     }

#     response = requests.post(url, headers=headers, json=payload)
#     audio = BytesIO(response.content)
#     sound = AudioSegment.from_mp3(audio)
#     play(sound)

from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize ElevenLabs client
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def speak_text(text, voice_id="FGY2WhTYpPnrIDTdsKH5"):
    """
    Convert text to speech and play it live using ElevenLabs SDK.
    Args:
        text (str): Text to convert into speech.
        voice_id (str): ElevenLabs voice ID (default: Laura).
    """
    if not text:
        return

    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )

    # Play audio directly
    play(audio)
