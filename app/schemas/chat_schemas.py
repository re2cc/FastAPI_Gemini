from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session: int | None = None
