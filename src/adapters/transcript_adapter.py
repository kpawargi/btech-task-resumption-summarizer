from pathlib import Path
from typing import Dict, Any

from src.adapters.base import BaseAdapter


class TranscriptAdapter(BaseAdapter):
    def load(self, path: Path) -> Dict[str, Any]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return {
            "raw_text": text,
            "metadata": {
                "source_kind": "transcript",
                "path": str(path),
            },
        }
