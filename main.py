from contextlib import asynccontextmanager
from typing import Annotated
import os

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

load_dotenv()

class ChatRequest(BaseModel):
    message: str
    session: int | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting app...")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    app.state.gemini_client = genai.Client(api_key=gemini_api_key)
    yield
    print("Stopping app...")

app = FastAPI(lifespan=lifespan)

def get_client() -> genai.Client:
    return app.state.gemini_client

@app.post("/chat")
async def chat(gemini_client: Annotated[genai.Client, Depends(get_client)], request: ChatRequest):
    return {"message": "Response"}
