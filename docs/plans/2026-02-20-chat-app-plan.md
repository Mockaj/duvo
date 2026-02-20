# Duvo Chat App — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a full-stack chat app — React/shadcn frontend + FastAPI/pydantic-ai backend with DuckDuckGo search and Logfire observability.

**Architecture:** Single FastAPI backend with module-level pydantic-ai agent. In-memory session history keyed by UUID. Vite+React frontend with shadcn chat UI. No Docker — manual run.

**Tech Stack:** Python (FastAPI, pydantic-ai, logfire, uv) | TypeScript (Vite, React, Tailwind v4, shadcn)

**Design Doc:** `docs/plans/2026-02-20-chat-app-design.md`

**Parallelization:** Tasks 1-2 (backend scaffold + frontend scaffold) can run in parallel. Tasks 3-5 (backend implementation) are sequential. Task 6-7 (frontend implementation) can run in parallel with backend tasks once scaffolding is done. Task 8 requires both sides complete.

---

## Phase 1: Scaffolding (Parallelizable)

### Task 1: Scaffold Backend

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/.env`
- Create: `backend/app/__init__.py`
- Create: `backend/app/routes/__init__.py`

**Step 1: Init uv project**

```bash
cd /Users/mockaj/Code/duvo
mkdir -p backend
cd backend
uv init --no-readme
```

**Step 2: Add dependencies**

```bash
cd /Users/mockaj/Code/duvo/backend
uv add fastapi uvicorn pydantic pydantic-ai duckduckgo-search logfire python-dotenv
```

**Step 3: Create app package structure**

```bash
mkdir -p /Users/mockaj/Code/duvo/backend/app/routes
```

Create `backend/app/__init__.py`:
```python
```
(empty file)

Create `backend/app/routes/__init__.py`:
```python
```
(empty file)

**Step 4: Create .env template**

Create `backend/.env`:
```env
ANTHROPIC_API_KEY=your-key-here
LOGFIRE_TOKEN=your-token-here
```

**Step 5: Add .env to .gitignore**

Create `backend/.gitignore`:
```
.env
__pycache__/
*.pyc
.venv/
```

**Step 6: Verify uv can resolve deps**

```bash
cd /Users/mockaj/Code/duvo/backend
uv run python -c "import fastapi; import pydantic_ai; import logfire; print('deps OK')"
```
Expected: `deps OK`

**Step 7: Commit**

```bash
git add backend/
git commit -m "feat: scaffold backend with uv and dependencies"
```

---

### Task 2: Scaffold Frontend

**Files:**
- Create: `frontend/` (entire Vite project)
- Modify: `frontend/vite.config.ts` (add path alias)
- Modify: `frontend/tsconfig.json` (add path alias)

**Step 1: Create Vite project**

```bash
cd /Users/mockaj/Code/duvo
npm create vite@latest frontend -- --template react-ts
```

**Step 2: Install dependencies**

```bash
cd /Users/mockaj/Code/duvo/frontend
npm install
npm install tailwindcss @tailwindcss/vite
```

**Step 3: Configure Tailwind v4 in Vite**

Modify `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

**Step 4: Add Tailwind import to CSS**

Replace contents of `frontend/src/index.css`:
```css
@import "tailwindcss";
```

**Step 5: Add path alias to tsconfig**

Modify `frontend/tsconfig.json` — add to `compilerOptions`:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

Also add to `frontend/tsconfig.app.json` `compilerOptions`:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**Step 6: Init shadcn**

```bash
cd /Users/mockaj/Code/duvo/frontend
npx shadcn@latest init -d
```

The `-d` flag uses defaults (New York style, neutral color, CSS variables).

**Step 7: Add shadcn components**

```bash
cd /Users/mockaj/Code/duvo/frontend
npx shadcn@latest add card button input scroll-area
```

**Step 8: Verify it compiles**

```bash
cd /Users/mockaj/Code/duvo/frontend
npm run build
```
Expected: Build succeeds with no errors.

**Step 9: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold frontend with Vite, React, Tailwind v4, shadcn"
```

---

## Phase 2: Backend Implementation (Sequential)

### Task 3: Implement Agent and Models

**Files:**
- Create: `backend/app/agent.py`
- Create: `backend/app/models.py`

**Step 1: Create agent module**

Create `backend/app/agent.py`:
```python
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

agent = Agent(
    'anthropic:claude-sonnet-4-6',
    tools=[duckduckgo_search_tool()],
    instructions='You are a helpful assistant with web search capabilities.',
)
```

**Step 2: Create Pydantic models**

Create `backend/app/models.py`:
```python
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    response: str
    session_id: str
```

**Step 3: Verify imports work**

```bash
cd /Users/mockaj/Code/duvo/backend
uv run python -c "from app.agent import agent; from app.models import ChatRequest, ChatResponse; print('imports OK')"
```
Expected: `imports OK`

**Step 4: Commit**

```bash
git add backend/app/agent.py backend/app/models.py
git commit -m "feat: add pydantic-ai agent with DuckDuckGo tool and request/response models"
```

---

### Task 4: Implement Chat Route

**Files:**
- Create: `backend/app/routes/chat.py`

**Step 1: Create chat route**

Create `backend/app/routes/chat.py`:
```python
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
```

**Step 2: Commit**

```bash
git add backend/app/routes/chat.py
git commit -m "feat: add chat route with multi-turn session history"
```

---

### Task 5: Implement FastAPI App with Logfire

**Files:**
- Create: `backend/app/main.py`

**Step 1: Create main app**

Create `backend/app/main.py`:
```python
from dotenv import load_dotenv

load_dotenv()

import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router

logfire.configure()
logfire.instrument_pydantic_ai()

app = FastAPI(title="Duvo Chat API")

logfire.instrument_fastapi(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
```

Note: `load_dotenv()` is called FIRST so that `ANTHROPIC_API_KEY` and `LOGFIRE_TOKEN` are available before any library reads them. `logfire.instrument_pydantic_ai()` is called before agent import happens via the router to ensure all agent calls are instrumented.

**Step 2: Verify server starts**

```bash
cd /Users/mockaj/Code/duvo/backend
uv run uvicorn app.main:app --port 8000 &
sleep 3
curl -s http://localhost:8000/docs | head -5
kill %1
```
Expected: FastAPI docs HTML response (OpenAPI page).

**Step 3: Commit**

```bash
git add backend/app/main.py
git commit -m "feat: add FastAPI app with CORS, Logfire instrumentation"
```

---

## Phase 3: Frontend Implementation (Parallelizable after Phase 1)

### Task 6: Implement API Client

**Files:**
- Create: `frontend/src/lib/api.ts`

**Step 1: Create API client**

Create `frontend/src/lib/api.ts`:
```typescript
interface ChatRequest {
  message: string;
  session_id: string;
}

interface ChatResponse {
  response: string;
  session_id: string;
}

const API_BASE = "http://localhost:8000";

export async function sendMessage(
  message: string,
  sessionId: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId } as ChatRequest),
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}
```

**Step 2: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat: add API client for chat endpoint"
```

---

### Task 7: Implement Chat UI

**Files:**
- Create: `frontend/src/components/Chat.tsx`
- Modify: `frontend/src/App.tsx`

**Step 1: Create Chat component**

Create `frontend/src/components/Chat.tsx`:
```tsx
import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { sendMessage } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(crypto.randomUUID());
  };

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const userMessage: Message = { role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await sendMessage(trimmed, sessionId);
      const assistantMessage: Message = { role: "assistant", content: res.response };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: Message = {
        role: "assistant",
        content: `Error: ${err instanceof Error ? err.message : "Something went wrong"}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto h-[600px] flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Duvo Chat</CardTitle>
        <Button variant="outline" size="sm" onClick={handleNewChat}>
          New Chat
        </Button>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0">
        <ScrollArea className="h-full p-4" ref={scrollRef}>
          <div className="space-y-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 text-sm whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg px-4 py-2 text-sm text-muted-foreground">
                  Thinking...
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
      <CardFooter className="gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          disabled={isLoading}
        />
        <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
          Send
        </Button>
      </CardFooter>
    </Card>
  );
}
```

**Step 2: Update App.tsx**

Replace `frontend/src/App.tsx`:
```tsx
import { Chat } from "@/components/Chat";

function App() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Chat />
    </div>
  );
}

export default App;
```

**Step 3: Clean up default Vite files**

Delete these files if they exist (they're default Vite boilerplate):
- `frontend/src/App.css`
- `frontend/src/assets/react.svg`
- `frontend/public/vite.svg`

**Step 4: Verify build**

```bash
cd /Users/mockaj/Code/duvo/frontend
npm run build
```
Expected: Build succeeds.

**Step 5: Commit**

```bash
git add frontend/src/
git commit -m "feat: add Chat component with shadcn UI and API integration"
```

---

## Phase 4: Verification

### Task 8: End-to-End Verification

**Prerequisites:** Backend `.env` must have valid `ANTHROPIC_API_KEY` and `LOGFIRE_TOKEN`.

**Step 1: Start backend**

```bash
cd /Users/mockaj/Code/duvo/backend
uv run uvicorn app.main:app --reload --port 8000
```
Expected: Server starts, Logfire configured message appears.

**Step 2: Start frontend (separate terminal)**

```bash
cd /Users/mockaj/Code/duvo/frontend
npm run dev
```
Expected: Dev server on http://localhost:5173

**Step 3: Test basic chat**

Open http://localhost:5173 in browser. Type "Hello, who are you?" and press Enter.
Expected: Agent responds with a greeting identifying itself as a helpful assistant.

**Step 4: Test multi-turn**

Follow up with "What did I just ask you?"
Expected: Agent references the previous message, proving history works.

**Step 5: Test web search**

Ask "What is the latest news about AI today?"
Expected: Agent performs a DuckDuckGo search and returns current information.

**Step 6: Test new chat**

Click "New Chat" button. Ask "What did I ask before?"
Expected: Agent has no knowledge of previous conversation.

**Step 7: Check Logfire**

Open Logfire dashboard. Verify:
- FastAPI request traces appear
- pydantic-ai agent call spans appear
- DuckDuckGo tool call spans appear (from the web search test)

**Step 8: Final commit**

```bash
git add -A
git commit -m "feat: complete Duvo chat app v1"
```
