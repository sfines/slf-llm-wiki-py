import json
import uuid
import time
from typing import Dict, Any
from src.models.config import WikiConfig

class WikiLogger:
    """
    Handles structured JSONL logging for the wiki pipeline.
    """
    def __init__(self, config: WikiConfig):
        self.config = config
        self.run_id = str(uuid.uuid4())
        self.timestamp = int(time.time())
        self.log_dir = self.config.log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.summary_file = self.log_dir / f"{self.timestamp}_{self.run_id}_summary.jsonl"
        self.detail_file = self.log_dir / f"{self.timestamp}_{self.run_id}_detail.jsonl"

    def log_summary(self, action: str, status: str, details: Dict[str, Any]):
        """Logs high-level pipeline summaries."""
        entry = {
            "run_id": self.run_id,
            "action": action,
            "status": status,
            "details": details
        }
        with open(self.summary_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def log_detail(self, file_id: str, stage: str, status: str, metrics: Dict[str, Any] = None):
        """Logs specific file-level processing details (e.g. LLM calls)."""
        entry = {
            "run_id": self.run_id,
            "file_id": file_id,
            "stage": stage,
            "status": status,
            "metrics": metrics or {}
        }
        with open(self.detail_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
