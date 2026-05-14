import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "records.json")


def _load():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(records):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def add_record(category: str, title: str, result: str):
    """添加一条批改记录。"""
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
    """获取最近limit条记录。"""
    records = _load()
    return records[-limit:][::-1]
