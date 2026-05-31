# Story 1-4-cli-ingestion-loop-ledger-feedback: CLI Ingestion Loop & Ledger Feedback

## User Story
As a Researcher,
I want to execute a CLI command to parse and process my folder of inputs and see a clear ledger of successes, skips, and failures,
So that I know what happened.

## Acceptance Criteria
**Given** a directory of input files
**When** the user runs `src/cli.py`
**Then** it orchestrates the parser and hasher over the directory
**And** it logs a clear ledger to stdout detailing successes, skips, and specific failure reasons using standard library structured logging.

## Epic 2: Knowledge Synthesis & Graph Extraction

Users have their raw parsed texts automatically converted into clean Markdown summaries and structured knowledge graph data (entities/relationships) stored locally.

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
