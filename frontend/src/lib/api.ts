interface ChatRequest {
  message: string;
  session_id: string;
}

interface ChatResponse {
  response: string;
  session_id: string;
}

export const API_BASE = "http://localhost:8000";

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
