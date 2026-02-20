import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
FILENAME_PATTERN = re.compile(r"^[\w\-\.]+\.csv$")


@router.get("/api/downloads/{filename}")
async def download_file(filename: str) -> FileResponse:
    if not FILENAME_PATTERN.match(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    filepath = DATA_DIR / filename
    if not filepath.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=filepath,
        filename=filename,
        headers={"content-disposition": f'attachment; filename="{filename}"'},
    )
