import logging
from google.adk.agents.llm_agent import LlmAgent
from src.models.config import WikiConfig
from src.agents.builder import get_model

logger = logging.getLogger(__name__)

class Consolidator:
    """
    Finds duplicated concepts in the wiki, merges them structurally using markdown_hero,
    and semantic deduplicates them using an LLM.
    """
    def __init__(self, config: WikiConfig):
        self.config = config
        self.agent = self._create_consolidation_agent()

    def _create_consolidation_agent(self) -> LlmAgent:
        return LlmAgent(
            name="consolidation_agent",
            instruction=(
                "You are an expert technical editor. You are given a merged markdown document that contains duplicated or overlapping sections from multiple source documents. "
                "Your task is to semantically deduplicate the content. "
                "1. Keep all unique information.\n"
                "2. Remove redundant paragraphs or sentences.\n"
                "3. Ensure the final document flows logically under the provided headings.\n"
                "Output ONLY valid markdown."
            ),
            model=get_model(self.config.llm)
        )

    async def run_consolidation(self):
        """Find candidate duplicates (e.g. within groups or topics), merge, and rewrite."""
        # For simplicity in this implementation, we will look for files with similar names or 
        # in the same grouping to consolidate. In a real scenario, this would use similarity search.
        # Alternatively, we just look at the topics generated and consolidate the original files 
        # that share the same topic heavily.
        
        logger.info("Consolidation phase initiated.")
        logger.warning("Consolidation logic requires semantic grouping to identify merge candidates. (Stubbed for now).")
        
        # Example of how markdown_hero is used if candidates are found:
        # merged_md = mdh.markdown_merge([file_path_1, file_path_2], dedupe_headings=True)
        # final_md = await run_agent(self.agent, merged_md, session_id="consolidation")
