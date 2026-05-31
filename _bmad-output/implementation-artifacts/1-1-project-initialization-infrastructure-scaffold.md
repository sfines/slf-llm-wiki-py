# Story 1-1-project-initialization-infrastructure-scaffold: Project Initialization & Infrastructure Scaffold

## User Story
As a Developer,
I want to initialize the project using `uv` with the specified ADK 2.0 and NiceGUI dependencies,
So that I have a clean foundation following the starter template constraints.

## Acceptance Criteria
**Given** the project directory exists
**When** the initialization script is run
**Then** `pyproject.toml` and `uv.lock` are configured with `google-genai`, `pydantic`, `nicegui`, `duckdb`, `rank-bm25`, `markitdown`, `pytest`, `pytest-asyncio`, `pytest-mock`, and `ruff`
**And** the basic directory structure (`src/core`, `src/agents`, `src/ui`, `tests/`, `data/input`, `data/output`) is created.

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
