import os
import json

BASE_DIR = "data"

def ensure_dirs(task_id, session_id):
    paths = [
        f"{BASE_DIR}/inputs/{task_id}/{session_id}",
        f"{BASE_DIR}/context/{task_id}/{session_id}",
        f"{BASE_DIR}/outputs/{task_id}/{session_id}",
    ]
    for p in paths:
        os.makedirs(p, exist_ok=True)

def save_input(task_id, session_id, text):
    ensure_dirs(task_id, session_id)
    path = f"{BASE_DIR}/inputs/{task_id}/{session_id}/input.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def load_context(task_id, session_id):
    path = f"{BASE_DIR}/context/{task_id}/{session_id}/ContextBundle.json"
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("context_text", "")

def save_context(task_id, session_id, text):
    path = f"{BASE_DIR}/context/{task_id}/{session_id}/ContextBundle.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"context_text": text}, f, indent=2)

def save_output(task_id, session_id, summary):
    path = f"{BASE_DIR}/outputs/{task_id}/{session_id}/resume_summary.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
