# Story 3-4-sourced-chat-agent: Sourced Chat Agent

## User Story
As a User,
I want the chat agent to answer my questions and cite its sources,
So that I can trust the answers and read the source material.

## Acceptance Criteria
**Given** the combined context from Story 3.3 and the user query
**When** the user submits the query in the NiceGUI interface
**Then** the UI uses the "Task Lock Pattern" (disabling inputs) and calls `src/agents/chat.py`
**And** the chat agent uses Google ADK 2.0 to generate an answer based *only* on the provided context
**And** the answer explicitly cites the filenames of the source Wiki Pages
**And** the UI streams or displays the result and unlocks the inputs.

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
