
from src.core.nodes import hashing_node
from src.models.document import HashedDocument, ParsedDocument


class TestHashingNode:
    def test_returns_hashed_document(self, tmp_path):
        parsed = ParsedDocument(
            source_path=tmp_path / "test.md",
            entity_type_slug="test",
            body="test content",
            frontmatter={"title": "Test"},
        )
        event = hashing_node(parsed)
        assert event.output is not None
        assert isinstance(event.output, HashedDocument)

    def test_populates_content_hash(self, tmp_path):
        parsed = ParsedDocument(
            source_path=tmp_path / "test.md",
            entity_type_slug="test",
            body="test content",
            frontmatter={},
        )
        event = hashing_node(parsed)
        hashed: HashedDocument = event.output
        assert hashed.content_hash is not None
        assert len(hashed.content_hash) == 64

    def test_populates_document_id(self, tmp_path):
        parsed = ParsedDocument(
            source_path=tmp_path / "test.md",
            entity_type_slug="test",
            body="test content",
            frontmatter={},
        )
        event = hashing_node(parsed)
        hashed: HashedDocument = event.output
        assert hashed.document_id is not None
        assert len(hashed.document_id) == 36  # UUID format

    def test_populates_short_hash(self, tmp_path):
        parsed = ParsedDocument(
            source_path=tmp_path / "test.md",
            entity_type_slug="test",
            body="test content",
            frontmatter={},
        )
        event = hashing_node(parsed)
        hashed: HashedDocument = event.output
        assert hashed.short_hash is not None
        assert len(hashed.short_hash) == 8
        assert hashed.content_hash.startswith(hashed.short_hash)

    def test_is_deterministic(self, tmp_path):
        parsed1 = ParsedDocument(
            source_path=tmp_path / "test.md",
            entity_type_slug="test",
            body="same content",
            frontmatter={},
        )
        parsed2 = ParsedDocument(
            source_path=tmp_path / "test.md",
            entity_type_slug="test",
            body="same content",
            frontmatter={},
        )
        event1 = hashing_node(parsed1)
        event2 = hashing_node(parsed2)
        assert event1.output.content_hash == event2.output.content_hash
        assert event1.output.short_hash == event2.output.short_hash
        assert event1.output.document_id == event2.output.document_id

    def test_different_content_different_hash(self, tmp_path):
        parsed1 = ParsedDocument(
            source_path=tmp_path / "test.md",
            entity_type_slug="test",
            body="content one",
            frontmatter={},
        )
        parsed2 = ParsedDocument(
            source_path=tmp_path / "test.md",
            entity_type_slug="test",
            body="content two",
            frontmatter={},
        )
        event1 = hashing_node(parsed1)
        event2 = hashing_node(parsed2)
        assert event1.output.content_hash != event2.output.content_hash
        assert event1.output.short_hash != event2.output.short_hash

    def test_preserves_metadata(self, tmp_path):
        parsed = ParsedDocument(
            source_path=tmp_path / "test.md",
            entity_type_slug="manuals",
            body="test content",
            frontmatter={"title": "Test", "author": "Test Author"},
        )
        event = hashing_node(parsed)
        hashed: HashedDocument = event.output
        assert hashed.entity_type_slug == "manuals"
        assert hashed.body == "test content"
        assert hashed.frontmatter == {"title": "Test", "author": "Test Author"}
        assert hashed.source_path == tmp_path / "test.md"
