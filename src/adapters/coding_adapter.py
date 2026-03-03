from pathlib import Path
from typing import Dict, Any

from src.adapters.base import BaseAdapter


class CodingDiffAdapter(BaseAdapter):
    """
    Accepts a .diff / patch file and loads it as raw text.
    You can later enhance this to parse files/changed hunks.
    """

    def load(self, path: Path) -> Dict[str, Any]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return {
            "raw_text": text,
            "metadata": {
                "source_kind": "code",
                "path": str(path),
                "format": "diff",
            },
        }
