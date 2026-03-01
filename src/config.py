from dataclasses import dataclass


@dataclass(frozen=True)
class SliceConfig:
    token_budget: int = 220
    overlap_tokens: int = 0
    min_chunk_tokens: int = 30
    output_base_dir: str = "outputs"
    text_cleaning: bool = True
