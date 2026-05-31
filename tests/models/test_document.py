from pathlib import Path

from src.models.document import HashedDocument, SummarizedDocument


class TestHashedDocument:
    def test_has_short_hash_field(self):
        doc = HashedDocument(
            source_path=Path("test.md"),
            entity_type_slug="test",
            body="test content",
            frontmatter={},
            content_hash="a" * 64,
            document_id="12345678-1234-5678-1234-567812345678",
            short_hash="abcd1234",
        )
        assert doc.short_hash == "abcd1234"
        assert len(doc.short_hash) == 8

    def test_short_hash_is_optional_for_backwards_compatibility(self):
        doc = HashedDocument(
            source_path=Path("test.md"),
            entity_type_slug="test",
            body="test content",
            frontmatter={},
            content_hash="a" * 64,
            document_id="12345678-1234-5678-1234-567812345678",
        )
        assert hasattr(doc, "short_hash")


class TestSummarizedDocument:
    def test_has_short_hash_field(self):
        doc = SummarizedDocument(
            source_path=Path("test.md"),
            entity_type_slug="test",
            body="test content",
            frontmatter={},
            content_hash="a" * 64,
            document_id="12345678-1234-5678-1234-567812345678",
            summary_content="summary",
            short_hash="abcd1234",
        )
        assert doc.short_hash == "abcd1234"
        assert len(doc.short_hash) == 8

    def test_short_hash_is_optional_for_backwards_compatibility(self):
        doc = SummarizedDocument(
            source_path=Path("test.md"),
            entity_type_slug="test",
            body="test content",
            frontmatter={},
            content_hash="a" * 64,
            document_id="12345678-1234-5678-1234-567812345678",
            summary_content="summary",
        )
        assert hasattr(doc, "short_hash")
