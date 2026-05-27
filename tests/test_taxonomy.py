import pytest
from pathlib import Path

from src.models.config import WikiConfig, EntityTypeConfig
from src.core.indexer import JsonIndexer
from src.core.taxonomy import TaxonomyBuilder
from src.models.document import IndexedDocument

@pytest.mark.asyncio
async def test_taxonomy_builder(tmp_path):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    
    config = WikiConfig(
        wiki_name="Test Wiki",
        wiki_dir=wiki_dir,
        entity_types=[
            EntityTypeConfig(name="Manuals", slug="manuals", wiki_subdir="Manuals", prompt_generate=Path("p.txt"), prompt_evaluate=None),
            EntityTypeConfig(name="Guides", slug="guides", wiki_subdir="Guides", prompt_generate=Path("p.txt"), prompt_evaluate=None)
        ],
        prompt_editor=None,
        prompt_lint=None,
        prompt_consolidate=None,
        prompt_chat=None
    )
    
    index_path = wiki_dir / "index.json"
    indexer = JsonIndexer(index_path)
    
    doc1 = IndexedDocument(
        source_path=Path("input/doc1.pdf"),
        entity_type_slug="manuals",
        document_id="doc1",
        summary_path=wiki_dir / "Manuals" / "doc1.md",
        raw_path=wiki_dir / "Manuals" / "raw" / "doc1_raw.md"
    )
    
    doc2 = IndexedDocument(
        source_path=Path("input/doc2.pdf"),
        entity_type_slug="guides",
        document_id="doc2",
        summary_path=wiki_dir / "Guides" / "doc2.md",
        raw_path=wiki_dir / "Guides" / "raw" / "doc2_raw.md"
    )
    
    indexer.add_document("hash1", doc1)
    indexer.add_document("hash2", doc2)
    
    builder = TaxonomyBuilder(config, indexer)
    await builder.build_taxonomy()
    
    index_md = wiki_dir / "index.md"
    assert index_md.exists()
    
    content = index_md.read_text(encoding="utf-8")
    assert "# Test Wiki - Taxonomy" in content
    assert "## Manuals" in content
    assert "## Guides" in content
    assert "[doc1](Manuals/doc1.md)" in content
    assert "[doc2](Guides/doc2.md)" in content
