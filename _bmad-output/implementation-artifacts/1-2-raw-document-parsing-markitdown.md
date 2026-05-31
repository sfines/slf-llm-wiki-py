# Story 1-2-raw-document-parsing-markitdown: Raw Document Parsing (`markitdown`)

## User Story
As a Researcher,
I want the system to read raw files (PDFs, PPTXs, etc.) from `data/input/` and convert them into clean, raw text,
So that the AI can process them.

## Acceptance Criteria
**Given** a valid raw file (e.g., PDF) exists in `data/input/`
**When** `src/core/document_parser.py` is invoked with the file path
**Then** it extracts the text using `markitdown` and returns the raw string
**And** file reading errors are caught and logged gracefully.

## Developer Context
### Technical Requirements
- Follow guidelines in architecture.md and epics.md.
- Ensure proper use of async/await for I/O bounds and multi-agent loops.
- Use structured Pydantic v2.10+ models.
- Required to test with pytest, isolate/mock Vertex AI calls.

### Architecture Compliance
- Ensure separation of concerns (src/core vs src/ui vs src/agents).
- Follow the specific naming conventions and structural patterns (`snake_case` modules, `PascalCase` classes).
- Use `google-genai` and adhere strictly to ADK 2.0 orchestration paradigms.
- No global state. Utilize deterministic hashing.
