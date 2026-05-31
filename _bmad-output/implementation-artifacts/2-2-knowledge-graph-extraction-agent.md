# Story 2-2-knowledge-graph-extraction-agent: Knowledge Graph Extraction Agent

## User Story
As a Researcher,
I want an AI agent to extract entities and relationships from the text,
So that my knowledge base contains queryable graph data.

## Acceptance Criteria
**Given** the raw text and file metadata
**When** `src/agents/graph_extractor.py` is invoked
**Then** it defines strict Pydantic schemas (`Node`, `Edge`, `DocumentMetadata`) to enforce structured JSON output from Gemini
**And** it uses Google ADK 2.0 to extract and return a typed list of nodes and edges based on those schemas.

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
