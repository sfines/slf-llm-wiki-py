from pathlib import Path

from src.core.pipeline import WikiPipeline
from src.models.config import EntityTypeConfig, WikiConfig


def test_workflow_initialization(tmp_path):
    # Mock config
    entity = EntityTypeConfig(name="Test", slug="test", wiki_subdir="test", prompt_generate=Path("test.txt"))

    config = WikiConfig(
        content_dir=tmp_path / "content", wiki_dir=tmp_path / "wiki", log_dir=tmp_path / "logs", entity_types=[entity]
    )

    pipeline = WikiPipeline(config)
    assert pipeline.ingestion_workflow.name == "document_ingestion_pipeline"
    # Basic check to ensure edges are defined
    assert len(pipeline.ingestion_workflow.edges) > 0
