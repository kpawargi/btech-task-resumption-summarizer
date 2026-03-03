from pathlib import Path
from typing import Dict, Any

from src.adapters.base import BaseAdapter


class ReadingAdapter(BaseAdapter):
    def load(self, path: Path) -> Dict[str, Any]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return {
            "raw_text": text,
            "metadata": {
                "source_kind": "reading",
                "path": str(path),
            },
        }
