from typing import cast

from fastapi import Request
from google import genai
from sqlalchemy.ext.asyncio import AsyncConnection


def get_client(request: Request) -> genai.Client:
    return request.app.state.gemini_client


async def get_conn(request: Request):
    async with request.app.state.db_engine.connect() as conn:
        yield cast(AsyncConnection, conn)
