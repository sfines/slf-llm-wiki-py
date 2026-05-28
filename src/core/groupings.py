import logging
from pathlib import Path
from typing import Dict, List

from src.models.config import WikiConfig

logger = logging.getLogger(__name__)


class GroupingBuilder:
    """
    Builds grouping pages based on entity types (and potentially frontmatter).
    """

    def __init__(self, config: WikiConfig):
        self.config = config

    async def build_groups(self):
        """Generates grouping pages."""
        group_dir = self.config.wiki_dir / self.config.grouping.wiki_subdir
        group_dir.mkdir(parents=True, exist_ok=True)

        groups: Dict[str, List[Path]] = {}

        # Group by Entity Type
        for entity_type in self.config.entity_types:
            entity_dir = self.config.wiki_dir / entity_type.wiki_subdir
            if not entity_dir.exists():
                continue

            groups[entity_type.name] = []
            for file_path in entity_dir.glob("*.md"):
                if "raw" in file_path.parts:
                    continue
                groups[entity_type.name].append(file_path)

        logger.info(f"Generating {len(groups)} grouping pages...")
        for group_name, paths in groups.items():
            if not paths:
                continue

            safe_filename = "".join(c if c.isalnum() or c in "-_" else "_" for c in group_name) + ".md"
            group_path = group_dir / safe_filename

            with open(group_path, "w", encoding="utf-8") as f:
                f.write(f"# Group: {group_name}\n\n")
                f.write(f"All documents classified as **{group_name}**:\n\n")
                for p in sorted(paths):
                    rel_path = p.relative_to(self.config.wiki_dir)
                    f.write(f"- [{p.stem}](../{rel_path})\n")
