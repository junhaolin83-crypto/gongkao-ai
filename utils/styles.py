"""自定义CSS样式：现代简洁高级风格"""

CSS = """
<style>
/* ===== 全局 ===== */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: white;
}
.main-header h1 { color: white !important; font-size: 2rem; font-weight: 700; margin: 0; }
.main-header p { color: rgba(255,255,255,0.85) !important; margin: 0.5rem 0 0 0; font-size: 0.95rem; }

/* ===== 统计卡片 ===== */
.stats-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.stat-card {
    flex: 1; min-width: 140px;
    background: white; border-radius: 12px; padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 1px solid #eef0f5;
}
.stat-card .num { font-size: 2rem; font-weight: 700; color: #667eea; margin: 0; }
.stat-card .label { font-size: 0.85rem; color: #888; margin-top: 0.2rem; }

/* ===== 话题标签 ===== */
.tag {
    display: inline-block; padding: 0.25rem 0.7rem; border-radius: 20px;
    font-size: 0.8rem; font-weight: 500; cursor: pointer; transition: all 0.15s;
    margin: 0.15rem; border: 1px solid transparent;
}
.tag:hover { transform: translateY(-1px); }
.tag-blue { background: #e8f0fe; color: #1a73e8; }
.tag-green { background: #e6f4ea; color: #137333; }
.tag-orange { background: #fef7e0; color: #b06000; }
.tag-purple { background: #f3e8fd; color: #7627a9; }
.tag-teal { background: #e0f2f1; color: #00695c; }
.tag-pink { background: #fce4ec; color: #a0003c; }

/* ===== 素材卡片 ===== */
.material-card {
    background: white; border-radius: 12px; padding: 1.5rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    border: 1px solid #eef0f5;
    margin-bottom: 1rem;
    transition: box-shadow 0.2s;
}
.material-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.material-card .title {
    font-size: 1.1rem; font-weight: 600; color: #1a1a2e;
    margin-bottom: 0.4rem;
}
.material-card .meta {
    font-size: 0.82rem; color: #999; margin-bottom: 0.6rem;
}
.material-card .tags-wrap { margin: 0.5rem 0; }

/* ===== 推荐卡片 ===== */
.recommend-card {
    background: linear-gradient(135deg, #f8f9ff 0%, #f0f3ff 100%);
    border: 1px solid #d6dafa; border-radius: 12px; padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}
.recommend-card .rec-title { font-size: 0.95rem; font-weight: 600; color: #667eea; }
.recommend-card .rec-snippet { font-size: 0.82rem; color: #666; margin-top: 0.3rem; }

/* ===== 提示框 ===== */
.tip-box {
    background: #fff8e1; border-left: 4px solid #ffc107;
    padding: 0.8rem 1.2rem; border-radius: 0 8px 8px 0; font-size: 0.88rem;
    margin: 0.8rem 0; color: #5d4037;
}

/* ===== 分隔线 ===== */
.section-divider {
    height: 1px; background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
    margin: 1.5rem 0;
}

/* ===== 移动端优化 ===== */
@media (max-width: 768px) {
    .stats-row { flex-direction: column; }
    .stat-card { min-width: auto; }
    .main-header { padding: 1.2rem 1.5rem; }
}
</style>
"""
