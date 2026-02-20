import csv
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class SearchResult(BaseModel):
    date: str
    title: str
    description: str
    sources: str


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def save_search_to_csv(results: list[SearchResult]) -> str:
    """Save search results to a CSV file for the user to download.

    Args:
        results: List of search results with date, title, description, and sources fields.

    Returns:
        The filename of the saved CSV file, or an error message if saving failed.
    """
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"search_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        filepath = DATA_DIR / filename

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "title", "description", "sources"])
            for r in results:
                writer.writerow([r.date, r.title, r.description, r.sources])

        return filename
    except Exception as e:
        return f"Error saving CSV: {e}"
