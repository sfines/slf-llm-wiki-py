from pathlib import Path

import pytest

from src.core.indexer import IndexEntry
from src.core.pipeline import WikiPipeline
from src.models.config import EntityTypeConfig, WikiConfig
from src.models.document import HashedDocument, SummarizedDocument


class TestIndexerNode:
    @pytest.fixture
    def pipeline(self, tmp_path):
        content_dir = tmp_path / "content"
        wiki_dir = tmp_path / "wiki"
        log_dir = tmp_path / "logs"
        content_dir.mkdir()
        wiki_dir.mkdir()
        log_dir.mkdir()

        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        prompt_generate = prompts_dir / "generate.md"
        prompt_generate.write_text("Generate prompt")

        config = WikiConfig(
            content_dir=content_dir,
            wiki_dir=wiki_dir,
            log_dir=log_dir,
            entity_types=[
                EntityTypeConfig(
                    name="Manual",
                    slug="manuals",
                    wiki_subdir="manuals",
                    prompt_generate=prompt_generate,
                )
            ],
        )
        return WikiPipeline(config)

    @pytest.mark.asyncio
    async def test_outputs_file_with_slug_short_hash_naming(self, pipeline, tmp_path):
        summarized = SummarizedDocument(
            source_path=tmp_path / "test.pdf",
            entity_type_slug="manuals",
            body="test content",
            frontmatter={},
            content_hash="abcd1234567890",
            document_id="test-uuid",
            summary_content="This is the summary",
            short_hash="abcd1234",
        )

        event = await pipeline.indexer_node(summarized)
        indexed = event.output

        assert indexed is not None
        assert indexed.summary_path.name == "manuals-abcd1234.md"
        assert indexed.summary_path.parent.name == "manuals"
        assert indexed.summary_path.exists()

    @pytest.mark.asyncio
    async def test_outputs_raw_file_with_same_convention(self, pipeline, tmp_path):
        summarized = SummarizedDocument(
            source_path=tmp_path / "test.pdf",
            entity_type_slug="manuals",
            body="test content",
            frontmatter={},
            content_hash="abcd1234567890",
            document_id="test-uuid",
            summary_content="This is the summary",
            short_hash="wxyz9876",
        )

        event = await pipeline.indexer_node(summarized)
        indexed = event.output

        assert indexed is not None
        assert indexed.raw_path.name == "manuals-wxyz9876_raw.md"
        assert indexed.raw_path.parent.name == "raw"
        assert indexed.raw_path.exists()


class TestCacheCheckNode:
    @pytest.fixture
    def pipeline(self, tmp_path):
        content_dir = tmp_path / "content"
        wiki_dir = tmp_path / "wiki"
        log_dir = tmp_path / "logs"
        content_dir.mkdir()
        wiki_dir.mkdir()
        log_dir.mkdir()

        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        prompt_generate = prompts_dir / "generate.md"
        prompt_generate.write_text("Generate prompt")

        config = WikiConfig(
            content_dir=content_dir,
            wiki_dir=wiki_dir,
            log_dir=log_dir,
            entity_types=[
                EntityTypeConfig(
                    name="Manual",
                    slug="manuals",
                    wiki_subdir="manuals",
                    prompt_generate=prompt_generate,
                )
            ],
        )
        return WikiPipeline(config)

    @pytest.mark.asyncio
    async def test_skips_if_file_exists_with_new_naming(self, pipeline, tmp_path):
        wiki_dir = pipeline.config.wiki_dir
        manuals_dir = wiki_dir / "manuals"
        manuals_dir.mkdir(parents=True, exist_ok=True)

        existing_file = manuals_dir / "manuals-abcd1234.md"
        existing_file.write_text("Existing content")

        # Add the index entry that cache_check_node looks for
        pipeline.indexer.metadata.records["existing-hash"] = IndexEntry(
            source_file="test.pdf",
            document_hash="existing-hash",
            document_id="existing-uuid",
            entity_type_slug="manuals",
            summary_path=str(existing_file),
            raw_path="out/raw/test_raw.md",
        )

        hashed = HashedDocument(
            source_path=tmp_path / "test.pdf",
            entity_type_slug="manuals",
            body="test content",
            frontmatter={},
            content_hash="existing-hash",
            document_id="existing-uuid",
            short_hash="abcd1234",
        )

        event = await pipeline.cache_check_node(hashed)
        result = event.output

        assert result.frontmatter.get("_skip_generation") is True

    @pytest.mark.asyncio
    async def test_does_not_skip_if_file_missing(self, pipeline, tmp_path):
        hashed = HashedDocument(
            source_path=tmp_path / "test.pdf",
            entity_type_slug="manuals",
            body="new content",
            frontmatter={},
            content_hash="new-hash",
            document_id="new-uuid",
            short_hash="new12345",
        )

        event = await pipeline.cache_check_node(hashed)
        result = event.output

        assert result.frontmatter.get("_skip_generation") is None

    @pytest.mark.asyncio
    async def test_still_checks_index_for_backward_compatibility(self, pipeline, tmp_path):
        from src.models.document import IndexedDocument

        existing_doc = IndexedDocument(
            source_path=Path("old.pdf"),
            entity_type_slug="manuals",
            document_id="old-uuid",
            summary_path=pipeline.config.wiki_dir / "manuals" / "old-output.md",
            raw_path=pipeline.config.wiki_dir / "manuals" / "raw" / "old-output_raw.md",
        )

        (pipeline.config.wiki_dir / "manuals").mkdir(parents=True, exist_ok=True)
        existing_doc.summary_path.write_text("Old content")
        pipeline.indexer.add_document("backward-compat-hash", existing_doc)

        hashed = HashedDocument(
            source_path=tmp_path / "test.pdf",
            entity_type_slug="manuals",
            body="old content",
            frontmatter={},
            content_hash="backward-compat-hash",
            document_id="old-uuid",
            short_hash="old12345",
        )

        event = await pipeline.cache_check_node(hashed)
        result = event.output

        assert result.frontmatter.get("_skip_generation") is True


class TestGeneratorNode:
    @pytest.fixture
    def pipeline(self, tmp_path, mocker):
        content_dir = tmp_path / "content"
        wiki_dir = tmp_path / "wiki"
        log_dir = tmp_path / "logs"
        content_dir.mkdir()
        wiki_dir.mkdir()
        log_dir.mkdir()

        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        prompt_generate = prompts_dir / "generate.md"
        prompt_generate.write_text("Generate prompt")

        config = WikiConfig(
            content_dir=content_dir,
            wiki_dir=wiki_dir,
            log_dir=log_dir,
            entity_types=[
                EntityTypeConfig(
                    name="Manual",
                    slug="manuals",
                    wiki_subdir="manuals",
                    prompt_generate=prompt_generate,
                )
            ],
        )

        pipeline = WikiPipeline(config)
        mocker.patch.object(
            pipeline.generation_workflow,
            "process_document",
            return_value="Generated summary",
        )
        return pipeline

    @pytest.mark.asyncio
    async def test_passes_short_hash_to_summarized_document(self, pipeline, tmp_path):
        hashed = HashedDocument(
            source_path=tmp_path / "test.pdf",
            entity_type_slug="manuals",
            body="test content",
            frontmatter={},
            content_hash="test-hash",
            document_id="test-uuid",
            short_hash="test1234",
        )

        event = await pipeline.generator_node(hashed)
        result: SummarizedDocument = event.output

        assert result.short_hash == "test1234"
