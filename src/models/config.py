from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    backend: str = Field(
        default="openrouter", description="The LLM backend to use (openrouter, openai, bedrock, ollama, vertex)"
    )
    model_id: str = Field(
        default="mistralai/mistral-7b-instruct:free", description="The model ID to use for generation"
    )
    temperature: float = Field(default=0.0, description="Temperature for generation")


class EntityTypeConfig(BaseModel):
    name: str = Field(..., description="Display name of the entity type (e.g., 'Manual')")
    slug: str = Field(..., description="Folder name to monitor in the raw content dir (e.g., 'manuals')")
    wiki_subdir: str = Field(..., description="Output subdirectory in the wiki (e.g., 'Manuals')")
    prompt_generate: Path = Field(..., description="Path to the prompt template for generating the summary")
    prompt_evaluate: Optional[Path] = Field(None, description="Path to the evaluation prompt template")


class TaxonomyConfig(BaseModel):
    wiki_subdir: str = Field(default="Topics", description="Output subdirectory for topics")
    prompt_extract: Optional[Path] = None
    prompt_normalize: Optional[Path] = None


class GroupingConfig(BaseModel):
    wiki_subdir: str = Field(default="Groups", description="Output subdirectory for groupings")


class WikiConfig(BaseModel):
    wiki_name: str = Field(default="My Wiki", description="The display name of the wiki")
    wiki_dir: Path = Field(default=Path("wiki"), description="The output directory for the wiki")
    content_dir: Path = Field(
        default=Path("content_new"), description="The input directory containing the raw content folders"
    )
    log_dir: Path = Field(default=Path("logs"), description="The output directory for logs")

    llm: LLMConfig = Field(default_factory=LLMConfig)
    entity_types: List[EntityTypeConfig] = Field(default_factory=list)
    taxonomy: TaxonomyConfig = Field(default_factory=TaxonomyConfig)
    grouping: GroupingConfig = Field(default_factory=GroupingConfig)

    prompt_editor: Optional[Path] = Field(None, description="Path to editor prompt")
    prompt_lint: Optional[Path] = Field(None, description="Path to linting prompt")
    prompt_consolidate: Optional[Path] = Field(None, description="Path to consolidate prompt")
    prompt_chat: Optional[Path] = Field(None, description="Path to chat prompt")


def load_config(config_path: Path) -> WikiConfig:
    """Dynamically loads the WikiConfig from a python file."""
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("wiki_config", config_path)
    if not spec or not spec.loader:
        raise ValueError(f"Could not load config from {config_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["wiki_config"] = module
    spec.loader.exec_module(module)

    if hasattr(module, "config"):
        return module.config
    elif hasattr(module, "get_config"):
        return module.get_config()
    else:
        raise ValueError(
            f"Configuration file {config_path} must define a 'config' variable or 'get_config()' function."
        )
