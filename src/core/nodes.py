import json
import logging
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml
from google.adk import Event
from markitdown import MarkItDown

from src.models.document import HashedDocument, IndexedDocument, ParsedDocument, RawFile, SummarizedDocument
from src.utils.text import generate_content_hash, generate_content_uuid

logger = logging.getLogger(__name__)
md = MarkItDown()


def _parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Extracts YAML or JSON frontmatter from the beginning of the text."""
    text = text.strip()
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    frontmatter_str = parts[1].strip()
    body = parts[2].strip()

    try:
        if frontmatter_str.startswith("{"):
            return json.loads(frontmatter_str), body
        else:
            return yaml.safe_load(frontmatter_str) or {}, body
    except Exception as e:
        logger.warning(f"Failed to parse frontmatter: {e}")
        return {}, text


def parser_node(raw_file: RawFile) -> Event:
    """Reads the raw file and converts it to a ParsedDocument."""
    try:
        if raw_file.source_path.suffix.lower() in [".md", ".txt"]:
            with open(raw_file.source_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            logger.info(f"Converting {raw_file.source_path.name} with MarkItDown...")
            result = md.convert(str(raw_file.source_path))
            content = result.text_content

        frontmatter, body = _parse_frontmatter(content)

        parsed = ParsedDocument(
            source_path=raw_file.source_path,
            entity_type_slug=raw_file.entity_type_slug,
            body=body,
            frontmatter=frontmatter,
        )
        return Event(output=parsed)
    except Exception as e:
        logger.error(f"Error reading {raw_file.source_path}: {e}")
        raise


def hashing_node(parsed_doc: ParsedDocument) -> Event:
    """Hashes the parsed document to create a deterministic ID."""
    content_hash = generate_content_hash(parsed_doc.body)
    document_id = generate_content_uuid(parsed_doc.body)

    hashed = HashedDocument(
        source_path=parsed_doc.source_path,
        entity_type_slug=parsed_doc.entity_type_slug,
        body=parsed_doc.body,
        frontmatter=parsed_doc.frontmatter,
        content_hash=content_hash,
        document_id=document_id,
    )
    return Event(output=hashed)


async def cache_check_node(hashed_doc: HashedDocument) -> Event:
    """Checks if the document is already generated. In this implementation,
    it simply forwards it. Actual cache check can be implemented here."""
    # To implement branching in ADK 2.0 graph, we would return a dict or different event type.
    # For now, we will forward the hashed doc. The actual cache check logic requires WikiConfig.
    # We will pass the hashed doc to the generator.
    return Event(output=hashed_doc)


async def indexer_node(summarized_doc: SummarizedDocument) -> Event:
    """Saves the summarized document and raw document to disk."""
    # Assuming the directories are created in the pipeline setup,
    # or we can pass a config via state. For simplicity, we just return the indexed document event.
    indexed = IndexedDocument(
        source_path=summarized_doc.source_path,
        entity_type_slug=summarized_doc.entity_type_slug,
        document_id=summarized_doc.document_id,
        summary_path=Path(f"out/{summarized_doc.document_id}.md"),  # placeholder
        raw_path=Path(f"out/raw/{summarized_doc.document_id}_raw.md"),
    )
    return Event(output=indexed)
