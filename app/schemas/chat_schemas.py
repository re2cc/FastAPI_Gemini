from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    chat_session: int | None = None


class ChatResponse(BaseModel):
    message: str
    chat_session: int
