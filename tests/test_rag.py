import pytest
from pathlib import Path

from src.models.config import WikiConfig
from src.core.indexer import JsonIndexer
from src.core.rag import RagPipeline, tokenize
from src.models.document import IndexedDocument

def test_tokenizer():
    # Test strict regex dependency
    text = "Hello, world! This is 123-test."
    tokens = tokenize(text)
    assert tokens == ["hello", "world", "this", "is", "123", "test"]

@pytest.mark.asyncio
async def test_rag_pipeline(tmp_path):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    
    config = WikiConfig(
        wiki_name="Test Wiki",
        wiki_dir=wiki_dir,
        prompt_editor=None,
        prompt_lint=None,
        prompt_consolidate=None,
        prompt_chat=None
    )
    
    index_path = wiki_dir / "index.json"
    indexer = JsonIndexer(index_path)
    
    summary_path = wiki_dir / "doc1.md"
    summary_path.write_text("The quick brown fox jumps over the lazy dog and the lazy dog jumps over the quick brown fox.\n\nAnother very long paragraph about machine learning that exceeds the fifty character limit.\n\nThird paragraph has completely unrelated content to increase corpus size.\n\nFourth paragraph is also here to balance the BM25 inverse document frequency calculations.", encoding="utf-8")
    
    doc = IndexedDocument(
        source_path=Path("input/doc1.pdf"),
        entity_type_slug="manuals",
        document_id="doc1",
        summary_path=summary_path,
        raw_path=wiki_dir / "doc1_raw.md"
    )
    indexer.add_document("hash1", doc)
    
    # Initialize RAG Pipeline
    rag = RagPipeline(config, indexer)
    print(rag.chunks)
    
    # Test Search
    results = rag.search("fox jumps")
    print("RESULTS:", results)
    assert len(results) == 1
    assert "fox jumps" in results[0].text_snippet
    assert results[0].source_file == "input/doc1.pdf"
    assert results[0].entity_type == "manuals"
    
    # Test missing term
    results_empty = rag.search("cat")
    assert len(results_empty) == 0
