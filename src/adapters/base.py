from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any


class BaseAdapter(ABC):
    @abstractmethod
    def load(self, path: Path) -> Dict[str, Any]:
        """
        Returns a dict with:
        - raw_text: str
        - metadata: dict
        """
        raise NotImplementedError
