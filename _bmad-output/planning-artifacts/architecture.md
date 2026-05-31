---
title: "System Architecture"
status: "complete"
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
workflowType: "architecture"
lastStep: 8
completedAt: "2026-05-21"
inputDocuments:
  - "docs/architecture/architecture.md"
  - "docs/architecture/adk_implementation_plan.md"
  - "prd.md"
---

# Architecture Decisions

*This document will be built collaboratively through the architecture workflow.*

## 1. Context & Goals

### Project Context Analysis

**Requirements Overview**

*Functional Requirements:*
The system will ingest raw documents (txt, md, docx, xlsx, pptx, pdf), convert them into markdown, and generate summaries using an AI agent workflow. It will organize these summaries using deterministic ID generation and build a hierarchical taxonomy (`index.md`) based on generated pages. A web-based chat interface (NiceGUI) will allow users to query the generated knowledge base using a BM25 retrieval system.

*Primary Use Case:*
The primary goal is the generation of comprehensive, shareable Markdown artifacts that users can read to quickly digest complex papers and articles. The chat interface is a secondary feature designed for quick, specific Q&A against the corpus. The hierarchical taxonomy (`index.md`) provides human-navigable structure for these readable artifacts.

*Non-Functional Requirements:*
- **Idempotency & Caching:** The system must use content hashing (specifically, SHA256 of the stripped Markdown string) to avoid redundant LLM calls for previously processed files.
- **Modularity:** It must have pluggable interfaces, especially for document ingestion (e.g., adding PDF support).
- **Format Adherence:** AI agents must output strict Markdown without JSON wrappers or metadata.
- **Local Retrieval:** The chat interface must use a fast, local BM25 text retrieval system (with a defined tokenizer dependency), avoiding external vector stores.
- **Human-Readable Output:** The file system must use semantic slugging (`{semantic-slug}-{hash}.md`) so users can easily navigate the raw output directory.
- **Traceability:** The system must maintain a strict linkage between generated summaries and their original source files to enable citations in the chat UI.
- **Testability:** Requires `pytest`, `pytest-asyncio`, and `pytest-mock` to isolate Gemini network calls for cost-effective CI.

**Scale & Complexity:**
- Primary domain: CLI application and Web UI (Python, ADK 2.0, NiceGUI)
- Complexity level: Medium (Multi-agent orchestration, local search, file I/O)
- Estimated architectural components: 5-7 core components (Ingestion, Generation Workflow, Taxonomy/Indexing, Consolidation/Repair, Retrieval/Chat, CLI, Config/Models).

### Technical Constraints & Dependencies
- Must use Google's Agent Development Kit (ADK) 2.0 for agent orchestration.
- Must integrate with Vertex AI Gemini models (requiring specific authentication and environment variables).
- Uses `uv` for dependency management.
- Requires `markitdown` for document parsing and `rank_bm25` for local search.

### Cross-Cutting Concerns Identified
- **Error Handling & Repair:** Robustly handling LLM output format errors and structurally repairing broken Markdown (requires fixture-driven testing).
- **Configuration Management:** Handling environment variables, `.env` files, and Python configuration seamlessly across modules.
- **State Management:** Maintaining deterministic file states and tracking execution flow between agents.
- **CLI Feedback Loop:** Providing a clear, real-time ledger to the user during batch ingestion (successes, caching skips, and explicit failure reasons).

## 2. Core Decisions

## 3. Structural Patterns

## 4. Components & Interfaces

## 5. Security & Deployment


## 3. Structural Patterns

### Starter Template Evaluation

### Primary Technology Domain

CLI application and Web UI based on project requirements analysis

### Starter Options Considered

Given the highly custom nature of this project—requiring Google ADK 2.0 orchestration and a NiceGUI web interface within a single Python application—standard web boilerplate generators (like Next.js or standard FastAPI templates) do not fit the specific constraints. The project is already bootstrapped utilizing `uv` for dependency management with a clear modular layout in `src/`.

Instead of a generic template, the chosen "starter" approach is to leverage the existing modular structure defined in `slf-llm-wiki-py` while standardizing the dependencies and testing stack around the current ADK 2.0 and NiceGUI releases.

### Selected Starter: Custom ADK 2.0 + NiceGUI Architecture

**Rationale for Selection:**
The project demands a specific integration between local file processing, Google GenAI ADK multi-agent orchestration, and a Python-native web interface (NiceGUI). A custom structure managed by `uv`, utilizing `google-genai` (replacing older vertex/genai SDKs) and `nicegui`, provides the precise control needed for this unique workflow without the bloat of a generic web framework.

**Initialization Command:**

The project is already initialized via `uv init`, but the dependency standardization command is:

```bash
uv add google-genai pydantic nicegui rank-bm25 markitdown
uv add --dev pytest pytest-asyncio pytest-mock ruff
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
Python 3.10+ to ensure compatibility with `google-genai` and `nicegui`.

**Styling Solution:**
Tailwind CSS and Quasar Framework (provided out-of-the-box by NiceGUI) for the chat interface.

**Build Tooling:**
`uv` for fast, deterministic dependency resolution and environment management.

**Testing Framework:**
`pytest` combined with `pytest-asyncio` (for asynchronous ADK workflows) and `pytest-mock` (to isolate all Gemini network calls during local CI).

**Code Organization:**
- `src/core/`: Pipeline, File I/O, Hashing, RAG
- `src/agents/`: ADK 2.0 Agent definitions and prompts
- `src/ui/`: NiceGUI chat interface
- `src/models/`: Pydantic data structures

**Development Experience:**
- Rapid iteration via NiceGUI's implicit auto-reload.
- Linting and formatting enforced by `ruff`.

**Note:** Project initialization using this command should be the first implementation story.
## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Data modeling for the document hierarchy (required for hashing and index generation)
- State management for the generation pipeline (idempotency relies on this)
- BM25 tokenizer selection (required for search relevance and testing)

**Important Decisions (Shape Architecture):**
- Component architecture for the NiceGUI interface
- Error handling strategy for LLM calls (retries, fallback)
- Logging format for the CLI feedback loop

**Deferred Decisions (Post-MVP):**
- Multi-user authentication (local application first)
- Remote vector databases (sticking to local BM25 for now)

### Data Architecture

- **Database Choice:** Local filesystem with JSON metadata for documents, AND an embedded **DuckDB** database (`data/output/knowledge_graph.db`) for the knowledge graph. (Rationale: DuckDB provides high-performance relational querying for entities and relationships while maintaining the local, serverless constraint).
- **Data Modeling:** Pydantic `v2.10+` models for strict typing of document metadata and LLM structured outputs (Nodes and Edges).
- **Graph Schema (DuckDB):**
  - **`Nodes` Table:** `id` (hash), `label` (Concept/Author/etc.), `name`, `source_hash` (FK).
  - **`Edges` Table:** `source_node_id`, `target_node_id`, `relationship_type`, `weight`.
- **Hashing Target:** Parsed Markdown string, normalized (strip whitespace/newlines). (Rationale: Avoids cache invalidation due to minor formatting changes in the source documents like PDFs.)
- **Caching Strategy:** Local JSON index file mapping SHA256 hashes to output slugs. (Rationale: Fast, local lookup for idempotency.)

### Authentication & Security

- **Authentication Method:** Google Application Default Credentials (ADC) / `.env` loaded via `python-dotenv`. (Rationale: Required for Vertex AI access using `google-genai`.)
- **Security Middleware:** Not applicable for current local/CLI focus.
- **Data Encryption:** Rely on OS-level encryption for local files. (Rationale: Out of scope for MVP).

### API & Communication Patterns

- **API Design Patterns:** Internal asynchronous Python API using `asyncio`. (Rationale: Required by NiceGUI and efficient for concurrent LLM calls).
- **Error Handling Standards:** Custom exception hierarchy with aggressive logging. LLM parsing errors fall back to raw output or trigger repair agent. (Rationale: Ensures batch ingestion doesn't halt on single document failure).
- **Rate Limiting:** Exponential backoff with `tenacity` for Gemini API calls. (Rationale: Essential for Google Cloud quotas during batch ingestion).

### Frontend Architecture

- **Framework:** NiceGUI `v3.12+` (Rationale: Decided by Starter Template)
- **State Management Approach:** NiceGUI `app.storage.user` or global state classes. (Rationale: Simple session management for chat history).
- **Component Architecture:** Reusable functional components (`ui.chat_message`, `ui.markdown`). (Rationale: NiceGUI idiomatic approach).
- **Styling:** Tailwind CSS (built into NiceGUI). (Rationale: Decided by Starter Template)

### Infrastructure & Deployment

- **Hosting Strategy:** Local execution (CLI) / `localhost` serving (Web UI). (Rationale: Primary requirement is local artifact generation).
- **CI/CD Pipeline:** GitHub Actions running `pytest` (mocked). (Rationale: Standard, free CI).
- **Monitoring and Logging:** Standard library `logging` with structured output for CLI feedback. (Rationale: Meets the transparent feedback requirement).

### Decision Impact Analysis

**Implementation Sequence:**
1. Core Data Models (Pydantic) & Hashing Logic
2. Document Ingestion Pipeline (`markitdown` integration)
3. LLM Agent Workflow (`google-genai` integration with mocked tests)
4. Idempotent Generation & Indexing (Taxonomy creation)
5. BM25 Retrieval Engine
6. NiceGUI Chat Interface

**Cross-Component Dependencies:**
- The Hashing Logic strictly determines caching, meaning the Ingestion Pipeline must finalize the parsed string before Generation can start.
- BM25 Retrieval depends entirely on the Taxonomy indexing structure to map query results back to the original source files for citations.
## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
3 key areas where AI agents could make different choices and break integration:
1. File I/O vs Memory State (When to read from disk vs pass variables)
2. Asynchronous execution patterns in NiceGUI
3. Error handling within ADK multi-agent loops

### Naming Patterns

**File & Directory Naming:**
- Use `snake_case` for all Python modules (`document_parser.py`, `rag_pipeline.py`).
- Output generated documents with `{semantic-slug}-{short_hash}.md` format.

**Code Naming Conventions:**
- Variables and functions: `snake_case` (e.g., `generate_summary()`).
- Classes: `PascalCase` (e.g., `DocumentIngestor`, `NiceGuiChat`).
- Constants/Environment variables: `UPPER_SNAKE_CASE` (e.g., `VERTEX_API_KEY`, `MAX_RETRIES`).

### Structure Patterns

**Project Organization:**
- Business logic MUST be separated from UI logic. `src/core/` handles all data manipulation, decoupled from `src/ui/`.
- All ADK agent definitions go in `src/agents/`, not scattered across business logic.

**File Structure Patterns:**
- Pydantic models must be centralized in `src/models/` to ensure shared data types across ingestion and UI boundaries.

### Format Patterns

**ADK Prompt Formats:**
- System prompts must use markdown formatting for structure (e.g., `## Role`, `## Instructions`).
- LLM outputs must be structured via Pydantic schema validation when internal, but output *raw* markdown when writing final artifacts (no JSON wrappers).

**Data Formats:**
- The index metadata file (`index.json`) must use `camelCase` for keys (e.g., `sourceFile`, `documentHash`) to align with standard JSON patterns, even though Python uses `snake_case` internally (Pydantic aliases should handle this).

### Communication Patterns

**Async execution & Concurrency:**
- Use `async`/`await` for ALL I/O bound operations (file reading, writing, and LLM calls).
- In NiceGUI, use `ui.timer` for polling or background updates, and ensure long-running tasks don't block the main event loop by using `run.io_bound` or `run.cpu_bound` where necessary.
- **Task Lock Pattern:** Any UI component triggering an LLM call must disable its trigger mechanism and acquire a component-level lock until the `await` returns or errors out to prevent concurrent quota exhaustion.

**State Management Patterns:**
- Do not use global variables for UI state. Use NiceGUI's `app.storage` for persistent user state, or class instance variables for isolated component state.

### Process Patterns

**Error Handling & Fallbacks:**
- Do not let LLM parsing failures crash the ingestion loop. Catch validation errors, log them, and either emit a fallback artifact or queue for a repair agent.
- NiceGUI UI should catch `Exception` at the top level of event handlers and display a `ui.notify(..., type='negative')` rather than breaking the UI silently.
- **Markdown Rendering Boundary:** The `ui.markdown` rendering must be wrapped in an error boundary. If the markdown parser fails on invalid LLM output, fallback to rendering the text as a raw `ui.label` wrapped in a `<pre>` tag.

**Data Consistency:**
- **Deterministic Hashing:** The hashing pattern MUST enforce `utf-8` encoding and normalize line endings (`\n`) before hashing the string to ensure cross-platform idempotency.

**Loading State Patterns:**
- NiceGUI interactions triggering LLM calls MUST show a loading indicator (spinner or skeleton) and disable the submit button until the `await` returns.

### Enforcement Guidelines

**All AI Agents MUST:**
- Isolate Vertex AI calls so they can be mocked in tests.
- Strictly adhere to Pydantic definitions for all data crossing module boundaries.
- Generate valid, strict Markdown output when creating final artifacts.

### Pattern Examples

**Good Examples:**
```python
# Good: Pydantic for data boundary, snake_case
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    source_file: str = Field(alias="sourceFile")
    document_hash: str = Field(alias="documentHash")

# Good: Async LLM call with error boundary in UI and Task Lock
async def handle_submit(self):
    if self.loading: return # Task Lock
    self.loading = True
    self.submit_btn.disable()
    try:
        response = await self.rag.query(self.input.value)
        self.display(response)
    except Exception as e:
        ui.notify(f"Query failed: {e}", type="negative")
    finally:
        self.loading = False
        self.submit_btn.enable()
```

**Anti-Patterns:**
```python
# Bad: Blocking UI with synchronous LLM call
def handle_submit(self):
    response = self.rag.query_sync(self.input.value) # Blocks event loop!

# Bad: Using global variables for state
global_chat_history = []

# Bad: Cross-platform hash mismatch
hashlib.sha256(text.encode()) # Uses system default encoding/newlines
```
## Project Structure & Boundaries

### Complete Project Directory Structure

```
slf-llm-wiki-py/
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── docs/
│   ├── architecture/
│   │   ├── architecture.md
│   │   └── adk_implementation_plan.md
│   └── setup.md
├── tests/
│   ├── conftest.py
│   ├── core/
│   │   ├── test_hash.py
│   │   └── test_rag.py
│   ├── agents/
│   │   └── test_mocked_llm.py
│   └── ui/
│       └── test_nicegui_components.py
├── src/
│   ├── main.py                # NiceGUI entry point
│   ├── cli.py                 # CLI ingestion entry point
│   ├── config.py              # Environment loading (Pydantic BaseSettings)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── document_parser.py # markitdown wrapper
│   │   ├── hashing.py         # SHA256 deterministic logic
│   │   ├── indexer.py         # JSON metadata indexer
│   │   ├── graph_store.py     # DuckDB node/edge storage logic
│   │   └── rag_pipeline.py    # rank_bm25 + DuckDB orchestration
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py      # ADK 2.0 base class
│   │   ├── generator.py       # Summarization agent
│   │   ├── graph_extractor.py # Entity/relationship extraction agent
│   │   └── repair.py          # Markdown structure repair agent
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py        # Shared Document metadata schemas
│   │   └── messages.py        # Chat message schemas
│   └── ui/
│       ├── __init__.py
│       ├── app.py             # NiceGUI app orchestration
│       ├── components/
│       │   ├── chat_message.py
│       │   ├── search_bar.py
│       │   └── file_browser.py
│       └── pages/
│           └── chat.py
└── data/                      # Example input data / output target
    ├── input/                 # Raw PDFs/Docs
    └── output/                # Generated Markdown & index.json
```

### Architectural Boundaries

**API Boundaries:**
- The *only* external API boundary is from `src/agents/` to Vertex AI (Gemini) via the `google-genai` SDK.
- Internal boundary: `src/ui/` only communicates with `src/core/rag_pipeline.py` for search and `src/agents/` for chat generation.

**Component Boundaries:**
- UI components (`src/ui/components/`) must only receive primitive data or Pydantic models from `src/models/`. They must not parse files or run hashes themselves.

**Data Boundaries:**
- `src/core/document_parser.py` is the only component allowed to read raw binary files (`.pdf`, `.docx`).
- `src/core/indexer.py` is the only component allowed to read/write `index.json`.

### Requirements to Structure Mapping

**Feature/Epic Mapping:**
- **Epic: Ingestion Pipeline**
  - Read/parse: `src/core/document_parser.py`
  - Hash/cache: `src/core/hashing.py`
  - CLI feedback: `src/cli.py`
- **Epic: AI Generation**
  - Prompts/Gen: `src/agents/generator.py`
  - Fallback/Fixes: `src/agents/repair.py`
- **Epic: Taxonomy & Search**
  - Indexing: `src/core/indexer.py`
  - BM25: `src/core/rag_pipeline.py`
- **Epic: Chat UI**
  - Web Server: `src/main.py`
  - UI Logic: `src/ui/app.py` & `src/ui/pages/chat.py`

**Cross-Cutting Concerns:**
- **Configuration:** Managed globally via `src/config.py` using `pydantic-settings`.

### Integration Points

**Internal Communication:**
- **CLI to Core:** `cli.py` instantiates `DocumentIngestor`, passes paths, and awaits `generator.py` outputs.
- **UI to Core:** `ui/app.py` instantiates `RagPipeline` on load, maintaining the BM25 index in memory for the session.

**Data Flow:**
1. `data/input/*.pdf` → `document_parser.py` (Markdown string)
2. Markdown string → `hashing.py` (SHA256)
3. Markdown string + Hash → `generator.py` (Vertex AI call) AND `graph_extractor.py` (Vertex AI call)
4. Vertex Output → `repair.py` (if invalid markdown)
5. Clean Markdown → File system (`data/output/slug-hash.md`)
6. Graph Entities → `graph_store.py` (inserts into DuckDB)
7. Hash + Metadata → `indexer.py` (updates `index.json`)
8. `index.json` + `data/output/*.md` + DuckDB → `rag_pipeline.py` (on startup)
9. User Query → `rag_pipeline.py` (BM25 + Graph SQL context) → `ui/pages/chat.py` (display)
## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
All decisions align effectively. The choice of `pydantic` heavily supports the structured data demands of both `google-genai` and our JSON metadata indexing approach. The custom ADK + NiceGUI split approach is maintained clearly through directory boundaries.

**Pattern Consistency:**
The specified async execution patterns perfectly support NiceGUI's event loop model while managing the inherently asynchronous nature of Vertex AI API calls.

**Structure Alignment:**
The `src/` directory explicitly enforces the separation of concerns outlined in the architecture, keeping the `markitdown` file I/O safely away from the web serving layers.

### Requirements Coverage Validation ✅

**Epic/Feature Coverage:**
- Document Ingestion is supported by `src/core/document_parser.py` and `src/core/hashing.py`.
- Generative Summarization is supported by the ADK agents in `src/agents/`.
- Local Search/Taxonomy is supported by `src/core/indexer.py` and `src/core/rag_pipeline.py`.
- UI/Chat is supported by the NiceGUI setup in `src/ui/`.

**Functional Requirements Coverage:**
All functional requirements, including idempotent hashing, strict markdown generation, and fast local retrieval, are represented by specific components in the architecture map.

**Non-Functional Requirements Coverage:**
- **Testability:** Fully addressed by the `tests/` structure and mocking requirements.
- **Traceability/Lineage:** Addressed by the `DocumentMetadata` Pydantic boundary model linking queries to source files.
- **Reliability:** Addressed via exponential backoff (Tenacity) and UI error boundaries.

### Implementation Readiness Validation ✅

**Decision Completeness:**
All critical path decisions (hashing targets, state management, dependencies) have been documented.

**Structure Completeness:**
A concrete, file-level map exists to guide scaffolding.

**Pattern Completeness:**
Strict guidelines for naming, concurrency, and error handling have been established.

### Gap Analysis Results

**None Critical:** The architecture is sound for MVP generation.

**Important Gaps:**
- We did not specify the exact chunking strategy for large PDFs prior to sending them to Gemini. (Can be deferred to the implementation of `rag_pipeline.py`/`generator.py`).

### Validation Issues Addressed

- We successfully addressed the risk of cross-platform hash mismatches by mandating newline normalization and UTF-8 encoding.
- We closed the loop on concurrent LLM execution safety in the UI by mandating a "Task Lock" pattern.

### Architecture Completeness Checklist

**Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

**Key Strengths:**
- Extremely specific to the Google ADK 2.0 and NiceGUI constraints.
- Strong focus on determinism (hashing) and cost-control (mocked testing).
- Robust error boundary definitions.

**Areas for Future Enhancement:**
- Advanced chunking strategies for extremely large documents.
- Multi-user authentication if the NiceGUI deployment moves beyond `localhost`.

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently across all components
- Respect project structure and boundaries
- Refer to this document for all architectural questions

**First Implementation Priority:**
```bash
uv add google-genai pydantic nicegui rank-bm25 markitdown
uv add --dev pytest pytest-asyncio pytest-mock ruff
```
