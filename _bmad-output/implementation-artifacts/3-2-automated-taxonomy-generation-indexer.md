# Story 3-2-automated-taxonomy-generation-indexer: Automated Taxonomy Generation (Indexer)

## User Story
As a User,
I want an agent to rebuild my `index.md` file whenever I ingest new documents,
So that I always have a structured, readable hierarchy of my wiki.

## Acceptance Criteria
**Given** the CLI ingestion loop has finished generating new markdown files
**When** `src/agents/indexer.py` is invoked
**Then** it reads the directory of generated Wiki Pages and generates a hierarchical taxonomy
**And** rewrites `data/output/index.md` with the new structure.

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
