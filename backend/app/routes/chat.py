from fastapi import APIRouter

from app.agent import agent
from app.evaluation import maybe_trigger_evaluation
from app.models import ChatRequest, ChatResponse

router = APIRouter()

sessions: dict[str, list] = {}


@router.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    history = sessions.get(request.session_id, [])
    async with agent:
        result = await agent.run(request.message, message_history=history)
    all_messages = result.all_messages()
    sessions[request.session_id] = all_messages
    maybe_trigger_evaluation(request.session_id, all_messages)
    return ChatResponse(response=result.output, session_id=request.session_id)
