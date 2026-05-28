import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.models.document import IndexedDocument

logger = logging.getLogger(__name__)


class IndexEntry(BaseModel):
    """Represents a single document record in the index.json metadata."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    source_file: str
    document_hash: str
    document_id: str
    entity_type_slug: str
    summary_path: str
    raw_path: str


class IndexMetadata(BaseModel):
    """The complete structure of index.json."""

    records: Dict[str, IndexEntry] = Field(default_factory=dict)


class JsonIndexer:
    """
    Manages reading and writing the JSON metadata index.
    Provides local caching logic and metadata persistence.
    """

    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.metadata = self._load_index()

    def _load_index(self) -> IndexMetadata:
        """Loads index.json if it exists, otherwise returns an empty IndexMetadata."""
        if not self.index_path.exists():
            return IndexMetadata()

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return IndexMetadata.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to load index from {self.index_path}: {e}")
            return IndexMetadata()

    def _save_index(self):
        """Saves the current metadata state to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.index_path, "w", encoding="utf-8") as f:
                # Use model_dump_json with by_alias=True to enforce camelCase keys
                json_str = self.metadata.model_dump_json(by_alias=True, indent=2)
                f.write(json_str)
        except Exception as e:
            logger.error(f"Failed to save index to {self.index_path}: {e}")

    def get_by_hash(self, content_hash: str) -> Optional[IndexEntry]:
        """Checks if a document hash already exists in the index."""
        return self.metadata.records.get(content_hash)

    def get_all_records(self) -> List[IndexEntry]:
        """Returns all records in the index."""
        return list(self.metadata.records.values())

    def add_document(self, content_hash: str, doc: IndexedDocument):
        """
        Adds or updates an IndexedDocument in the JSON index.
        """
        entry = IndexEntry(
            source_file=str(doc.source_path),
            document_hash=content_hash,
            document_id=doc.document_id,
            entity_type_slug=doc.entity_type_slug,
            summary_path=str(doc.summary_path),
            raw_path=str(doc.raw_path),
        )
        self.metadata.records[content_hash] = entry
        self._save_index()
        logger.debug(f"Added document {doc.document_id} to index.")
