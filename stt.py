import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

MODEL_PATH = "vosk-model-small-en-us-0.15"
sample_rate = 16000

# Load model once
model = Model(MODEL_PATH)

# Recognizer
recognizer = KaldiRecognizer(model, sample_rate)

# Audio queue
q = queue.Queue()

def _callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    q.put(bytes(indata))

def listen_once():
    """
    Listen to mic until the user stops speaking,
    then return final recognized text.
    """
    with sd.RawInputStream(samplerate=sample_rate, blocksize=8000, dtype='int16',
                           channels=1, callback=_callback):

        print("🎤 Speak now...")

        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if result.get("text"):
                    return result["text"]
