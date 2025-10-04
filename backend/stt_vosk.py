# backend/stt_vosk.py
from vosk import Model, KaldiRecognizer
import json
import wave

MODEL_PATH = r"../vosk-model-small-en-us-0.15"
model = Model(MODEL_PATH)  # path to unzipped model folder

def speech_to_text(audio_path: str):
    wf = wave.open(audio_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text += result.get("text", "") + " "

    result = json.loads(rec.FinalResult())
    text += result.get("text", "")
    return text.strip()
