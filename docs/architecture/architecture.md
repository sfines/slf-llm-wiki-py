# SLF LLM Wiki Architecture

This document describes the architecture of the SLF LLM Wiki Python/Google ADK 2.0 implementation, utilizing Domain-Driven Design (DDD) concepts to outline its core artifacts, contexts, and operational flows.

## Ubiquitous Language

The following terms define the core language shared across the domain:

*   **Raw Material / Raw Content**: Original source files (papers, articles, notes) ingested from the file system.
*   **Wiki Page / Summary Page**: The structured Markdown output generated from Raw Material, focusing on insights, definitions, and controversies.
*   **Index**: The central taxonomy document (`index.md`) that logically organizes all generated Wiki Pages.
*   **Agent**: An AI-powered actor (implemented via Google GenAI ADK 2.0) with specific instructions and capabilities.
*   **Summarizer Agent**: The specialized Agent responsible for synthesizing Raw Material into Wiki Pages.
*   **Indexer Agent**: The specialized Agent responsible for organizing a list of Wiki Pages into a cohesive Index.
*   **Pipeline**: The orchestration layer that manages file reading, hashing, agent invocation, and writing results to the file system.
*   **Content Hash**: A SHA256 digest of Raw Material used to ensure idempotency, cache outputs, and avoid redundant LLM calls.

## Bounded Contexts

The system is organized into three primary bounded contexts:

### 1. Ingestion & Storage Context
*   **Responsibility**: Manages all file system interactions. It reads Raw Material, computes Content Hashes, checks for the existence of previous Wiki Pages (caching/idempotency), and persists the output of the Agents.
*   **Key Components**: `core.pipeline.WikiPipeline`, File I/O operations, Hashing logic (`_get_content_hash`).

### 2. Knowledge Generation Context
*   **Responsibility**: Transforms unstructured Raw Material into structured, distilled knowledge.
*   **Key Components**: `agents.builder.create_summarizer_agent`, `core.pipeline.run_agent`.
*   **Model**: Utilizes Vertex AI Gemini models with strict instructions to output pure Markdown without metadata or JSON wrappers.

### 3. Taxonomy & Indexing Context
*   **Responsibility**: Observes the current state of generated knowledge and creates a navigational structure mapping the domain.
*   **Key Components**: `agents.builder.create_indexer_agent`, `core.pipeline.run_agent`.

## Flow of Processing

### 1. Generate Pages Operation (`generate`)
This operation converts raw research into structured wiki entries.

1.  **Scan**: The `WikiPipeline` scans the defined raw directory (e.g., `raw/`) for `.md` and `.txt` files.
2.  **Read & Hash**: For each file, the content is read into memory and a Content Hash (SHA256) is generated.
3.  **Idempotency Check**: The pipeline checks if a Wiki Page named `{stem}-{hash}.md` already exists in the destination directory. If it does (and `--force` is not passed), the file is skipped.
4.  **Prompt Construction**: A prompt combining the generation instruction and the raw content is created.
5.  **Agent Invocation**: The `summarizer_agent` is invoked within a new ephemeral ADK session.
6.  **Persistence**: The Markdown response is written to the file system.

### 2. Build Index Operation (`index`)
This operation organizes the generated pages into a readable map.

1.  **Discovery**: The `WikiPipeline` scans the wiki directory for all generated `.md` files (excluding `index.md` itself).
2.  **Aggregation**: A list of existing Wiki Pages is compiled.
3.  **Agent Invocation**: The `indexer_agent` is invoked with a prompt containing the list of pages, instructed to build a hierarchical taxonomy.
4.  **Persistence**: The resulting structured taxonomy is saved as `wiki/index.md`.

### 3. Full Pipeline Operation (`run-all`)
Executes the **Generate Pages Operation** followed sequentially by the **Build Index Operation** to ensure the index accurately reflects the newly generated content.
