import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from google import genai
from sqlalchemy.ext.asyncio import create_async_engine

from app.models.db_model import metadata_obj
from app.routers import chat

load_dotenv(override=True)


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
    async with app.state.db_engine.connect() as conn:
        await conn.run_sync(metadata_obj.create_all)
        await conn.commit()

    yield

    # Database cleanup
    await app.state.db_engine.dispose()

    print("Stopping app...")


app = FastAPI(lifespan=lifespan)

app.include_router(chat.router)
