# Story 2-1-generative-summarizer-agent: Generative Summarizer Agent

## User Story
As a Researcher,
I want an AI agent to read the parsed text and generate a structured markdown synthesis,
So that I have a clean, readable wiki page.

## Acceptance Criteria
**Given** the raw text and file metadata
**When** `src/agents/generator.py` is invoked
**Then** it uses Google ADK 2.0 and `google-genai` to synthesize the text into strict Markdown (no JSON wrappers)
**And** fallback logic catches and logs structural errors, and network calls are isolated for test mocking.

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
