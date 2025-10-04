# backend/main.py
from fastapi import FastAPI
from livekit_routes import router as livekit_router

app = FastAPI(title="Voice Emergency AI")
app.include_router(livekit_router)
