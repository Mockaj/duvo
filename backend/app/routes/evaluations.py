import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.models import EvaluationResult

router = APIRouter()

EVALUATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "evaluations"


@router.get("/api/evaluations/{session_id}")
async def get_evaluation(session_id: str) -> EvaluationResult:
    filepath = EVALUATIONS_DIR / f"{session_id}.json"
    if not filepath.is_file():
        raise HTTPException(status_code=404, detail="No evaluation found for this session")

    try:
        entries = json.loads(filepath.read_text())
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=500, detail="Corrupted evaluation data") from exc

    if not entries:
        raise HTTPException(status_code=404, detail="No evaluation found for this session")

    latest = entries[-1]
    return EvaluationResult(**latest)
