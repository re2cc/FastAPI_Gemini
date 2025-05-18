from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from google import genai
from google.genai.types import (
    GenerateContentConfig,
    ModelContent,
    UserContent,
)
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.dependencies import get_client, get_conn
from app.models.db_model import chat_message as chat_message_table
from app.models.db_model import chat_session as chat_session_table
from app.schemas.chat_schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat")
async def chat(
    gemini_client: Annotated[genai.Client, Depends(get_client)],
    conn: Annotated[AsyncConnection, Depends(get_conn)],
    chat_request: ChatRequest,
):
    chat_session_id: int = 0
    if not chat_request.chat_session:
        result = await conn.execute(insert(chat_session_table).values())
        if not result.inserted_primary_key:
            raise HTTPException(status_code=500, detail="Failed to create session ID")
        chat_session_id = result.inserted_primary_key[0]
    else:  # TODO: check if chat_request.session exists
        chat_session_id = chat_request.chat_session

    history_retrieve_query = (
        select(chat_message_table.c.role, chat_message_table.c.message)
        .where(chat_message_table.c.chat_session_id == chat_session_id)
        .order_by(chat_message_table.c.time_created.asc())
    )
    result = await conn.execute(history_retrieve_query)

    history = []
    for row in result.all():
        if row.role == "user":
            history.append(UserContent(row.message))
        else:
            history.append(ModelContent(row.message))

    chat = gemini_client.aio.chats.create(
        model="gemini-2.0-flash-lite",
        config=GenerateContentConfig(
            system_instruction="Generate a response to the user message",
        ),
        history=history,
    )

    response = await chat.send_message(chat_request.message)
    if not response.text:
        raise HTTPException(status_code=500, detail="Failed to generate response")

    message_insert_query = insert(chat_message_table).values(
        chat_session_id=chat_session_id, role="user", message=chat_request.message
    )
    await conn.execute(message_insert_query)

    message_insert_query = insert(chat_message_table).values(
        chat_session_id=chat_session_id, role="model", message=response.text
    )
    await conn.execute(message_insert_query)

    await conn.commit()

    return ChatResponse(message=response.text, chat_session=chat_session_id)
