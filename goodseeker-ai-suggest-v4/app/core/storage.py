import json, os
from typing import Dict, Iterator

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "stories.jsonl")
DATA_PATH = os.path.abspath(DATA_PATH)

def ensure_store():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            pass

def append_story(record: Dict):
    ensure_store()
    with open(DATA_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def iter_stories() -> Iterator[Dict]:
    ensure_store()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue

def get_all() -> list:
    return list(iter_stories())
