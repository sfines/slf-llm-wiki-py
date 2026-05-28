import logging

from nicegui import ui

from src.core.generation_workflow import GenerationWorkflow
from src.core.indexer import JsonIndexer
from src.core.rag import RagPipeline
from src.models.config import WikiConfig

logger = logging.getLogger(__name__)


class WikiChatApp:
    def __init__(self, config: WikiConfig):
        self.config = config

        index_path = self.config.wiki_dir / "index.json"
        if not index_path.exists():
            logger.warning(f"Index missing at {index_path}. Generating empty index.")
            self.indexer = JsonIndexer(index_path)
        else:
            self.indexer = JsonIndexer(index_path)

        self.rag_pipeline = RagPipeline(config, self.indexer)
        self.generation_workflow = GenerationWorkflow(config.llm)

    def _build_ui(self):
        ui.markdown("# Wiki Chat").classes("text-3xl font-bold mb-4")

        chat_messages = ui.column().classes("w-full max-w-2xl mx-auto space-y-4 mb-16")

        with ui.row().classes("w-full max-w-2xl mx-auto fixed bottom-4 items-center"):
            user_input = (
                ui.input(placeholder="Ask the wiki...")
                .classes("flex-grow")
                .on("keydown.enter", lambda e: send_message())
            )

            async def send_message():
                question = user_input.value
                if not question:
                    return
                user_input.value = ""

                with chat_messages:
                    ui.markdown(f"**You:** {question}").classes("bg-blue-100 p-2 rounded-lg text-right")

                # 1. Retrieve context
                results = self.rag_pipeline.search(question, top_k=3)

                if not results:
                    with chat_messages:
                        ui.markdown("**Wiki:** No relevant context found in the wiki.").classes(
                            "bg-gray-100 p-2 rounded-lg"
                        )
                    return

                context_str = "\n\n---\n\n".join([f"Source: {r.source_file}\n\n{r.text_snippet}" for r in results])

                prompt = (
                    f"Context from the Wiki:\n{context_str}\n\n"
                    f"User Question: {question}\n\n"
                    "Please answer the question based only on the provided context."
                    "Include citations to the source file where appropriate."
                )

                # 2. Get LLM response
                try:
                    # Using the base process_document logic for standard adk 2.0 generation
                    response = await self.generation_workflow.process_document(
                        document_id="chat", filename="chat", body=prompt
                    )
                except Exception as e:
                    logger.error(f"Chat error: {e}")
                    response = "Sorry, I encountered an error processing that request."

                # Format citations
                citations_md = "\n\n**Sources:**\n"
                seen_sources = set()
                for r in results:
                    if r.source_file not in seen_sources:
                        citations_md += f"- `{r.source_file}`\n"
                        seen_sources.add(r.source_file)

                with chat_messages:
                    ui.markdown(f"**Wiki:** {response}{citations_md}").classes("bg-gray-100 p-2 rounded-lg")

            ui.button("Send", on_click=send_message).classes("ml-2")

    def run(self):
        """Starts the NiceGUI server."""
        self._build_ui()
        logger.info("Starting Chat UI...")
        ui.run(title=f"{self.config.wiki_name} Chat", port=8080, show=False)
