import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from google import genai
from google.genai.types import GenerateContentConfig, ModelContent, UserContent
from google.genai.types import Schema as GenaiSchema
from google.genai.types import Type as GenaiType
from pydantic import ValidationError
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.dependencies import get_client, get_conn
from app.models.db_model import chat_message as chat_message_table
from app.models.db_model import chat_session as chat_session_table
from app.schemas.chat_schemas import AnalysisModelResponse, ChatRequest, ChatResponse

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
    else:
        chat_session_verify_query = select(chat_session_table.c.id).where(
            chat_session_table.c.id == chat_request.chat_session
        )
        result = await conn.execute(chat_session_verify_query)
        if not result.one_or_none():
            raise HTTPException(status_code=404, detail="Failed to find chat session")

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

    analysis_chat = gemini_client.aio.chats.create(
        model=os.getenv("ANALYSIS_MODEL", "gemini-1.5-flash-8b"),
        config=GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GenaiSchema(
                type=GenaiType.OBJECT,
                required=["emotional_state", "stress_value", "human_required"],
                properties={
                    "emotional_state": GenaiSchema(
                        type=GenaiType.STRING,
                        enum=["calm", "angry", "happy", "sad", "frustrated"],
                    ),
                    "stress_value": GenaiSchema(
                        type=GenaiType.INTEGER,
                    ),
                    "human_required": GenaiSchema(
                        type=GenaiType.BOOLEAN,
                    ),
                },
            ),
            system_instruction="""Your goal is to analyze the user emotional state and stress level (in a scale from 0 to 10). You should analyze the user input and answer based on their writing patterns and language, pay attention to how the user's writing evolves. If the stress value pass the 7, the user gets angry or the user asks to speak with a human you should send him with a human.
Your conversation should look like:
User: Hi, could you help me with a problem?
Model: {
  \"emotional_state\": \"calm\",
  \"human_required\": false
  \"stress_value\": 0,
}
User: Stupid machine, why do i even need to talk with you?a fahbw fbwwwhfhb
Model: {
  \"emotional_state\": \"angry\",
  \"human_required\": true
  \"stress_value\": 9,
}""",
        ),
        history=history[-6:],
    )

    analysis_response = await analysis_chat.send_message(chat_request.message)
    if not analysis_response.text:
        raise HTTPException(status_code=500, detail="Failed to generate response")
    try:
        analysis_response = AnalysisModelResponse.model_validate_json(
            analysis_response.text
        )
    except ValidationError:
        raise HTTPException(status_code=500, detail="Interal model error")

    # TODO: Some kind of redirect, not really in project scope
    if analysis_response.human_required:
        raise HTTPException(status_code=501, detail="Redirect to human :(")

    main_chat = gemini_client.aio.chats.create(
        model=os.getenv("ANALYSIS_MODEL", "gemini-2.0-flash-lite"),
        config=GenerateContentConfig(
            system_instruction="""You are a helpfull customer support chatbot, your goal is to resolve the problem that the user might have. You should adapt to the user request and ask for clarification if you dont undestand insted of make guesses. The user may have an indicative of the current mood of the user, use it to decide how to aproach the user. Your conversations should look like:
User: Hi, could you help me?
Model: Of couse, what would you need help with?
User: (sad) My package has not arived yet, i am afraid it might have get lost""",
        ),
        history=history,
    )

    response = await main_chat.send_message(
        f"({analysis_response.emotional_state.value}) {chat_request.message}"
    )
    if not response.text:
        raise HTTPException(status_code=500, detail="Failed to generate response")

    user_message_insert_query = insert(chat_message_table).values(
        chat_session_id=chat_session_id, role="user", message=chat_request.message
    )
    await conn.execute(user_message_insert_query)

    model_message_insert_query = insert(chat_message_table).values(
        chat_session_id=chat_session_id, role="model", message=response.text
    )
    await conn.execute(model_message_insert_query)

    await conn.commit()

    return ChatResponse(message=response.text, chat_session=chat_session_id)
