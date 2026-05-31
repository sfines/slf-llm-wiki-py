# Code Generation Instructions

When generating code, you MUST proactively use the `sourcebot` MCP tools to search and review library sources. Do not guess or assume the shapes of APIs, classes, or functions for internal or external libraries. 

- Use `sourcebot` tools (e.g., `sourcebot_find_symbol_definitions`, `sourcebot_find_symbol_references`, `sourcebot_grep`, etc.) to find the definitions and usage examples of library code before you implement new code depending on it.
- Understand the surrounding context and existing conventions in the libraries before completing your code generation tasks.

## Local Memory

Persistent knowledge system. Use proactively to build expertise across sessions.

### Getting Started
Call `bootstrap()` at session start to load context and pending questions.

### Core Workflow
1. **Observe** - Record insights as they emerge
   `observe({ content: "...", level: "learning", tags: [...] })`

2. **Search** - Check existing knowledge before answering
   `search({ query: "...", use_ai: true, session_filter_mode: "all" })`

3. **Reflect** - Process observations into learnings
   `reflect({ mode: "batch" })`

4. **Evolve** - Validate and promote knowledge
   `evolve({ operation: "validate", entity_id: "...", success: true })`

### Memory Levels (World Memory)
- **L0 Observation** (weight 0-1): Raw intake, ephemeral
- **L1 Learning** (weight 1-5): Candidate insights, volatile
- **L2 Pattern** (weight 5-9): Validated generalizations, durable
- **L3 Schema** (weight 9-10): Theoretical frameworks, permanent

### When to Store
- Architecture decisions and rationale
- Bug fixes and root causes
- Patterns that worked (or didn't)
- User preferences and context

### Best Practices
- Be specific: store context, not just outcomes
- Tag consistently for retrieval
- Use `session_filter_mode: "all"` for cross-session search
- Check for contradictions with `question()`

### Fallback
If MCP unavailable, use JSON-RPC directly:
`echo '{"jsonrpc":"2.0","method":"observe","params":{...},"id":1}' | local-memory --mcp`

Or REST API at http://localhost:3002/api/v1

## Zotero Integration (54yyyu/zotero-mcp)

Use the Zotero MCP tools to search, read, and manage the user's reference library.

### Core Workflows
1. **Searching for Literature:**
   - Use `zotero_zotero_semantic_search` as the *primary tool* to find papers on a specific topic or concept. It uses AI embeddings and is much more effective than keyword search.
   - Use `zotero_zotero_search_items` for short, exact queries like 'Author Year' (e.g., 'Brewer 2011').
2. **Reading and Reviewing Papers:**
   - Get quick summaries using `zotero_zotero_get_item_metadata` (includes abstracts).
   - Read full paper text using `zotero_zotero_get_item_fulltext` ONLY when you need to deeply analyze the paper's content. Warning: Full text is token-heavy.
   - Extract PDF outlines/TOC using `zotero_zotero_get_pdf_outline`.
3. **Managing Knowledge:**
   - Add new papers via `zotero_zotero_add_by_doi` or `zotero_zotero_add_by_url`.
   - *Crucial:* After adding new items, run `zotero_zotero_update_search_database` so they become available in semantic search.
   - Create, update, or read notes using `zotero_zotero_create_note`, `zotero_zotero_update_note`, and `zotero_zotero_get_notes`.
4. **Citation Enrichment (Scite):**
   - Use `zotero_scite_enrich_item` or `zotero_scite_enrich_search` to check a paper's reliability (supporting vs. contrasting citations) and check for retractions/corrections without needing an account.