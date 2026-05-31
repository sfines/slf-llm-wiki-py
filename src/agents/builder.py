import os
from functools import cached_property
from typing import Optional

from google.adk import Agent
from google.adk.models import Gemini
from google.genai import Client

from src.models.config import LLMConfig


class VertexGemini(Gemini):
    @cached_property
    def api_client(self) -> Client:
        location = os.environ.get("VERTEX_LOCATION", "us-central1")
        project = os.environ.get("VERTEX_PROJECT")
        # Initialize the vertex client
        return Client(vertexai=True, location=location, project=project)


def get_model(config: LLMConfig):
    # Depending on config.backend, return the right model
    # For now, we support vertex using the VertexGemini shim
    # In a full implementation, we'd map "openrouter", "ollama", etc.
    # to their respective ADK Model implementations.
    if config.backend == "vertex":
        return VertexGemini(model=config.model_id)
    else:
        # Fallback to standard Gemini (or other supported ADK models in the future)
        return Gemini(model=config.model_id)


def _get_generate_config(config: LLMConfig):
    from google.genai import types

    return types.GenerateContentConfig(temperature=config.temperature)


def create_writer_agent(config: LLMConfig, custom_instruction: Optional[str] = None) -> Agent:
    instruction = (
        custom_instruction
        or """You are an expert technical writer and archivist building an LLM-Wiki.
Your job is to read raw text and synthesize it into a well-structured Markdown summary.
Focus on extracting key concepts, architecture, benefits, drawbacks, and definitions.
Format: Pure Markdown only. Do not output anything outside the markdown content."""
    )

    return Agent(
        name="writer_agent",
        instruction=instruction,
        model=get_model(config),
        generate_content_config=_get_generate_config(config),
    )


def create_evaluator_agent(config: LLMConfig, custom_instruction: Optional[str] = None) -> Agent:
    instruction = (
        custom_instruction
        or """You are an expert editor and reviewer.
Your job is to evaluate a generated wiki page against the original source text.
Provide a critique. If the page is missing key details or contains inaccuracies, note them.
If the page is good as-is, state "APPROVED".
Output your critique clearly."""
    )

    return Agent(
        name="evaluator_agent",
        instruction=instruction,
        model=get_model(config),
        generate_content_config=_get_generate_config(config),
    )


def create_editor_agent(config: LLMConfig, custom_instruction: Optional[str] = None) -> Agent:
    instruction = (
        custom_instruction
        or """You are an expert technical editor.
Your job is to revise a generated wiki page based on the provided critique.
Output the COMPLETE revised Markdown. Do not output anything outside the markdown content."""
    )

    return Agent(
        name="editor_agent",
        instruction=instruction,
        model=get_model(config),
        generate_content_config=_get_generate_config(config),
    )


def create_indexer_agent(config: LLMConfig, custom_instruction: Optional[str] = None) -> Agent:
    instruction = (
        custom_instruction
        or "You are a knowledge graph taxonomy builder.\n"
        "Given a list of existing wiki pages and their descriptions, generate a cohesive "
        "hierarchical `index.md` file.\n"
        "Structure it with logical headings and bullet points linking to the pages "
        "(e.g., `- [Page Title](page-file-name.md)`)."
    )

    return Agent(
        name="indexer_agent",
        instruction=instruction,
        model=get_model(config),
        generate_content_config=_get_generate_config(config),
    )


def create_repair_agent(config: LLMConfig, custom_instruction: Optional[str] = None) -> Agent:
    instruction = (
        custom_instruction
        or "You are a markdown repair agent.\n"
        "You are given a broken markdown file and a linting report showing structural issues "
        "(e.g. broken links, unclosed fences, missing headings).\n"
        "Fix the markdown structure without changing the semantic content.\n"
        "Output the COMPLETE repaired Markdown. Do not output anything outside the markdown content."
    )

    return Agent(
        name="repair_agent",
        instruction=instruction,
        model=get_model(config),
        generate_content_config=_get_generate_config(config),
    )


def create_chat_agent(config: LLMConfig) -> Agent:
    return Agent(
        name="chat_agent",
        instruction="You are a helpful assistant specialized in answering questions "
        "about the wiki content provided in the context.",
        model=get_model(config),
        generate_content_config=_get_generate_config(config),
    )
