---
title: SLF LLM Wiki
status: draft
created: 2026-05-27
updated: 2026-05-27
---

# PRD: SLF LLM Wiki
*Working title — SLF LLM Wiki.*

## 0. Document Purpose
This Product Requirements Document (PRD) outlines the requirements, user journeys, and core features for the SLF LLM Wiki system. It is designed for developers, AI agents, and architects to align on the scope and functionality of the tool. It builds upon the foundational concept from the Karpathy LLM Wiki pattern and the existing technical architecture (Google ADK 2.0, NiceGUI, local BM25), with the addition of a local knowledge graph.

## 1. Vision
Most traditional RAG systems treat knowledge as ephemeral, rediscovering facts from raw documents on every query. The SLF LLM Wiki flips this model: it incrementally builds and maintains a persistent, compounding markdown wiki AND a structured knowledge graph. When a user drops a new source into the system, the LLM reads it, synthesizes the knowledge into structured markdown pages, extracts entities and relationships into a local DuckDB-backed knowledge graph, flags contradictions, and updates a central index. You own the curation; the LLM handles the tedious bookkeeping. The end result is a highly structured, locally hosted knowledge base that can be instantly searched via a local chat interface and graph queries, accumulating value over time.

## 2. Target User

### 2.1 Primary Persona
**The Knowledge Synthesizer (Researcher, Developer, or Writer)**
A professional who consumes a high volume of complex literature—papers, technical articles, meeting transcripts, or book chapters—and needs a persistent, synthesized structure. They want the benefits of a meticulously maintained Zettelkasten or wiki without the manual overhead of writing summaries, linking concepts, and maintaining indices.

### 2.2 Jobs To Be Done
- Automatically convert raw files (PDFs, PPTXs, notes) into structured, readable markdown summaries.
- Extract entities, concepts, and relationships from papers and articles to form an interconnected, queryable knowledge graph.
- Maintain a constantly up-to-date, hierarchical index (`index.md`) of all knowledge without manual effort.
- Quickly find answers from past reading using a fast, local semantic search, graph data, and chat interface.
- Prevent duplicate effort by ensuring files are never re-processed unnecessarily.

### 2.3 Non-Users (v1)
- Enterprise teams needing multi-tenant, permission-gated cloud wikis.
- Users who expect the system to autonomously browse the web to fetch live data (v1 is local-source only).

### 2.4 Key User Journeys

- **UJ-1. Batch Ingesting New Research.**
  - **Persona + context:** A researcher drops a batch of five new PDFs into the `data/input/` directory to update their wiki.
  - **Entry state:** CLI environment.
  - **Path:** The user runs the ingestion command. The system parses the files via `markitdown` and calculates a SHA256 hash for idempotency. A Gemini agent generates synthesized markdown Wiki Pages, while simultaneously extracting structured graph nodes and edges (entities and relationships). The extracted graph data is inserted into the local embedded DuckDB store. Finally, the Indexer agent rebuilds the `index.md` taxonomy.
  - **Climax:** The CLI outputs a success ledger showing 5 new pages created, graph nodes added, and the index updated.
  - **Resolution:** The user opens the markdown files in their IDE (e.g., Obsidian) to browse the updated knowledge graph.
  - **Edge case:** If a file was previously processed, the system skips it instantly to save API costs.

- **UJ-2. Interrogating the Knowledge Base.**
  - **Persona + context:** The user needs to recall a specific architectural pattern from a paper they ingested last month.
  - **Entry state:** User navigates to the local NiceGUI web interface.
  - **Path:** The user types a query in the chat bar. The system uses local BM25 retrieval against the generated Wiki Pages and queries DuckDB for relevant entity relationships to pull context, then prompts Gemini to generate an answer.
  - **Climax:** The chat interface streams back the answer, explicitly citing the specific Wiki Page(s) and relationships it used.
  - **Resolution:** The user gets the answer and can click/reference the specific generated page for deeper reading.

## 3. Glossary

- **Raw Material** — Original source files (papers, articles, notes) ingested from the file system.
- **Wiki Page** — The structured Markdown output generated from Raw Material, focusing on insights, definitions, and controversies.
- **Index** — The central taxonomy document (`index.md`) that logically organizes all generated Wiki Pages.
- **Knowledge Graph** — The structured collection of entities (nodes) and their relationships (edges) extracted from Raw Material, stored relationally.
- **Content Hash** — A SHA256 digest of Raw Material used to ensure idempotency, cache outputs, and avoid redundant LLM calls.
- **Agent** — An AI-powered actor (implemented via Google GenAI ADK 2.0). Specific roles include the **Summarizer Agent**, **Graph Extraction Agent**, and the **Indexer Agent**.

## 4. Features

### 4.1 Automated Idempotent Ingestion
**Description:** The system watches or processes a target directory of raw documents, converting them to clean markdown summaries without repeating work for unchanged files.

**Functional Requirements:**
#### FR-1: Document Parsing
The system must parse raw documents (PDF, DOCX, XLSX, etc.) into raw text strings using `markitdown`. Realizes UJ-1.

#### FR-2: Content Hashing for Idempotency
The system must compute a normalized, UTF-8 SHA256 hash of the parsed string and skip generation if a matching Wiki Page already exists. Realizes UJ-1.

#### FR-3: Knowledge Synthesis
The Summarizer Agent must process the parsed string and output strict, well-structured Markdown (no JSON wrappers) representing the distilled knowledge. Realizes UJ-1.

### 4.2 Knowledge Graph Extraction & Storage
**Description:** The system extracts structured entities and relationships from the text and stores them in a local format optimized for graph-like queries.

**Functional Requirements:**
#### FR-4: Entity & Relationship Extraction
A Graph Extraction Agent (or a unified summarizer) must extract core entities (e.g., authors, concepts, frameworks) and their relationships (e.g., "USES", "CONTRADICTS") from the parsed text. Realizes UJ-1.

#### FR-5: Local Graph Storage (DuckDB)
The system must store these entities and relationships locally using DuckDB, allowing for fast, relational queries that simulate a graph data store while maintaining the lightweight, embedded application constraint. Realizes UJ-1.

### 4.3 Automated Taxonomy & Indexing
**Description:** A background agent maintains the organizational structure of the wiki, ensuring no page is orphaned.

**Functional Requirements:**
#### FR-6: Index Generation
Following generation, the Indexer Agent must aggregate all available Wiki Pages and rewrite `index.md` into a cohesive, hierarchical structure. Realizes UJ-1.

### 4.4 Local Retrieval & Chat Interface
**Description:** A local web interface allowing users to converse with their knowledge base using fast BM25 retrieval and graph queries.

**Functional Requirements:**
#### FR-7: Web Interface
The system must provide a local chat interface using NiceGUI. Realizes UJ-2.

#### FR-8: Hybrid Retrieval (BM25 + Graph)
The chat interface must retrieve relevant chunks from the generated Wiki Pages using a local `rank_bm25` implementation, and augment this context by querying the DuckDB knowledge graph for relevant entity connections. Realizes UJ-2.

#### FR-9: Sourced Answers
The chat agent must use retrieved context to answer the user's query and must cite the source Wiki Pages in its response. Realizes UJ-2.

## 5. Non-Goals (Explicit)
- **Dedicated Graph/Vector Databases:** The system will not use complex external vector stores (e.g., Pinecone, Milvus) or dedicated, server-based graph databases (e.g., Neo4j). It strictly relies on fast, local BM25 token matching and embedded DuckDB for graph relations.
- **Multi-user / Cloud Hosting:** The web interface is strictly for local execution (`localhost`). Auth and cloud deployment are out of scope.
- **Automated Web Searching:** The system will not browse the internet to fill data gaps during ingestion. It strictly processes local raw files.

## 6. MVP Scope

### 6.1 In Scope
- CLI ingestion pipeline for local files (`data/input/`).
- Idempotent caching using SHA256 hashes and a local JSON metadata store.
- ADK 2.0 integration for Summarizer, Graph Extraction, and Indexer agents via Gemini models.
- DuckDB integration for storing and querying extracted entities and relationships.
- BM25 local text retrieval mechanism.
- NiceGUI interactive chat interface for querying.

### 6.2 Out of Scope for MVP
- Browser extensions for web clipping (to be handled by external tools like Obsidian Web Clipper).
- Automated slide deck (Marp) generation.
- Dynamic data visualization generation (matplotlib) in chat.

## 7. Success Metrics

**Primary**
- **SM-1**: **Ingestion Success Rate** — >95% of valid raw documents successfully parse, extract graph data, and generate a valid Wiki Page without unhandled exceptions. Validates FR-1, FR-3, FR-4.
- **SM-2**: **Idempotency Accuracy** — 100% of unchanged files are successfully skipped on subsequent ingestion runs, saving API quota. Validates FR-2.

**Secondary**
- **SM-3**: **Retrieval Latency** — Local BM25 and DuckDB graph queries execute in under 500ms before sending the prompt to the LLM. Validates FR-8.

## 8. Open Questions
1. Do we want to implement chunking for extremely large PDFs before summarization and entity extraction, or rely entirely on Gemini's large context window?
2. Should the system maintain a chronological `log.md` (as suggested by the gist) in addition to the hierarchical `index.md`?
3. How should we map graph queries back into the natural language chat experience in NiceGUI (e.g., automated tool calling by the chat agent vs. deterministic context injection alongside BM25)?

## 9. Assumptions Index
- [ASSUMPTION] The user has sufficient Gemini API quota to process their initial batch of raw documents.
- [ASSUMPTION] BM25 tokenization combined with relational DuckDB queries will be sufficient for semantic retrieval without needing true semantic vector embeddings for the anticipated scale of a personal wiki.
- [ASSUMPTION] DuckDB's relational table structure (e.g., a Nodes table and an Edges table) will be sufficient to model the knowledge graph effectively.