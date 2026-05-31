---
stepsCompleted: [1, 2]
inputDocuments: 
  - "_bmad-output/planning-artifacts/prd.md"
  - "_bmad-output/planning-artifacts/architecture.md"
---

# slf-llm-wiki-py - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for slf-llm-wiki-py, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: The system must parse raw documents (PDF, DOCX, XLSX, etc.) into raw text strings using `markitdown`.
FR2: The system must compute a normalized, UTF-8 SHA256 hash of the parsed string and skip generation if a matching Wiki Page already exists.
FR3: The Summarizer Agent must process the parsed string and output strict, well-structured Markdown (no JSON wrappers) representing the distilled knowledge.
FR4: A Graph Extraction Agent (or a unified summarizer) must extract core entities (e.g., authors, concepts, frameworks) and their relationships (e.g., "USES", "CONTRADICTS") from the parsed text.
FR5: The system must store these entities and relationships locally using DuckDB, allowing for fast, relational queries that simulate a graph data store while maintaining the lightweight, embedded application constraint.
FR6: Following generation, the Indexer Agent must aggregate all available Wiki Pages and rewrite `index.md` into a cohesive, hierarchical structure.
FR7: The system must provide a local chat interface using NiceGUI.
FR8: The chat interface must retrieve relevant chunks from the generated Wiki Pages using a local `rank_bm25` implementation, and augment this context by querying the DuckDB knowledge graph for relevant entity connections.
FR9: The chat agent must use retrieved context to answer the user's query and must cite the source Wiki Pages in its response.

### NonFunctional Requirements

NFR1: The system must use a local filesystem and embedded DuckDB; no external vector stores or graph database servers.
NFR2: Local execution only (`localhost`); auth and cloud deployment are out of scope.
NFR3: Ingestion Success Rate must be >95% of valid raw documents.
NFR4: Idempotency Accuracy must be 100% to save API quota.
NFR5: Retrieval Latency must be under 500ms before sending the prompt to the LLM.

### Additional Requirements

- Starter Template Required: Must initialize using `uv` with specific dependencies: `google-genai pydantic nicegui rank-bm25 markitdown duckdb pytest pytest-asyncio pytest-mock ruff`. (Affects Epic 1 Story 1).
- Python Version: Must be compatible with Python 3.14.
- Data Storage: JSON metadata (`index.json` with camelCase keys) for document metadata + DuckDB database (`data/output/knowledge_graph.db`) with `Nodes` and `Edges` tables.
- API Usage: Must use `google-genai` SDK and mock all Vertex AI network calls in tests using `pytest-mock`.
- Pydantic Models: Must use Pydantic (v2.10+) centralized in `src/models/` for boundaries.
- Async Patterns: Must use `async`/`await` for all I/O and ADK multi-agent loops.
- UI Restrictions: NiceGUI interactions triggering LLM calls must use the "Task Lock Pattern" (disable buttons and show loaders) to prevent concurrent quota exhaustion. UI logic must be separated from business logic.
- Error Handling: Robust exception hierarchy, fallback mechanisms for failed LLM formats, and boundary handling in UI components (e.g., raw label fallback if markdown parsing fails).
- Deterministic Caching: Hash logic must strictly use normalized UTF-8 text strings to prevent cross-platform issues.

### UX Design Requirements

None (No specific UX document available).

### FR Coverage Map

- **FR1:** Epic 1 - Document Parsing (`markitdown`)
- **FR2:** Epic 1 - Content Hashing for Idempotency
- **FR3:** Epic 2 - Knowledge Synthesis (Markdown)
- **FR4:** Epic 2 - Entity & Relationship Extraction
- **FR5:** Epic 2 - Local Graph Storage (DuckDB)
- **FR6:** Epic 3 - Index Generation (`index.md`)
- **FR7:** Epic 3 - Web Interface (NiceGUI)
- **FR8:** Epic 3 - Hybrid Retrieval (BM25 + Graph)
- **FR9:** Epic 3 - Sourced Answers in Chat

## Epic List

### Epic 1: Idempotent Batch Ingestion
Users can drop raw PDFs/documents into a folder and run a command to safely parse them into raw text and hash them to prevent duplicate processing.
**FRs covered:** FR1, FR2

### Epic 2: Knowledge Synthesis & Graph Extraction
Users have their raw parsed texts automatically converted into clean Markdown summaries and structured knowledge graph data (entities/relationships) stored locally.
**FRs covered:** FR3, FR4, FR5

### Epic 3: Local Taxonomy & Hybrid Search Interface
Users can view a dynamically updated `index.md` of all their knowledge and use a local web UI to chat with their knowledge base, receiving sourced answers backed by both text search and graph relationships.
**FRs covered:** FR6, FR7, FR8, FR9

## Epic 1: Idempotent Batch Ingestion

Users can drop raw PDFs/documents into a folder and run a command to safely parse them into raw text and hash them to prevent duplicate processing.

### Story 1.1: Project Initialization & Infrastructure Scaffold

As a Developer,
I want to initialize the project using `uv` with the specified ADK 2.0 and NiceGUI dependencies,
So that I have a clean foundation following the starter template constraints.

**Acceptance Criteria:**

**Given** the project directory exists
**When** the initialization script is run
**Then** `pyproject.toml` and `uv.lock` are configured with `google-genai`, `pydantic`, `nicegui`, `duckdb`, `rank-bm25`, `markitdown`, `pytest`, `pytest-asyncio`, `pytest-mock`, and `ruff`
**And** the basic directory structure (`src/core`, `src/agents`, `src/ui`, `tests/`, `data/input`, `data/output`) is created.

### Story 1.2: Raw Document Parsing (`markitdown`)

As a Researcher,
I want the system to read raw files (PDFs, PPTXs, etc.) from `data/input/` and convert them into clean, raw text,
So that the AI can process them.

**Acceptance Criteria:**

**Given** a valid raw file (e.g., PDF) exists in `data/input/`
**When** `src/core/document_parser.py` is invoked with the file path
**Then** it extracts the text using `markitdown` and returns the raw string
**And** file reading errors are caught and logged gracefully.

### Story 1.3: Content Hashing & Idempotency

As a Researcher,
I want the system to hash my document contents before passing them to the AI,
So that unchanged files are skipped, saving me API costs.

**Acceptance Criteria:**

**Given** a raw parsed text string
**When** `src/core/hashing.py` is invoked
**Then** it normalizes string newlines, enforces UTF-8, and computes a SHA256 hash
**And** `src/cli.py` uses this hash to determine if processing should be skipped (e.g., checking if `{semantic-slug}-{short_hash}.md` already exists).

### Story 1.4: CLI Ingestion Loop & Ledger Feedback

As a Researcher,
I want to execute a CLI command to parse and process my folder of inputs and see a clear ledger of successes, skips, and failures,
So that I know what happened.

**Acceptance Criteria:**

**Given** a directory of input files
**When** the user runs `src/cli.py`
**Then** it orchestrates the parser and hasher over the directory
**And** it logs a clear ledger to stdout detailing successes, skips, and specific failure reasons using standard library structured logging.

## Epic 2: Knowledge Synthesis & Graph Extraction

Users have their raw parsed texts automatically converted into clean Markdown summaries and structured knowledge graph data (entities/relationships) stored locally.

### Story 2.1: Generative Summarizer Agent

As a Researcher,
I want an AI agent to read the parsed text and generate a structured markdown synthesis,
So that I have a clean, readable wiki page.

**Acceptance Criteria:**

**Given** the raw text and file metadata
**When** `src/agents/generator.py` is invoked
**Then** it uses Google ADK 2.0 and `google-genai` to synthesize the text into strict Markdown (no JSON wrappers)
**And** fallback logic catches and logs structural errors, and network calls are isolated for test mocking.

### Story 2.2: Knowledge Graph Extraction Agent

As a Researcher,
I want an AI agent to extract entities and relationships from the text,
So that my knowledge base contains queryable graph data.

**Acceptance Criteria:**

**Given** the raw text and file metadata
**When** `src/agents/graph_extractor.py` is invoked
**Then** it defines strict Pydantic schemas (`Node`, `Edge`, `DocumentMetadata`) to enforce structured JSON output from Gemini
**And** it uses Google ADK 2.0 to extract and return a typed list of nodes and edges based on those schemas.

### Story 2.3: DuckDB Local Graph Storage

As a Researcher,
I want the extracted entities and relationships stored locally in DuckDB,
So that I can query them fast without a remote database.

**Acceptance Criteria:**

**Given** structured Node and Edge data
**When** `src/core/graph_store.py` is invoked
**Then** it ensures an embedded DuckDB instance at `data/output/knowledge_graph.db` with `Nodes` and `Edges` tables exists
**And** successfully inserts the structured data into the tables.

### Story 2.4: Connect Generation to CLI Pipeline

As a Researcher,
I want the generation agents and DuckDB store connected to the main ingestion loop,
So that dropping a file automatically results in markdown and graph data.

**Acceptance Criteria:**

**Given** a successfully hashed input file
**When** the `src/cli.py` ingestion loop runs
**Then** it awaits both `generator.py` and `graph_extractor.py`
**And** it writes the Markdown file to `data/output/{semantic-slug}-{short_hash}.md` and delegates the graph data to `graph_store.py`.

## Epic 3: Local Taxonomy & Hybrid Search Interface

Users can view a dynamically updated `index.md` of all their knowledge and use a local web UI to chat with their knowledge base, receiving sourced answers backed by both text search and graph relationships.

### Story 3.1: Chat Web Interface Scaffold

As a User,
I want a local web interface to interact with my knowledge base,
So that I don't have to search via the CLI.

**Acceptance Criteria:**

**Given** the project is running
**When** I start `src/ui/app.py`
**Then** it launches a NiceGUI web server locally on port 8080
**And** displays a chat interface with a text input, submit button, and a message history pane.

### Story 3.2: Automated Taxonomy Generation (Indexer)

As a User,
I want an agent to rebuild my `index.md` file whenever I ingest new documents,
So that I always have a structured, readable hierarchy of my wiki.

**Acceptance Criteria:**

**Given** the CLI ingestion loop has finished generating new markdown files
**When** `src/agents/indexer.py` is invoked
**Then** it reads the directory of generated Wiki Pages and generates a hierarchical taxonomy
**And** rewrites `data/output/index.md` with the new structure.

### Story 3.3: Hybrid Document Retrieval (BM25 + Graph)

As a User,
I want the system to find relevant context for my chat queries using both text search and graph relations,
So that the AI has the right information to answer my questions.

**Acceptance Criteria:**

**Given** a user query string
**When** `src/core/retriever.py` is called
**Then** it uses `rank-bm25` to find the most relevant chunks from the local Markdown files
**And** it queries DuckDB to pull connected entities based on extracted keywords from the query
**And** returns a combined context string.

### Story 3.4: Sourced Chat Agent

As a User,
I want the chat agent to answer my questions and cite its sources,
So that I can trust the answers and read the source material.

**Acceptance Criteria:**

**Given** the combined context from Story 3.3 and the user query
**When** the user submits the query in the NiceGUI interface
**Then** the UI uses the "Task Lock Pattern" (disabling inputs) and calls `src/agents/chat.py`
**And** the chat agent uses Google ADK 2.0 to generate an answer based *only* on the provided context
**And** the answer explicitly cites the filenames of the source Wiki Pages
**And** the UI streams or displays the result and unlocks the inputs.