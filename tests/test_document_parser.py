from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.document_parser import DocumentParseError, parse_document


class TestDocumentParser:
    """Tests for the document parser module."""

    @pytest.mark.asyncio
    async def test_parse_valid_pdf_returns_text(self, tmp_path: Path):
        """Test that a valid PDF file is parsed and returns text."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake pdf content")

        with patch("src.core.document_parser.MarkItDown") as mock_markitdown:
            mock_instance = MagicMock()
            mock_result = MagicMock()
            mock_result.text_content = "Extracted text from PDF"
            mock_instance.convert.return_value = mock_result
            mock_markitdown.return_value = mock_instance

            result = await parse_document(pdf_file)

            assert result == "Extracted text from PDF"
            mock_instance.convert.assert_called_once()

    @pytest.mark.asyncio
    async def test_parse_nonexistent_file_raises_error(self):
        """Test that a nonexistent file raises DocumentParseError."""
        with pytest.raises(DocumentParseError) as exc_info:
            await parse_document("/nonexistent/path/file.pdf")

        assert "File not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_parse_conversion_failure_raises_error(self, tmp_path: Path):
        """Test that markitdown conversion failures are handled gracefully."""
        from markitdown import MarkItDownException

        pdf_file = tmp_path / "corrupt.pdf"
        pdf_file.write_bytes(b"not a real pdf")

        with patch("src.core.document_parser.MarkItDown") as mock_markitdown:
            mock_instance = MagicMock()
            mock_instance.convert.side_effect = MarkItDownException("Conversion failed")
            mock_markitdown.return_value = mock_instance

            with pytest.raises(DocumentParseError) as exc_info:
                await parse_document(pdf_file)

            assert "Failed to parse document" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_parse_supports_various_formats(self, tmp_path: Path):
        """Test that parser supports various document formats."""
        formats = ["pdf", "docx", "pptx", "xlsx"]

        for fmt in formats:
            test_file = tmp_path / f"test.{fmt}"
            test_file.write_bytes(b"dummy content")

            with patch("src.core.document_parser.MarkItDown") as mock_markitdown:
                mock_instance = MagicMock()
                mock_result = MagicMock()
                mock_result.text_content = f"Text from {fmt}"
                mock_instance.convert.return_value = mock_result
                mock_markitdown.return_value = mock_instance

                result = await parse_document(test_file)
                assert result == f"Text from {fmt}"

    @pytest.mark.asyncio
    async def test_parse_uses_to_thread_for_non_blocking(self, tmp_path: Path):
        """Verify that parse_document uses asyncio.to_thread for non-blocking I/O."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"content")

        with patch("src.core.document_parser.MarkItDown") as mock_markitdown:
            mock_instance = MagicMock()
            mock_result = MagicMock()
            mock_result.text_content = "result"
            mock_instance.convert.return_value = mock_result
            mock_markitdown.return_value = mock_instance

            with patch("src.core.document_parser.asyncio.to_thread") as mock_to_thread:
                mock_to_thread.return_value = "result"

                result = await parse_document(test_file)

                mock_to_thread.assert_called_once()
                assert result == "result"
