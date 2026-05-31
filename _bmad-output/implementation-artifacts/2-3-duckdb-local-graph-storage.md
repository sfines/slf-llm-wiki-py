# Story 2-3-duckdb-local-graph-storage: DuckDB Local Graph Storage

## User Story
As a Researcher,
I want the extracted entities and relationships stored locally in DuckDB,
So that I can query them fast without a remote database.

## Acceptance Criteria
**Given** structured Node and Edge data
**When** `src/core/graph_store.py` is invoked
**Then** it ensures an embedded DuckDB instance at `data/output/knowledge_graph.db` with `Nodes` and `Edges` tables exists
**And** successfully inserts the structured data into the tables.

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
