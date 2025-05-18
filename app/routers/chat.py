from typing import Annotated

from fastapi import APIRouter, Depends
from google import genai
from sqlalchemy.ext.asyncio import AsyncConnection

from app.dependencies import get_client, get_conn
from app.schemas.chat_schemas import ChatRequest

router = APIRouter()


@router.post("/chat")
async def chat(
    gemini_client: Annotated[genai.Client, Depends(get_client)],
    conn: Annotated[AsyncConnection, Depends(get_conn)],
    request: ChatRequest,
):
    return {"message": "Response"}
