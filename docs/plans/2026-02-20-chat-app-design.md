# Duvo Chat App — Design Document

**Date**: 2026-02-20
**Status**: Approved

## Goal

Build a lightweight full-stack chat application: React frontend (Vite + shadcn) calling a FastAPI backend powered by pydantic-ai with DuckDuckGo web search and Logfire observability.

## Scope

**In scope (v1):**
- Single chat page with message input and response display
- Multi-turn conversation with in-memory history (per session)
- Agent autonomously decides when to use DuckDuckGo web search
- "New Chat" button to start fresh conversation without server restart
- Logfire observability for both FastAPI requests and pydantic-ai agent calls
- Manual run (no Docker)

**Out of scope:**
- SSE/streaming responses
- Persistent storage / database
- Authentication
- Multiple concurrent users (works but no session isolation guarantees)
- Docker deployment

## Architecture

### Approach: Minimal Monolith Backend

Single FastAPI app with one POST endpoint. Agent instance at module level. Conversation history in an in-memory dict keyed by session ID.

```
┌─────────────┐    POST /api/chat    ┌──────────────────────┐
│   Frontend   │ ──────────────────► │   FastAPI Backend     │
│  Vite+React  │ ◄────────────────── │                      │
│   shadcn UI  │    JSON response    │  ┌─────────────────┐ │
│              │                     │  │  pydantic-ai     │ │
│  localhost:  │                     │  │  Agent           │ │
│  5173        │                     │  │  (Claude 4.6)    │ │
│              │                     │  │  + DuckDuckGo    │ │
└─────────────┘                     │  └─────────────────┘ │
                                    │                      │
                                    │  Logfire telemetry ──┼──► Logfire Dashboard
                                    │  localhost:8000      │
                                    └──────────────────────┘
```

## Project Structure

```
duvo/
├── backend/
│   ├── pyproject.toml
│   ├── .env                    # ANTHROPIC_API_KEY, LOGFIRE_TOKEN
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app, CORS, logfire setup
│   │   ├── agent.py            # pydantic-ai Agent definition
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── chat.py         # POST /api/chat endpoint
│   │   └── models.py           # Pydantic request/response schemas
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   └── Chat.tsx
│   │   ├── lib/
│   │   │   └── api.ts
│   │   └── main.tsx
```

## Backend Design

### Agent Definition (`app/agent.py`)

Per pydantic-ai docs — module-level agent with DuckDuckGo common tool:

```python
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

agent = Agent(
    'anthropic:claude-sonnet-4-6',
    tools=[duckduckgo_search_tool()],
    instructions='You are a helpful assistant with web search capabilities.',
)
```

The agent autonomously decides when to invoke web search based on the user's query.

### Conversation History (`app/routes/chat.py`)

Per pydantic-ai docs — multi-turn via `message_history` param and `result.all_messages()`:

```python
sessions: dict[str, list] = {}

@router.post("/api/chat")
async def chat(request: ChatRequest):
    history = sessions.get(request.session_id, [])
    result = await agent.run(request.message, message_history=history)
    sessions[request.session_id] = result.all_messages()
    return ChatResponse(response=result.output, session_id=request.session_id)
```

New conversation = frontend generates new UUID → no history found → fresh context.

### Observability (`app/main.py`)

Per logfire docs (https://logfire.pydantic.dev/docs/#instrument):

```python
import logfire
from dotenv import load_dotenv

load_dotenv()  # Load ANTHROPIC_API_KEY, LOGFIRE_TOKEN

logfire.configure()
logfire.instrument_pydantic_ai()  # Instruments agent calls
logfire.instrument_fastapi(app)   # Instruments HTTP requests
```

### Request/Response Models (`app/models.py`)

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
```

## Frontend Design

### Chat Component (`components/Chat.tsx`)

Built with shadcn components:
- **Card** — main chat container
- **ScrollArea** — scrollable message history
- **Input** + **Button** — message input area
- Messages as styled divs (user right-aligned, assistant left-aligned)
- Loading state: disabled input + spinner while awaiting response
- **"New Chat" button** in header — generates new UUID, clears local messages

### State Management

React `useState` only — no external state library:
- `messages: Array<{role: 'user' | 'assistant', content: string}>`
- `sessionId: string` (crypto.randomUUID(), regenerated on "New Chat")
- `isLoading: boolean`

### API Client (`lib/api.ts`)

Simple fetch to `http://localhost:8000/api/chat` with JSON body.

## Dependencies

### Backend (`pyproject.toml`, managed by uv)
- `fastapi`
- `uvicorn`
- `pydantic`
- `pydantic-ai`
- `duckduckgo-search` (required by pydantic-ai's DuckDuckGo common tool)
- `logfire`
- `python-dotenv`

### Frontend (`package.json`)
- `react`, `react-dom`
- `tailwindcss` (v4)
- shadcn components: `card`, `button`, `input`, `scroll-area`

## Running

```bash
# Backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

## Task Breakdown

1. **Scaffold backend** — `uv init`, pyproject.toml, install deps
2. **Implement agent** — agent.py with DuckDuckGo tool
3. **Implement FastAPI app** — main.py with CORS, logfire, routes
4. **Implement chat endpoint** — models.py, routes/chat.py with session history
5. **Scaffold frontend** — Vite + React + Tailwind + shadcn init
6. **Implement Chat UI** — Chat.tsx component with shadcn
7. **Implement API client** — api.ts, wire up to Chat component
8. **End-to-end verification** — test full flow manually
