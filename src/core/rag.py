import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from rank_bm25 import BM25Okapi

from src.models.config import WikiConfig
from src.core.indexer import JsonIndexer, IndexEntry

logger = logging.getLogger(__name__)

# Strict tokenizer dependency: regex targeting alphanumeric tokens
TOKENIZER_REGEX = re.compile(r'\b\w+\b')

def tokenize(text: str) -> List[str]:
    """Standard regex tokenizer for BM25 to ensure deterministic matching."""
    return TOKENIZER_REGEX.findall(text.lower())

class SearchResult(BaseModel):
    score: float
    text_snippet: str
    source_file: str
    summary_path: str
    entity_type: str

class RagPipeline:
    """
    Local BM25 text retrieval system that links queries back to the original
    source files via the JSON index.
    """
    def __init__(self, config: WikiConfig, indexer: JsonIndexer):
        self.config = config
        self.indexer = indexer
        self.chunks: List[Dict[str, Any]] = []
        self.bm25: Optional[BM25Okapi] = None
        self._build_index()

    def _build_index(self):
        """Builds the BM25 index strictly from the JSON metadata and summary artifacts."""
        logger.info("Building BM25 Retrieval Index...")
        tokenized_corpus = []
        
        records = self.indexer.get_all_records()
        for record in records:
            summary_path = Path(record.summary_path)
            if not summary_path.exists():
                logger.warning(f"Summary missing for {record.document_id}, skipping indexing.")
                continue
                
            try:
                with open(summary_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Basic chunking: split by paragraphs to keep chunks manageable.
                paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50]
                
                if not paragraphs:
                    # Fallback to whole file if no clear paragraphs
                    paragraphs = [content]
                    
                for para in paragraphs:
                    self.chunks.append({
                        'record': record,
                        'text': para
                    })
                    tokenized_corpus.append(tokenize(para))
                    
            except Exception as e:
                logger.error(f"Failed to read/chunk {summary_path}: {e}")
                
        if tokenized_corpus:
            self.bm25 = BM25Okapi(tokenized_corpus)
            logger.info(f"Index built successfully with {len(self.chunks)} chunks from {len(records)} documents.")
        else:
            logger.warning("No chunks extracted. BM25 Index is empty.")

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Retrieve top k chunks for the given query, preserving strict lineage."""
        if not self.bm25:
            return []
            
        tokenized_query = tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            score = scores[idx]
            if score > 0:
                chunk = self.chunks[idx]
                record: IndexEntry = chunk['record']
                
                # Create a strict lineage result
                results.append(SearchResult(
                    score=score,
                    text_snippet=chunk['text'],
                    source_file=record.source_file,
                    summary_path=record.summary_path,
                    entity_type=record.entity_type_slug
                ))
                
        return results
