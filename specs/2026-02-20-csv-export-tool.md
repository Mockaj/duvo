# CSV Export Tool for Web Search Results

## Goal

Allow the agent to save web search results as a downloadable CSV file, with an inline download button in the chat UI.

## Scope

**In:** CSV tool, download endpoint, inline download button in chat
**Out:** Bulk export, other file formats, persistent file management

## Requirements

1. Agent can call `save_search_to_csv` with structured search results
2. CSV has columns: date, title, description, sources
3. CSV files stored in `backend/data/` with auto-generated timestamped filenames
4. `GET /api/downloads/{filename}` serves CSV files with path traversal protection
5. Agent includes `[DOWNLOAD:filename.csv]` marker in response text
6. Frontend parses markers and renders inline download buttons
7. Download button triggers browser file download

## Technical Approach

### Backend Tool (`backend/app/tools.py`)

- `SearchResult` Pydantic model: `date`, `title`, `description`, `sources`
- `save_search_to_csv(results: list[SearchResult]) -> str` tool function
- Writes CSV with `csv.writer` to `backend/data/search_YYYY-MM-DD_HH-MM-SS.csv`
- Returns filename string to agent

### Agent Update (`backend/app/agent.py`)

- Import and register `save_search_to_csv` tool
- Update instructions to tell agent to use `[DOWNLOAD:filename]` marker

### Download Route (`backend/app/routes/downloads.py`)

- `GET /api/downloads/{filename}` endpoint
- Filename validation: alphanumeric, hyphens, underscores, dots only
- Returns `FileResponse` with `content-disposition: attachment`
- 404 if file not found

### Frontend (`frontend/src/components/Chat.tsx`)

- Regex `/\[DOWNLOAD:([\w\-\.]+\.csv)\]/g` to detect markers
- Replace markers with styled download buttons
- Button links to `http://localhost:8000/api/downloads/{filename}`

## Edge Cases

- Agent sends malformed marker → frontend ignores, shows raw text
- Path traversal in filename → endpoint rejects with 400
- File deleted before download → endpoint returns 404
- CSV write failure → tool returns error string, agent communicates failure

## Task Breakdown

1. Create `backend/app/tools.py` with model and tool function
2. Update `backend/app/agent.py` to register tool and update instructions
3. Create `backend/app/routes/downloads.py` with download endpoint
4. Register download route in `backend/app/main.py`
5. Update `frontend/src/components/Chat.tsx` to parse markers and render buttons
6. End-to-end verification
