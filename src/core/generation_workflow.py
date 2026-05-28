import logging
from typing import Optional

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from src.agents.builder import create_editor_agent, create_evaluator_agent, create_writer_agent
from src.models.config import LLMConfig

logger = logging.getLogger(__name__)


async def run_agent(agent, prompt: str, session_id: str) -> str:
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="wiki_llm", user_id="cli_user", session_id=session_id)

    runner = Runner(agent=agent, app_name="wiki_llm", session_service=session_service)
    msg = Content(role="user", parts=[Part.from_text(text=prompt)])
    events = runner.run_async(user_id="cli_user", session_id=session_id, new_message=msg)

    response_texts = []
    async for e in events:
        if e.content and e.content.parts:
            for p in e.content.parts:
                if p.text:
                    response_texts.append(p.text)

    return "".join(response_texts)


class GenerationWorkflow:
    """
    Manages the Writer -> Evaluator -> Editor pipeline for a single document.
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.writer = create_writer_agent(config)
        self.evaluator = create_evaluator_agent(config)
        self.editor = create_editor_agent(config)

    async def process_document(
        self, document_id: str, filename: str, body: str, max_revisions: int = 1
    ) -> Optional[str]:
        """
        Runs the document through the generation pipeline.
        Returns the generated markdown content.
        """
        doc_id = document_id
        logger.info(f"Starting generation for document {doc_id} ({filename})")

        # 1. Writer Agent
        writer_prompt = f"Please summarize the following source material:\n\n{body}"
        generated_content = await run_agent(self.writer, writer_prompt, session_id=f"writer_{doc_id}")

        if not generated_content:
            logger.error(f"Writer failed to generate content for {doc_id}")
            return None

        revisions = 0
        while revisions < max_revisions:
            logger.info(f"Evaluating generation for {doc_id} (Revision {revisions})")

            # 2. Evaluator Agent
            evaluator_prompt = (
                f"Source Material:\n{body}\n\n"
                f"Generated Page:\n{generated_content}\n\n"
                "Evaluate the generated page. If perfect, reply 'APPROVED'. "
                "Otherwise, provide a critique."
            )
            critique = await run_agent(self.evaluator, evaluator_prompt, session_id=f"evaluator_{doc_id}_{revisions}")

            if "APPROVED" in critique:
                logger.info(f"Evaluator approved content for {doc_id}")
                break

            logger.info(f"Evaluator requested revisions for {doc_id}. Running Editor...")

            # 3. Editor Agent
            editor_prompt = (
                f"Generated Page:\n{generated_content}\n\n"
                f"Critique:\n{critique}\n\n"
                "Please revise the generated page to address the critique. Output ONLY the revised markdown."
            )
            revised_content = await run_agent(self.editor, editor_prompt, session_id=f"editor_{doc_id}_{revisions}")

            if revised_content:
                generated_content = revised_content

            revisions += 1

        return generated_content
