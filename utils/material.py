"""人民日报素材库管理：增删改查 + 话题标签 + 智能搜索"""

import json
import os
import tempfile
from datetime import datetime

# 话题标签映射（纯数据，无IO操作）
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

# 延迟初始化：第一次调用时才确定路径
_data_dir = None
_db_file = None


def _init():
    """延迟初始化：确定可写数据目录。零IO时只做定义，调用时才执行。"""
    global _data_dir, _db_file
    if _data_dir is not None:
        return

    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_data = os.path.join(src_dir, "data")

    # 尝试本地路径是否可写
    writable = False
    try:
        os.makedirs(local_data, exist_ok=True)
        test = os.path.join(local_data, ".rw")
        with open(test, "w") as f:
            f.write("1")
        os.remove(test)
        writable = True
    except Exception:
        writable = False

    if writable:
        _data_dir = local_data
    else:
        _data_dir = os.path.join(tempfile.gettempdir(), "gongkao-ai")
        os.makedirs(_data_dir, exist_ok=True)

    _db_file = os.path.join(_data_dir, "materials.json")


def _seed_path():
    """找到种子文件：优先本地data/，其次云端data/。"""
    p1 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "seed.json")
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(_data_dir, "seed.json")
    if os.path.exists(p2):
        return p2
    return None


def _load():
    _init()
    if not os.path.exists(_db_file):
        sp = _seed_path()
        if sp:
            with open(sp, "r", encoding="utf-8") as f:
                records = json.load(f)
            for i, r in enumerate(records):
                r.setdefault("id", i + 1)
                r.setdefault("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
            _auto_tag(records)
            _save(records)
            return records
        return []
    with open(_db_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _auto_tag(records):
    for r in records:
        if r.get("tags"):
            continue
        text = " ".join([r.get("analysis_raw", ""), r.get("full_text", ""), r.get("title", "")])
        tags = []
        for topic, keywords in TOPIC_MAP.items():
            for kw in keywords:
                if kw in text:
                    tags.append(topic)
                    break
        r["tags"] = tags[:5] if tags else ["综合"]


def _save(records):
    _init()
    with open(_db_file, "w", encoding="utf-8") as f:
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
    return sorted_records(_load())


def get_articles_by_topic(topic: str):
    if not topic:
        return sorted_records(_load())
    return sorted_records([r for r in _load() if topic in r.get("tags", [])])


def get_all_topics():
    counts = {}
    for r in _load():
        for t in r.get("tags", []):
            counts[t] = counts.get(t, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)


def search_materials(query: str):
    if not query:
        return get_all_articles()
    results = []
    for r in _load():
        text = " ".join([r.get("title", ""), r.get("analysis_raw", ""), r.get("full_text", "")])
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
        "latest_date": records[0]["date"] if records else "NoData",
    }


def recommend_for_topic(topic: str, limit=5):
    """根据话题文本从所有TOPIC_MAP关键词中匹配，给文章打分排序。"""
    records = _load()
    # 找出输入文本命中了哪些话题标签
    matched_topics = []
    for tag, keywords in TOPIC_MAP.items():
        for kw in keywords:
            if kw in topic:
                matched_topics.append(tag)
                break
    if not matched_topics:
        matched_topics = ["综合"]

    scored = []
    for r in records:
        score = 0
        r_tags = r.get("tags", [])
        for mt in matched_topics:
            if mt in r_tags:
                score += 10
        text = r.get("analysis_raw", "") + " " + r.get("title", "")
        for mt in matched_topics:
            for kw in TOPIC_MAP.get(mt, []):
                if kw in text:
                    score += 1
        if score > 0:
            scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:limit]]
