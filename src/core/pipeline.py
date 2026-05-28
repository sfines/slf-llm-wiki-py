import logging
from pathlib import Path
from typing import List

from google.adk import Event, Workflow

from src.core.generation_workflow import GenerationWorkflow
from src.core.indexer import JsonIndexer
from src.core.nodes import hashing_node, parser_node
from src.core.taxonomy import TaxonomyBuilder
from src.models.config import WikiConfig
from src.models.document import HashedDocument, IndexedDocument, RawFile, SummarizedDocument

logger = logging.getLogger(__name__)


class WikiPipeline:
    def __init__(self, config: WikiConfig):
        self.config = config
        self.config.wiki_dir.mkdir(parents=True, exist_ok=True)
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        self.generation_workflow = GenerationWorkflow(config.llm)
        self.indexer = JsonIndexer(self.config.wiki_dir / "index.json")

        # Build the graph-based workflow per document
        self.ingestion_workflow = Workflow(
            name="document_ingestion_pipeline",
            edges=[("START", parser_node, hashing_node, self.cache_check_node, self.generator_node, self.indexer_node)],
        )

    def discover_files(self) -> List[RawFile]:
        """Scans the configured content directory and returns a list of RawFiles."""
        raw_files: List[RawFile] = []
        if not self.config.content_dir.exists():
            logger.warning(f"Content directory {self.config.content_dir} does not exist.")
            return raw_files

        for entity_type in self.config.entity_types:
            slug_dir = self.config.content_dir / entity_type.slug
            if not slug_dir.exists():
                continue

            for file_path in slug_dir.glob("**/*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    raw_files.append(RawFile(source_path=file_path, entity_type_slug=entity_type.slug))

        return raw_files

    async def cache_check_node(self, hashed_doc: HashedDocument) -> Event:
        """Checks if the document is already generated via index."""
        entity_config = next((e for e in self.config.entity_types if e.slug == hashed_doc.entity_type_slug), None)
        if not entity_config:
            logger.error(f"No configuration found for entity slug: {hashed_doc.entity_type_slug}")
            return Event(output=hashed_doc)

        existing_entry = self.indexer.get_by_hash(hashed_doc.content_hash)

        if existing_entry and Path(existing_entry.summary_path).exists():
            logger.info(
                f"Skipping {hashed_doc.source_path.name} (already in index: {Path(existing_entry.summary_path).name})"
            )
            hashed_doc.frontmatter["_skip_generation"] = True

        return Event(output=hashed_doc)

    async def generator_node(self, hashed_doc: HashedDocument) -> Event:
        """Generates summary using LLM if not skipped."""
        if hashed_doc.frontmatter.get("_skip_generation"):
            return Event(
                output=SummarizedDocument(
                    source_path=hashed_doc.source_path,
                    entity_type_slug=hashed_doc.entity_type_slug,
                    body=hashed_doc.body,
                    frontmatter=hashed_doc.frontmatter,
                    content_hash=hashed_doc.content_hash,
                    document_id=hashed_doc.document_id,
                    summary_content="",
                )
            )

        summary = await self.generation_workflow.process_document(
            document_id=hashed_doc.document_id, filename=hashed_doc.source_path.name, body=hashed_doc.body
        )

        return Event(
            output=SummarizedDocument(
                source_path=hashed_doc.source_path,
                entity_type_slug=hashed_doc.entity_type_slug,
                body=hashed_doc.body,
                frontmatter=hashed_doc.frontmatter,
                content_hash=hashed_doc.content_hash,
                document_id=hashed_doc.document_id,
                summary_content=summary or "",
            )
        )

    async def indexer_node(self, summarized_doc: SummarizedDocument) -> Event:
        """Saves the summarized document and raw document to disk."""
        if not summarized_doc.summary_content:
            # skipped or failed
            return Event(output=None)

        entity_config = next((e for e in self.config.entity_types if e.slug == summarized_doc.entity_type_slug), None)
        if not entity_config:
            logger.error(f"Cannot find entity config for slug: {summarized_doc.entity_type_slug}")
            return Event(output=None)

        out_dir = self.config.wiki_dir / entity_config.wiki_subdir
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = out_dir / f"{summarized_doc.document_id}.md"
        raw_dir = out_dir / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / f"{summarized_doc.document_id}_raw.md"

        if not raw_path.exists():
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(summarized_doc.body)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(summarized_doc.summary_content)

        indexed = IndexedDocument(
            source_path=summarized_doc.source_path,
            entity_type_slug=summarized_doc.entity_type_slug,
            document_id=summarized_doc.document_id,
            summary_path=out_path,
            raw_path=raw_path,
        )
        self.indexer.add_document(summarized_doc.content_hash, indexed)
        return Event(output=indexed)

    async def generate_pages(self, force: bool = False):
        """Reads raw files and generates summaries using the ADK 2.0 Workflow."""
        raw_files = self.discover_files()
        if not raw_files:
            logger.warning("No documents found to process.")
            return

        from google.adk import Runner

        for raw_file in raw_files:
            logger.info(f"Processing {raw_file.source_path.name} via ADK Workflow")
            runner = Runner(agent=self.ingestion_workflow)
            # Send the initial item into the workflow graph
            events = runner.run_async(new_message=raw_file)
            async for _ in events:
                # ADK 2.0 flows: parser_node -> hashing_node -> cache_check_node -> generator_node -> indexer_node
                pass

    async def build_index(self):
        """Builds the human-readable index.md taxonomy."""
        builder = TaxonomyBuilder(self.config, self.indexer)
        await builder.build_taxonomy()
