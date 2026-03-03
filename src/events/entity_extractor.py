"""Extract entities (functions, files, errors) from code"""

import re
from typing import List
from src.schemas import EventRecord


class CodeEntityExtractor:
    """Extract entities from code chunks (functions, files, error codes)"""

    # Patterns for code entities
    FUNCTION_PATTERN = r"def\s+([a-zA-Z_]\w*)\s*\("
    CLASS_PATTERN = r"class\s+([a-zA-Z_]\w*)\s*[:\(]"
    FILE_PATTERN = r"(?:[a-zA-Z0-9_\-./]+\.(?:py|js|java|cpp|c|h|txt|json|xml|yaml|yml|md|rb|go|rs|ts))"
    ERROR_PATTERN = r"\b(?:Error|Exception|ValueError|TypeError|KeyError|IndexError|RuntimeError|OSError|IOError|Exception):?\s+([A-Za-z0-9_]+)?"
    ERROR_CODE_PATTERN = r"\b[Ee]\d{3,4}\b|\b[A-Z]+[0-9]{3,}\b"

    def __init__(self):
        # Compile patterns
        self.function_regex = re.compile(self.FUNCTION_PATTERN)
        self.class_regex = re.compile(self.CLASS_PATTERN)
        self.file_regex = re.compile(self.FILE_PATTERN)
        self.error_regex = re.compile(self.ERROR_PATTERN)
        self.error_code_regex = re.compile(self.ERROR_CODE_PATTERN)

    def extract_entities(self, text: str, source_type: str) -> List[str]:
        """
        Extract entities from text.

        Args:
            text: Text to extract entities from
            source_type: Type of source ("reading", "transcript", "code")

        Returns:
            List of extracted entity strings
        """
        if source_type != "code":
            return []

        entities = set()

        # Extract functions
        for match in self.function_regex.finditer(text):
            entities.add(f"fn:{match.group(1)}")

        # Extract classes
        for match in self.class_regex.finditer(text):
            entities.add(f"class:{match.group(1)}")

        # Extract file paths
        for match in self.file_regex.finditer(text):
            entities.add(f"file:{match.group(0)}")

        # Extract error codes
        for match in self.error_code_regex.finditer(text):
            entities.add(f"error_code:{match.group(0)}")

        # Extract error types
        for match in self.error_regex.finditer(text):
            entities.add(f"error:{match.group(0)[:50]}")  # Limit to 50 chars

        return sorted(list(entities))[:10]  # Return top 10 unique entities

    def enrich_events_with_entities(
        self, events: List[EventRecord], source_type: str
    ) -> List[EventRecord]:
        """
        Add entities to events based on their text.

        Args:
            events: List of EventRecord objects
            source_type: Source type ("reading", "transcript", "code")

        Returns:
            Same list with entities populated
        """
        if source_type != "code":
            return events

        for event in events:
            entities = self.extract_entities(event.text, source_type)
            if entities:
                event.entities = entities

        return events
