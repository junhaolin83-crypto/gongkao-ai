"""人民日报素材库管理：增删改查 + AI自动分析"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_FILE = os.path.join(DATA_DIR, "materials.json")
SEED_FILE = os.path.join(DATA_DIR, "seed.json")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load():
    _ensure_dir()
    if not os.path.exists(DB_FILE):
        # 首次运行：从种子文件导入
        records = _load_seed()
        _save(records)
        return records
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_seed():
    """加载种子数据（预置的人民日报分析文章）。"""
    if os.path.exists(SEED_FILE):
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
        for i, r in enumerate(records):
            r["id"] = i + 1
            r["created_at"] = r.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
        return records
    return []


def _save(records):
    _ensure_dir()
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def add_article(article: dict) -> int:
    """添加一篇文章，返回 id。"""
    records = _load()
    new_id = max((r.get("id", 0) for r in records), default=0) + 1
    article["id"] = new_id
    article["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    records.append(article)
    _save(records)
    return new_id


def update_article(article_id: int, analysis: dict):
    """更新文章的分析结果。"""
    records = _load()
    for r in records:
        if r["id"] == article_id:
            r["analysis"] = analysis
            break
    _save(records)


def get_all_articles():
    """获取所有文章，按日期倒序。"""
    records = _load()
    return sorted(records, key=lambda x: x.get("date", ""), reverse=True)


def delete_article(article_id: int):
    """删除文章。"""
    records = _load()
    records = [r for r in records if r["id"] != article_id]
    _save(records)
