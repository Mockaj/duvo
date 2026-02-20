import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import logfire
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import ModelRequest, ModelResponse, ToolReturnPart, TextPart

EVALUATIONS_DIR = Path(__file__).resolve().parent.parent / "data" / "evaluations"


class EvaluationScore(BaseModel):
    score: int
    reasoning: str


judge_agent = Agent(
    'anthropic:claude-sonnet-4-6',
    output_type=EvaluationScore,
    instructions=(
        'You are an expert evaluator of text summaries. '
        'Given raw source data and a summary produced from that data, '
        'evaluate the summary on these criteria:\n'
        '- Accuracy: Does the summary faithfully represent the source data?\n'
        '- Completeness: Are the key points from the source included?\n'
        '- Conciseness: Is the summary free of unnecessary filler?\n'
        '- Relevance: Does the summary focus on what matters most?\n\n'
        'Return a score from 0-100 and a brief reasoning explaining the score.'
    ),
)


def extract_hn_tool_data(
    messages: list[ModelRequest | ModelResponse],
) -> list[str]:
    """Extract raw content from HN MCP tool returns in the message history."""
    hn_data: list[str] = []
    for msg in messages:
        if isinstance(msg, ModelRequest):
            for part in msg.parts:
                if isinstance(part, ToolReturnPart) and (
                    "hackernews" in part.tool_name.lower()
                    or "hn" in part.tool_name.lower()
                ):
                    content = part.content
                    if isinstance(content, str):
                        hn_data.append(content)
                    else:
                        hn_data.append(str(content))
    return hn_data


def extract_summary(
    messages: list[ModelRequest | ModelResponse],
) -> str | None:
    """Extract the final text output from the last ModelResponse."""
    for msg in reversed(messages):
        if isinstance(msg, ModelResponse):
            for part in msg.parts:
                if isinstance(part, TextPart):
                    return part.content
    return None


async def run_evaluation(session_id: str, hn_data: list[str], summary: str) -> None:
    """Run the judge agent and store results. Designed to be fire-and-forget."""
    try:
        source_text = "\n\n---\n\n".join(hn_data)
        prompt = (
            f"## Source Data\n{source_text}\n\n"
            f"## Summary\n{summary}"
        )

        async with judge_agent:
            result = await judge_agent.run(prompt)

        score = result.output

        logfire.info(
            "HN summary evaluation",
            session_id=session_id,
            score=score.score,
            reasoning=score.reasoning,
        )

        EVALUATIONS_DIR.mkdir(parents=True, exist_ok=True)
        filepath = EVALUATIONS_DIR / f"{session_id}.json"

        entry = {
            "session_id": session_id,
            "score": score.score,
            "reasoning": score.reasoning,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        existing: list[dict] = []
        if filepath.exists():
            try:
                existing = json.loads(filepath.read_text())
            except (json.JSONDecodeError, ValueError):
                existing = []

        existing.append(entry)
        filepath.write_text(json.dumps(existing, indent=2))

    except Exception:
        logfire.exception("Failed to run HN summary evaluation", session_id=session_id)


def maybe_trigger_evaluation(
    session_id: str,
    messages: list[ModelRequest | ModelResponse],
) -> None:
    """Check if HN tools were used and spawn a background evaluation task if so."""
    hn_data = extract_hn_tool_data(messages)
    if not hn_data:
        return

    summary = extract_summary(messages)
    if not summary:
        return

    asyncio.create_task(run_evaluation(session_id, hn_data, summary))
