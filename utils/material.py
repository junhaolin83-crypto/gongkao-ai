"""人民日报素材库管理：增删改查 + 话题标签 + 智能搜索"""

import json
import os
import tempfile
from datetime import datetime

# 数据目录：优先本地，云部署时回退到临时目录
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOCAL_DATA = os.path.join(_SRC_DIR, "data")


def _get_data_dir():
    """返回可写的数据目录（云部署时本地可能只读）。"""
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


DATA_DIR = _get_data_dir()
DB_FILE = os.path.join(DATA_DIR, "materials.json")
_SEED_FILE_LOCAL = os.path.join(_SRC_DIR, "data", "seed.json")
_SEED_FILE_CLOUD = os.path.join(DATA_DIR, "seed.json")

# 预设话题标签
TOPIC_MAP = {
    "高质量发展": ["高质量", "发展主动", "产业升级", "转型", "增长极"],
    "科技创新": ["科技", "创新", "数字化", "AI", "算力", "智能", "技术"],
    "文化自信": ["文化", "传统", "历史", "文明", "非遗", "国潮"],
    "基层治理": ["基层", "治理", "社区", "网格", "便民", "服务"],
    "改革开放": ["改革", "开放", "攻坚", "突破", "自贸", "试点"],
    "生态文明": ["生态", "绿色", "低碳", "环保", "碳达峰", "碳中和"],
    "区域协调": ["区域", "协调", "内陆", "沿海", "东部", "西部", "中部"],
    "乡村振兴": ["乡村", "三农", "农业", "农村", "脱贫", "粮"],
    "民生保障": ["民生", "就业", "医疗", "教育", "养老", "住房", "社保"],
    "数字经济": ["数字", "数据", "互联网", "电商", "直播", "算力"],
    "营商环境": ["营商", "市场", "公平", "准入", "民营", "企业"],
    "干部作风": ["作风", "担当", "实干", "政绩观", "调研", "群众"],
}


def _find_seed():
    """找到种子文件位置。"""
    if os.path.exists(_SEED_FILE_LOCAL):
        return _SEED_FILE_LOCAL
    if os.path.exists(_SEED_FILE_CLOUD):
        return _SEED_FILE_CLOUD
    return None


def _load():
    if not os.path.exists(DB_FILE):
        seed_path = _find_seed()
        if seed_path:
            records = _load_seed(seed_path)
            _auto_tag(records)
            _save(records)
            return records
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_seed(seed_path):
    with open(seed_path, "r", encoding="utf-8") as f:
        records = json.load(f)
    for i, r in enumerate(records):
        r["id"] = i + 1
        r["created_at"] = r.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
    return records


def _auto_tag(records):
    for r in records:
        if r.get("tags"):
            continue
        text = r.get("analysis_raw", "") + " " + r.get("full_text", "") + " " + r.get("title", "")
        tags = []
        for topic, keywords in TOPIC_MAP.items():
            for kw in keywords:
                if kw in text:
                    tags.append(topic)
                    break
        r["tags"] = tags[:5] if tags else ["综合"]


def _save(records):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def add_article(article: dict) -> int:
    records = _load()
    new_id = max((r.get("id", 0) for r in records), default=0) + 1
    article["id"] = new_id
    article["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    _auto_tag([article])
    records.append(article)
    _save(records)
    return new_id


def get_all_articles():
    records = _load()
    return sorted_records(records)


def get_articles_by_topic(topic: str):
    records = _load()
    if not topic:
        return sorted_records(records)
    return sorted_records([r for r in records if topic in r.get("tags", [])])


def get_all_topics():
    records = _load()
    counts = {}
    for r in records:
        for t in r.get("tags", []):
            counts[t] = counts.get(t, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)


def search_materials(query: str):
    if not query:
        return get_all_articles()
    records = _load()
    results = []
    for r in records:
        text = r.get("title", "") + r.get("analysis_raw", "") + r.get("full_text", "")
        if query.lower() in text.lower():
            results.append(r)
    return sorted_records(results)


def sorted_records(records):
    return sorted(records, key=lambda x: x.get("date", ""), reverse=True)


def delete_article(article_id: int):
    records = _load()
    records = [r for r in records if r["id"] != article_id]
    _save(records)


def get_stats():
    records = _load()
    topics = get_all_topics()
    return {
        "total": len(records),
        "topics_covered": len(topics),
        "dates": len(set(r.get("date", "") for r in records)),
        "latest_date": records[0]["date"] if records else "暂无",
    }


def recommend_for_topic(topic: str, limit=5):
    records = _load()
    scored = []
    for r in records:
        score = 0
        tags = r.get("tags", [])
        if topic in tags:
            score += 10
        text = r.get("analysis_raw", "") + r.get("title", "")
        for kw in TOPIC_MAP.get(topic, []):
            if kw in text:
                score += 1
        if score > 0:
            scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:limit]]
