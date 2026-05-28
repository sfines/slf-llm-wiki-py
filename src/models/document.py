from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class RawFile(BaseModel):
    """Initial state: A discovered file path and its target entity slug."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_path: Path
    entity_type_slug: str


class ParsedDocument(BaseModel):
    """Second state: The file has been read and converted to Markdown text."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_path: Path
    entity_type_slug: str
    body: str
    frontmatter: Dict[str, Any] = Field(default_factory=dict)


class HashedDocument(BaseModel):
    """Third state: The parsed content has been hashed for identity."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_path: Path
    entity_type_slug: str
    body: str
    frontmatter: Dict[str, Any] = Field(default_factory=dict)
    content_hash: str
    document_id: str  # Deterministic UUID based on hash


class SummarizedDocument(BaseModel):
    """Fourth state: The LLM has generated a summary."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_path: Path
    entity_type_slug: str
    body: str
    frontmatter: Dict[str, Any] = Field(default_factory=dict)
    content_hash: str
    document_id: str
    summary_content: str


class IndexedDocument(BaseModel):
    """Final state: The document and its raw fallback have been written to disk."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_path: Path
    entity_type_slug: str
    document_id: str
    summary_path: Path
    raw_path: Path
