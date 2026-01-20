import uuid
from pathlib import Path
from typing import Tuple

from src.schemas import SessionRecord
from src.utils import utc_now_iso, safe_mkdir, write_json


SCHEMA_VERSION = "v1"


def create_session(
    output_base_dir: str,
    task_id: str,
    source_type: str,
    source_path: str,
) -> Tuple[SessionRecord, Path]:
    session_id = str(uuid.uuid4())
    session_dir = Path(output_base_dir) / session_id
    safe_mkdir(session_dir)

    session = SessionRecord(
        schema_version=SCHEMA_VERSION,
        session_id=session_id,
        task_id=task_id,
        source_type=source_type,
        source_path=source_path,
        created_utc=utc_now_iso(),
    )

    write_json(session_dir / "session.json", session.to_dict())
    return session, session_dir
