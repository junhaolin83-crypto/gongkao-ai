import json
import os
import tempfile
from datetime import datetime

_history_file = None


def _init():
    global _history_file
    if _history_file is not None:
        return
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_data = os.path.join(src_dir, "data")
    try:
        os.makedirs(local_data, exist_ok=True)
        test = os.path.join(local_data, ".rw")
        with open(test, "w") as f:
            f.write("1")
        os.remove(test)
        _history_file = os.path.join(local_data, "records.json")
    except Exception:
        alt = os.path.join(tempfile.gettempdir(), "gongkao-ai")
        os.makedirs(alt, exist_ok=True)
        _history_file = os.path.join(alt, "records.json")


def _load():
    _init()
    if not os.path.exists(_history_file):
        return []
    with open(_history_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(records):
    _init()
    with open(_history_file, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def add_record(category: str, title: str, result: str):
    records = _load()
    records.append({
        "id": len(records) + 1,
        "category": category,
        "title": title,
        "result": result,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    _save(records)


def get_records(limit=20):
    records = _load()
    return records[-limit:][::-1]
