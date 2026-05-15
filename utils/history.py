import json
import os
import tempfile
from datetime import datetime

# 数据目录：优先本地，云部署时回退到临时目录
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOCAL_DATA = os.path.join(_SRC_DIR, "data")


def _get_data_dir():
    try:
        os.makedirs(_LOCAL_DATA, exist_ok=True)
        test = os.path.join(_LOCAL_DATA, ".rw_test")
        with open(test, "w") as f:
            f.write("ok")
        os.remove(test)
        return _LOCAL_DATA
    except (OSError, PermissionError):
        alt = os.path.join(tempfile.gettempdir(), "gongkao-ai")
        os.makedirs(alt, exist_ok=True)
        return alt


HISTORY_FILE = os.path.join(_get_data_dir(), "records.json")


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
