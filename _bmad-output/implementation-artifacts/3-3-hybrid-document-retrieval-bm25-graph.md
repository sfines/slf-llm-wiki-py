# Story 3-3-hybrid-document-retrieval-bm25-graph: Hybrid Document Retrieval (BM25 + Graph)

## User Story
As a User,
I want the system to find relevant context for my chat queries using both text search and graph relations,
So that the AI has the right information to answer my questions.

## Acceptance Criteria
**Given** a user query string
**When** `src/core/retriever.py` is called
**Then** it uses `rank-bm25` to find the most relevant chunks from the local Markdown files
**And** it queries DuckDB to pull connected entities based on extracted keywords from the query
**And** returns a combined context string.

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
