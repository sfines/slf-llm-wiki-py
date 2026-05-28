import logging
from pathlib import Path
from typing import Dict, List

from src.core.indexer import IndexEntry, JsonIndexer
from src.models.config import WikiConfig

logger = logging.getLogger(__name__)


class TaxonomyBuilder:
    """
    Builds the hierarchical index.md taxonomy based on the JSON index and configuration.
    """

    def __init__(self, config: WikiConfig, indexer: JsonIndexer):
        self.config = config
        self.indexer = indexer

    async def build_taxonomy(self):
        """
        Generates index.md at the root of the wiki_dir by grouping documents
        by their entity type slug and generating links to the summary pages.
        """
        records = self.indexer.get_all_records()
        if not records:
            logger.warning("No records in index. Skipping taxonomy build.")
            return

        logger.info("Building hierarchical taxonomy (index.md)...")

        # Group by entity_type_slug
        grouped_records: Dict[str, List[IndexEntry]] = {}
        for record in records:
            if record.entity_type_slug not in grouped_records:
                grouped_records[record.entity_type_slug] = []
            grouped_records[record.entity_type_slug].append(record)

        index_path = self.config.wiki_dir / "index.md"

        try:
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(f"# {self.config.wiki_name} - Taxonomy\n\n")
                f.write("Welcome to the generated knowledge base. Browse the documents by category below.\n\n")

                for entity_type in self.config.entity_types:
                    docs = grouped_records.get(entity_type.slug, [])
                    if not docs:
                        continue

                    # Sort alphabetically by source filename or summary path
                    docs.sort(key=lambda d: Path(d.source_file).name)

                    f.write(f"## {entity_type.name}\n\n")
                    for doc in docs:
                        # Create relative links from index.md to the summary markdown
                        summary_path = Path(doc.summary_path)
                        rel_path = summary_path.relative_to(self.config.wiki_dir)
                        title = Path(doc.source_file).stem

                        f.write(f"- [{title}]({rel_path})\n")
                    f.write("\n")

            logger.info(f"Successfully generated {index_path.name}")
        except Exception as e:
            logger.error(f"Failed to generate taxonomy index.md: {e}")
