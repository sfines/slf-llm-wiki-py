# SLF LLM Wiki: ADK Implementation Plan

This document outlines the structured plan to fully implement the features of `LeoBR84p/wiki_llm` using Google's Agent Development Kit (ADK) 2.0.

## Phase 1: Core Configuration and Data Structures
Goal: Establish the foundation for how the pipeline handles data, configuration, and deterministic identity.

*   **Task 1.1: Configuration System**
    *   Implement Pydantic `WikiConfig`, `EntityTypeConfig`, `LLMConfig` models based on the original.
    *   Create a configuration loader that supports environment variables (`.env`) and Python-based configuration files.
*   **Task 1.2: Deterministic Identity & Data Models**
    *   Implement the `Document` Pydantic model.
    *   Build the `md_strip()` text cleaning utility.
    *   Implement the deterministic UUID generation based on `SHA-256(md_strip(body))`.

## Phase 2: Robust Ingestion Engine
Goal: Support various file types to match the original tool's flexibility.

*   **Task 2.1: `FilesystemReader`**
    *   Implement the directory scanner.
    *   Integrate `markitdown` for reading `.docx`, `.xlsx`, and `.pptx` files.
    *   Add a pluggable interface for PDF ingestion.
    *   Handle frontmatter extraction (`extract_frontmatter()`) using `markdown-hero` concepts.

## Phase 3: ADK Multi-Agent Generation Workflow
Goal: Replicate the robust "Writer -> Evaluator -> Editor" generation loop using ADK workflows.

*   **Task 3.1: Generation Agents**
    *   Create the `writer_agent`, `evaluator_agent`, and `editor_agent` using ADK's `LlmAgent`.
    *   Bind appropriate Jinja2 templates or dynamic prompts.
*   **Task 3.2: ADK Generation Workflow**
    *   Design and implement an ADK Workflow that routes a document through the Writer, gets a critique from the Evaluator, and passes to the Editor if revisions are needed.
    *   Ensure the raw fallback content is correctly saved alongside the final generated Markdown.

## Phase 4: Taxonomy, Grouping, and Indexing
Goal: Rebuild the organizational capabilities of the wiki.

*   **Task 4.1: Topic Normalization (`topics`)**
    *   Implement an agent workflow to collect terms across documents and use the LLM to normalize them.
    *   Generate Topic taxonomy pages.
*   **Task 4.2: Metadata Groupings (`groups`)**
    *   Implement logic to generate organizational grouping pages based on document metadata.
*   **Task 4.3: Index Generation (`index`)**
    *   Enhance the current `indexer_agent` to build the hierarchical `index.md` based on the full generated taxonomy.

## Phase 5: Consolidation, Linting, and Repair
Goal: Ensure the structural integrity of the generated Markdown using `markdown-hero` and ADK.

*   **Task 5.1: Consolidation (`consolidate`)**
    *   Implement pre-pass structural merging (`markdown_merge`).
    *   Implement an LLM agent to semantically deduplicate merged content.
*   **Task 5.2: Static Linting (`lint`)**
    *   Integrate `markdown-hero.lint()` to detect skipped headings, duplicate anchors, and unclosed fences.
*   **Task 5.3: ADK Repair Agent Workflow (`repair`)**
    *   Translate the LangGraph automatic repair agent into an ADK Workflow.
    *   This workflow should take the `lint_report.md`, traverse the broken files, and iteratively fix structural errors.

## Phase 6: RAG Chat Interface and UI
Goal: Re-implement the query interface.

*   **Task 6.1: BM25 Retrieval System**
    *   Integrate `rank_bm25` for fast, local text retrieval (no vector store needed).
    *   Use `markdown-hero`'s `extract_chunks()` to prepare the index.
*   **Task 6.2: Chat UI (`chat`)**
    *   Rebuild the web interface using `NiceGUI`.
    *   Connect the UI to an ADK conversational agent that uses the BM25 retrieval results as context.

## Phase 7: Polish and Export
*   **Task 7.1: Word Export**
    *   Implement the `.docx` export feature using `markdown-hero`'s `word_format()`.
*   **Task 7.2: Logging**
    *   Implement the structured JSONL `LLMLogger` for tracking run summaries and details.
*   **Task 7.3: CLI Refinement**
    *   Update `main.py` (Click CLI) to map to all newly implemented commands (`setup`, `topics`, `groups`, `consolidate`, `lint`, `repair`, `chat`).
