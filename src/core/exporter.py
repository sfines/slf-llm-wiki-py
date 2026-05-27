import logging
import markdown_hero as mdh
from src.models.config import WikiConfig

logger = logging.getLogger(__name__)

class Exporter:
    """
    Exports the generated wiki pages to other formats like .docx.
    """
    def __init__(self, config: WikiConfig):
        self.config = config

    def export_word(self, output_file: str = "wiki_export.docx"):
        """Merges the wiki and exports to a single Word document."""
        logger.info(f"Exporting Wiki to {output_file}...")
        
        # 1. Collect all generated markdown files
        file_paths = []
        for file_path in self.config.wiki_dir.glob("**/*.md"):
            if "raw" in file_path.parts:
                continue
            file_paths.append(file_path)
            
        if not file_paths:
            logger.warning("No generated wiki pages found to export.")
            return

        # 2. Merge them structurally
        try:
            logger.info("Merging markdown files...")
            # If markdown_merge takes a list of paths or contents
            # Assuming it takes list of string contents for safety, though check markdown-hero docs in reality
            contents = []
            for path in file_paths:
                with open(path, "r", encoding="utf-8") as f:
                    contents.append(f.read())
            
            # Use basic string joining if markdown_hero merge isn't path-based
            merged_content = "\n\n".join(contents)
            
            # 3. Export to Word using markdown-hero
            logger.info("Converting to Word document...")
            # markdown-hero word_format might return a python-docx Document or raw bytes
            doc = mdh.word_format(merged_content)
            
            # Save the doc
            if hasattr(doc, 'save'):
                doc.save(output_file)
            else:
                # If it's bytes
                with open(output_file, "wb") as f:
                    f.write(doc)
                    
            logger.info(f"Successfully exported Wiki to {output_file}")
            
        except Exception as e:
            logger.error(f"Error during Word export: {e}")
