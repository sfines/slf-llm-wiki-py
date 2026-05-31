"""Document parser module for converting various file formats to text."""

import asyncio
import logging
from pathlib import Path
from typing import Union

from markitdown import MarkItDown, MarkItDownException

logger = logging.getLogger(__name__)


class DocumentParseError(Exception):
    """Raised when document parsing fails."""

    pass


async def parse_document(file_path: Union[str, Path]) -> str:
    """
    Parse a document file and extract its text content.

    Args:
        file_path: Path to the document file (PDF, DOCX, PPTX, XLSX, etc.)

    Returns:
        Extracted text content as a string.

    Raises:
        DocumentParseError: If the file doesn't exist or parsing fails.
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path

    if not path.exists():
        logger.error(f"File not found: {path}")
        raise DocumentParseError(f"File not found: {path}")

    if not path.is_file():
        logger.error(f"Path is not a file: {path}")
        raise DocumentParseError(f"Path is not a file: {path}")

    try:
        logger.info(f"Parsing document: {path}")

        def _convert() -> str:
            converter = MarkItDown()
            result = converter.convert(str(path))
            return result.text_content

        text = await asyncio.to_thread(_convert)
        logger.info(f"Successfully parsed document: {path}")
        return text

    except MarkItDownException as e:
        logger.error(f"Failed to parse document {path}: {e}")
        raise DocumentParseError(f"Failed to parse document {path}: {e}") from e
    except Exception as e:
        logger.exception(f"Unexpected error parsing document {path}")
        raise DocumentParseError(f"Unexpected error parsing document {path}: {e}") from e
