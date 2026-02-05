from typing import List, Optional

from src.event_schemas import SourceRef


def link_evidence(
    chunk_id: str,
    chunk_text: str,
    event_text: str,
    chunk_char_start: int = 0,
    chunk_char_end: Optional[int] = None,
) -> List[SourceRef]:
    refs: List[SourceRef] = []
    ct = chunk_text.strip()
    et = event_text.strip()
    if not et:
        refs.append(SourceRef(chunk_id=chunk_id))
        return refs

    et_search = et[:200] if len(et) > 200 else et
    idx = ct.find(et_search)
    if idx >= 0:
        char_start = chunk_char_start + idx
        char_end = char_start + len(et_search)
        if chunk_char_end is not None and char_end > chunk_char_end:
            char_end = chunk_char_end
        refs.append(
            SourceRef(chunk_id=chunk_id, char_start=char_start, char_end=char_end)
        )
    else:
        refs.append(SourceRef(chunk_id=chunk_id))
    return refs
