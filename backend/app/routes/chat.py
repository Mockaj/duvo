from fastapi import APIRouter

from app.agent import agent
from app.models import ChatRequest, ChatResponse

router = APIRouter()

sessions: dict[str, list] = {}


@router.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    history = sessions.get(request.session_id, [])
    result = await agent.run(request.message, message_history=history)
    sessions[request.session_id] = result.all_messages()
    return ChatResponse(response=result.output, session_id=request.session_id)
