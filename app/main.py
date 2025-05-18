import os
from contextlib import asynccontextmanager
from typing import Annotated, cast

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from google import genai
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

load_dotenv()


class ChatRequest(BaseModel):
    message: str
    session: int | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting app...")

    # Gemini setup
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    app.state.gemini_client = genai.Client(api_key=gemini_api_key)

    # Database setup
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")

    app.state.db_engine = create_async_engine(db_url, echo=True)

    yield

    # Database cleanup
    await app.state.db_engine.dispose()

    print("Stopping app...")


app = FastAPI(lifespan=lifespan)


def get_client() -> genai.Client:
    return app.state.gemini_client


async def get_conn():
    async with app.state.db_engine.connect() as conn:
        yield cast(AsyncConnection, conn)


@app.post("/chat")
async def chat(
    gemini_client: Annotated[genai.Client, Depends(get_client)],
    conn: Annotated[AsyncConnection, Depends(get_conn)],
    request: ChatRequest,
):
    return {"message": "Response"}
