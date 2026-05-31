# Story 1-2: Raw Document Parsing (`markitdown`)

## User Story
As a Researcher,
I want the system to read raw files (PDFs, PPTXs, etc.) from `data/input/` and convert them into clean, raw text,
So that the AI can process them.

## Acceptance Criteria
**Given** a valid raw file (e.g., PDF) exists in `data/input/`
**When** `src/core/document_parser.py` is invoked with the file path
**Then** it extracts the text using `markitdown` and returns the raw string
**And** file reading errors are caught and logged gracefully.

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

## Tasks/Subtasks
- [x] Create `src/core/document_parser.py` with async `parse_document` function
- [x] Write unit tests in `tests/test_document_parser.py`
- [x] Handle file not found errors gracefully
- [x] Handle markitdown conversion errors gracefully
- [x] Ensure async I/O compliance (use `asyncio.to_thread` for blocking calls)

## Dev Agent Record
### Debug Log
- Created `DocumentParseError` exception class for structured error handling
- Used `asyncio.to_thread()` to wrap blocking `MarkItDown.convert()` call
- All 5 unit tests pass, covering happy path, error cases, and async behavior

### Completion Notes
- Implemented async document parser using `markitdown` library
- Proper error handling with custom `DocumentParseError` exception
- Structured logging for debugging and monitoring
- All acceptance criteria met

## File List
- `src/core/document_parser.py` (new)
- `tests/test_document_parser.py` (new)

## Change Log
- 2026-05-30: Story initialized and ready for development
- 2026-05-30: Implementation complete, all tests passing

## Status
review

## Senior Developer Review (AI)
**Review Date:** 2026-05-30
**Review Outcome:** Approve (with minor fix)

### Action Items
- [x] Fix flawed async test (`test_parse_is_async`) - replaced with proper `to_thread` mock verification
- [x] Verified `MarkItDownException` import is correct (exists in root namespace)

### Summary
Implementation is clean and well-structured. Async test was flawed but has been corrected. The `MarkItDownException` import concern was a false positive - the exception is properly exposed in the root namespace.
