# Story 3-1-chat-web-interface-scaffold: Chat Web Interface Scaffold

## User Story
As a User,
I want a local web interface to interact with my knowledge base,
So that I don't have to search via the CLI.

## Acceptance Criteria
**Given** the project is running
**When** I start `src/ui/app.py`
**Then** it launches a NiceGUI web server locally on port 8080
**And** displays a chat interface with a text input, submit button, and a message history pane.

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
