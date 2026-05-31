import json
import logging
from pathlib import Path
from typing import Dict, List

import markdown_hero as mdh

from src.agents.builder import create_repair_agent
from src.core.generation_workflow import run_agent
from src.models.config import WikiConfig

logger = logging.getLogger(__name__)


class LinterAndRepairer:
    """
    Runs markdown_hero static linting on the wiki, produces a report, and optionally
    triggers the ADK Repair agent to iteratively fix broken files.
    """

    def __init__(self, config: WikiConfig):
        self.config = config
        self.repair_agent = create_repair_agent(config.llm)

    def run_lint(self) -> Dict[Path, List[mdh.Issue]]:
        """Runs markdown-hero linting over all generated markdown files."""
        logger.info("Running static markdown linting...")
        issues: Dict[Path, List[mdh.Issue]] = {}

        for file_path in self.config.wiki_dir.glob("**/*.md"):
            if "raw" in file_path.parts:
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Assume mdh.lint returns a list of dictionaries describing issues
                file_issues = mdh.lint(content)
                if file_issues:
                    issues[file_path] = file_issues
            except Exception as e:
                logger.error(f"Error linting {file_path}: {e}")

        # Generate lint report
        report_path = self.config.wiki_dir / "lint_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Wiki Lint Report\n\n")
            if not issues:
                f.write("No linting issues found. 🚀\n")
            else:
                for path, file_issues in issues.items():
                    rel_path = path.relative_to(self.config.wiki_dir)
                    f.write(f"## [{rel_path}]({rel_path})\n")
                    for issue in file_issues:
                        f.write(f"- {issue.rule}: {issue.message} (Line {issue.line})\n")
                    f.write("\n")

        logger.info(f"Linting complete. Found issues in {len(issues)} files. Report saved to {report_path.name}")
        return issues

    async def run_repair(self, issues: Dict[Path, List[mdh.Issue]]):
        """Iterates through broken files and uses the repair agent to fix them."""
        if not issues:
            logger.info("No issues to repair.")
            return

        logger.info(f"Initiating automatic repair on {len(issues)} files...")
        for file_path, file_issues in issues.items():
            logger.info(f"Repairing {file_path.name}...")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            issues_dicts = [{"rule": i.rule, "message": i.message, "line": i.line} for i in file_issues]

            prompt = (
                "The following markdown file has structural issues detected by the linter.\n"
                f"Issues: {json.dumps(issues_dicts)}\n\n"
                "Please fix these issues and output the corrected markdown. Do NOT change the core text.\n"
                f"Content:\n{content}"
            )

            try:
                fixed_content = await run_agent(self.repair_agent, prompt, session_id=f"repair_{file_path.stem}")
                if fixed_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(fixed_content)
                    logger.info(f"  -> Fixed and saved {file_path.name}")
            except Exception as e:
                logger.error(f"  -> Failed to repair {file_path.name}: {e}")
