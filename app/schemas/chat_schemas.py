from enum import Enum

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    chat_session: int | None = None


class ChatResponse(BaseModel):
    message: str
    chat_session: int


class EmotionalState(str, Enum):
    calm = "calm"
    angry = "angry"
    happy = "happy"
    sad = "sad"
    frustrated = "frustrated"


class AnalysisModelResponse(BaseModel):
    emotional_state: EmotionalState
    stress_value: int
    human_required: bool
