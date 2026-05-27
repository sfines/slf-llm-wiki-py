from pathlib import Path
from src.models.config import WikiConfig, EntityTypeConfig, LLMConfig

config = WikiConfig(
    wiki_name="Test Wiki",
    wiki_dir=Path("wiki"),
    content_dir=Path("content_new"),
    log_dir=Path("logs"),
    llm=LLMConfig(backend="vertex", model_id="gemini-3.1-pro-preview"),
    entity_types=[
        EntityTypeConfig(
            name="Manual",
            slug="manuals",
            wiki_subdir="Manuals",
            prompt_generate=Path("prompts/summarize.md")
        )
    ]
)
