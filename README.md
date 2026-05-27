# SLF LLM Wiki (Python ADK Implementation)

This project is a Python/Google ADK 2.0 re-implementation of the concepts found in [`wiki_llm`](https://github.com/LeoBR84p/wiki_llm) and the local `slf-llm-wiki`. It replaces the LangChain/LangGraph architecture with Google's Agent Development Kit (ADK) 2.0.

## Architecture

The project consists of an Agentic pipeline to ingest raw research material, extract its core concepts, and organize it into a structured markdown wiki.

- **`main.py`**: The CLI entrypoint.
- **`src/agents/builder.py`**: Contains the Google ADK `Agent` definitions (Summarizer, Indexer).
- **`src/core/pipeline.py`**: Manages the Agent runner and file I/O operations (hashing, checking existences, maintaining the `index.md`).

## Installation

This project is managed with `uv`.

```bash
# Sync dependencies
uv sync
```

## Usage

Set your Google Cloud project and location to use Vertex AI. Make sure you are authenticated with Application Default Credentials (`gcloud auth application-default login`).

```bash
export VERTEX_PROJECT="your-google-cloud-project-id"
export VERTEX_LOCATION="us-central1" # Optional, defaults to us-central1
```

To run the tools:

```bash
# See all options
uv run python main.py --help

# Generate summaries for all documents in the `raw/` folder
uv run python main.py generate

# Build or rebuild the index.md based on the generated wiki/ folder
uv run python main.py index

# Run the complete pipeline
uv run python main.py run-all
```

## How It Works

1. **Ingestion**: The script reads files from `raw/`.
2. **Generation (`summarizer_agent`)**: Instead of a LangGraph evaluator, ADK 2.0 uses a tightly scoped prompt instruction with a `LlmAgent` to extract insights, controversies, and key terms in pure markdown. 
3. **Storage**: The output is saved deterministically via content hashing, preventing unnecessary API calls for previously processed files.
4. **Taxonomy (`indexer_agent`)**: An agent takes the layout of `wiki/` and generates the cohesive `index.md` knowledge map.
