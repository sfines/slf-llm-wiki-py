# Story 2-4-connect-generation-to-cli-pipeline: Connect Generation to CLI Pipeline

## User Story
As a Researcher,
I want the generation agents and DuckDB store connected to the main ingestion loop,
So that dropping a file automatically results in markdown and graph data.

## Acceptance Criteria
**Given** a successfully hashed input file
**When** the `src/cli.py` ingestion loop runs
**Then** it awaits both `generator.py` and `graph_extractor.py`
**And** it writes the Markdown file to `data/output/{semantic-slug}-{short_hash}.md` and delegates the graph data to `graph_store.py`.

## Epic 3: Local Taxonomy & Hybrid Search Interface

Users can view a dynamically updated `index.md` of all their knowledge and use a local web UI to chat with their knowledge base, receiving sourced answers backed by both text search and graph relationships.

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
