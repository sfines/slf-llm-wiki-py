# Story 1-3-content-hashing-idempotency: Content Hashing & Idempotency

## User Story
As a Researcher,
I want the system to hash my document contents before passing them to the AI,
So that unchanged files are skipped, saving me API costs.

## Acceptance Criteria
**Given** a raw parsed text string
**When** `src/core/hashing.py` is invoked
**Then** it normalizes string newlines, enforces UTF-8, and computes a SHA256 hash
**And** `src/cli.py` uses this hash to determine if processing should be skipped (e.g., checking if `{semantic-slug}-{short_hash}.md` already exists).

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
