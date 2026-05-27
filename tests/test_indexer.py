import json
from pathlib import Path

from src.core.indexer import JsonIndexer
from src.models.document import IndexedDocument

def test_indexer_initialization_empty(tmp_path):
    index_path = tmp_path / "index.json"
    indexer = JsonIndexer(index_path)
    
    assert len(indexer.get_all_records()) == 0

def test_indexer_add_and_retrieve(tmp_path):
    index_path = tmp_path / "index.json"
    indexer = JsonIndexer(index_path)
    
    doc = IndexedDocument(
        source_path=Path("input/doc1.pdf"),
        entity_type_slug="manuals",
        document_id="doc-uuid-1",
        summary_path=Path("output/manuals/doc1.md"),
        raw_path=Path("output/raw/manuals/doc1_raw.md")
    )
    
    indexer.add_document("hash123", doc)
    
    # Verify memory
    assert len(indexer.get_all_records()) == 1
    entry = indexer.get_by_hash("hash123")
    assert entry is not None
    assert entry.document_id == "doc-uuid-1"
    
    # Verify disk
    assert index_path.exists()
    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "hash123" in data["records"]
        assert data["records"]["hash123"]["documentId"] == "doc-uuid-1"
        assert data["records"]["hash123"]["entityTypeSlug"] == "manuals"

def test_indexer_load_existing(tmp_path):
    index_path = tmp_path / "index.json"
    data = {
        "records": {
            "hash456": {
                "sourceFile": "input/doc2.pdf",
                "documentHash": "hash456",
                "documentId": "doc-uuid-2",
                "entityTypeSlug": "guides",
                "summaryPath": "output/guides/doc2.md",
                "rawPath": "output/raw/guides/doc2_raw.md"
            }
        }
    }
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    indexer = JsonIndexer(index_path)
    records = indexer.get_all_records()
    
    assert len(records) == 1
    assert records[0].document_id == "doc-uuid-2"
    assert indexer.get_by_hash("hash456") is not None
