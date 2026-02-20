from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


class EvaluationResult(BaseModel):
    session_id: str
    score: int
    reasoning: str
    timestamp: str
