import os
from datetime import datetime
import streamlit as st

from utils.api import call_deepseek
from utils.history import add_record, get_records
from utils.material import (
    add_article, delete_article, get_all_articles,
    get_all_topics, get_articles_by_topic, get_stats,
    recommend_for_topic, search_materials,
)
from utils.styles import CSS
from prompts import xiaoti, dazhuowen, xingce
from prompts.material_analysis import build_prompt as material_prompt
from prompts.recommend import build_prompt as recommend_prompt

st.set_page_config(page_title="公考AI批改助手", page_icon="📝", layout="wide")

# 注入自定义CSS
st.markdown(CSS, unsafe_allow_html=True)

# 从 Secrets 读取 API Key
if "DEEPSEEK_API_KEY" not in os.environ:
    try:
        os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]
    except (KeyError, Exception):
        pass

# ---------- 顶部头图 ----------
st.markdown(
    '<div class="main-header">'
    '<h1>📝 公考AI批改助手</h1>'
    '<p>批改申论 · 分析行测 · 素材积累 · 智能推荐 — 一条龙备考</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ---------- 统计卡片 ----------
stats = get_stats()
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.markdown(f'<div class="stat-card"><div class="num">{stats["total"]}</div><div class="label">收录素材</div></div>', unsafe_allow_html=True)
with col_s2:
    st.markdown(f'<div class="stat-card"><div class="num">{stats["topics_covered"]}</div><div class="label">覆盖话题</div></div>', unsafe_allow_html=True)
with col_s3:
    st.markdown(f'<div class="stat-card"><div class="num">{stats["dates"]}</div><div class="label">收录日期</div></div>', unsafe_allow_html=True)
with col_s4:
    st.markdown(f'<div class="stat-card"><div class="num">{stats["latest_date"]}</div><div class="label">最近更新</div></div>', unsafe_allow_html=True)

# ---------- session_state ----------
_KEYS = [
    "xiaoti_material", "xiaoti_question", "xiaoti_requirement", "xiaoti_answer",
    "dzw_material", "dzw_question", "dzw_answer",
    "xc_question", "xc_user", "xc_correct", "xc_note",
    "show_add_form", "material_text",
    "dzw_recommendations",  # 大作文智能推荐
]
for k in _KEYS:
    if k not in st.session_state:
        st.session_state[k] = "" if k != "show_add_form" else False
    if k == "dzw_recommendations" and not isinstance(st.session_state.get(k), list):
        st.session_state[k] = []


# ---------- 侧边栏 ----------
with st.sidebar:
    st.markdown("### ⚙️ 配置")
    api_key = st.text_input("DeepSeek API Key", type="password", key="sidebar_key")
    if api_key:
        os.environ["DEEPSEEK_API_KEY"] = api_key
        st.success("API Key 已就绪")
    else:
        st.info("填入 API Key 后可用所有功能")
    st.divider()
    st.markdown("### 🧭 快速导航")
    st.markdown(
        "- 📄 小题批改\n"
        "- 📃 大作文 + 素材推荐\n"
        "- 🧮 行测错题分析\n"
        "- 📋 批改历史\n"
        "- 📰 素材库"
    )
    st.divider()
    st.caption("每日8:03自动收录人民日报素材 → 推送云端")


# ---------- OCR 组件 ----------
def ocr_uploader(expand_label: str, target_key: str):
    with st.expander(f"📷 {expand_label}", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            up = st.file_uploader("选择图片", type=["jpg", "jpeg", "png", "bmp", "webp"], key=f"up_{target_key}")
        with c2:
            cam = st.camera_input("拍照", key=f"cam_{target_key}")
        image_bytes = up.getvalue() if up is not None else (cam.getvalue() if cam is not None else None)
        if image_bytes and st.button("🔍 识别文字", key=f"ocr_{target_key}"):
            with st.status("识别中，首次需下载模型…"):
                try:
                    from utils.ocr import ocr_image_bytes
                    text = ocr_image_bytes(image_bytes)
                    if text.strip():
                        st.session_state[target_key] = text
                        st.success("已识别并填入")
                    else:
                        st.warning("未识别到文字")
                except ImportError as e:
                    st.error(f"❌ {e}")
                except Exception as e:
                    st.error(f"识别失败：{e}")


# ---------- 话题标签渲染 ----------
_tag_colors = ["tag-blue", "tag-green", "tag-orange", "tag-purple", "tag-teal", "tag-pink"]


def render_tags(tags):
    html = '<div class="tags-wrap">'
    for i, t in enumerate(tags):
        c = _tag_colors[i % len(_tag_colors)]
        html += f'<span class="tag {c}">{t}</span>'
    html += '</div>'
    return html


# ---------- 标签页 ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📄 小题批改", "📃 大作文 + 素材推荐", "🧮 行测分析", "📋 批改历史", "📰 素材库"]
)

# ==================== 小题 ====================
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        ocr_uploader("拍材料", "xiaoti_material")
        st.text_area("📄 给定材料", key="xiaoti_material", height=220)
        st.text_area("📌 题目要求", key="xiaoti_question", height=80)
    with col2:
        ocr_uploader("拍答案", "xiaoti_answer")
        st.text_area("📏 作答要求", key="xiaoti_requirement", height=80)
        st.text_area("✍️ 你的答案", key="xiaoti_answer", height=220)

    if st.button("🚀 开始批改", key="btn_xiaoti", use_container_width=True):
        if not api_key:
            st.warning("请在侧边栏填入 API Key")
        elif not st.session_state.xiaoti_material or not st.session_state.xiaoti_answer:
            st.warning("请填写材料与答案")
        else:
            with st.spinner("阅卷中..."):
                sp, up = xiaoti.build_prompt(
                    st.session_state.xiaoti_material, st.session_state.xiaoti_question,
                    st.session_state.xiaoti_requirement, st.session_state.xiaoti_answer,
                )
                r = call_deepseek(sp, up)
            st.markdown("### 批改报告")
            st.markdown(r)
            add_record("申论小题", st.session_state.xiaoti_question[:30] or "小题", r)

# ==================== 大作文 + 智能推荐 ====================
with tab2:
    col1, col2 = st.columns([3, 2])
    with col1:
        ocr_uploader("拍材料", "dzw_material")
        st.text_area("📄 给定资料/题干", key="dzw_material", height=200)
        st.text_area("📌 作答要求", key="dzw_question", height=80)
        ocr_uploader("拍作文", "dzw_answer")
        st.text_area("✍️ 你的作文", key="dzw_answer", height=300)

        if st.button("🚀 开始批改", key="btn_dzw", use_container_width=True):
            err = []
            if not api_key:
                err.append("请填入 API Key")
            if not st.session_state.dzw_material:
                err.append("请填写材料")
            if not st.session_state.dzw_answer:
                err.append("请填写作文")
            if err:
                st.warning("；".join(err))
            else:
                with st.spinner("阅卷中..."):
                    sp, up = dazhuowen.build_prompt(
                        st.session_state.dzw_material, st.session_state.dzw_question,
                        st.session_state.dzw_answer,
                    )
                    r = call_deepseek(sp, up)
                st.markdown("### 批改报告")
                st.markdown(r)
                add_record("大作文", st.session_state.dzw_question[:30] or "大作文", r)

    with col2:
        st.markdown("#### 💡 智能素材推荐")
        st.caption("根据你的话题，从素材库自动匹配相关论据")

        essay_text = st.session_state.dzw_question or st.session_state.dzw_material
        if st.button("🔍 分析话题并推荐素材", key="btn_recommend", use_container_width=True):
            if not api_key:
                st.warning("请先填入 API Key")
            elif not essay_text.strip():
                st.warning("请先填写作答要求")
            else:
                with st.spinner("分析中..."):
                    # 先从素材库匹配
                    all_mats = get_all_articles()
                    # 尝试关键词匹配
                    topic_hint = essay_text.strip()[:30]
                    matched = recommend_for_topic(topic_hint, limit=8)
                    if not matched and all_mats:
                        matched = all_mats[:5]

                    if matched:
                        sp, up = recommend_prompt(
                            topic_hint, essay_text, matched
                        )
                        rec = call_deepseek(sp, up)
                        st.session_state.dzw_recommendations = matched
                        st.session_state.rec_result = rec
                    else:
                        st.session_state.rec_result = "素材库暂无匹配内容，先积累一些人民日报文章吧！"
                        st.session_state.dzw_recommendations = []

        # 显示推荐结果
        rec_result = st.session_state.get("rec_result", "")
        if rec_result:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown(rec_result)

        if st.session_state.dzw_recommendations:
            st.markdown("##### 相关素材卡片")
            for m in st.session_state.dzw_recommendations[:4]:
                with st.expander(f"📰 {m.get('title', '')}", expanded=False):
                    snippet = m.get("analysis_raw", "")[:600]
                    st.markdown(snippet + ("…" if len(m.get("analysis_raw", "")) > 600 else ""))
                    st.caption(f"{m.get('date', '')} · {', '.join(m.get('tags', []))}")

# ==================== 行测 ====================
with tab3:
    module = st.selectbox("📂 模块", [
        "言语理解-逻辑填空", "言语理解-片段阅读", "言语理解-语句表达",
        "判断推理-图形推理", "判断推理-定义判断", "判断推理-类比推理", "判断推理-逻辑判断",
        "数量关系", "资料分析", "常识判断",
    ], key="xc_module")
    col1, col2 = st.columns(2)
    with col1:
        ocr_uploader("拍题目", "xc_question")
        st.text_area("📄 题目内容", key="xc_question", height=180)
    with col2:
        st.text_input("❌ 你选的答案", key="xc_user")
        st.text_input("✅ 正确答案", key="xc_correct")
    st.text_area("💬 备注（选填）", key="xc_note", height=70)
    if st.button("🚀 分析错题", key="btn_xc", use_container_width=True):
        err = []
        if not api_key:
            err.append("请填入 API Key")
        if not st.session_state.xc_question:
            err.append("请填题目")
        if not st.session_state.xc_user:
            err.append("请填你的答案")
        if not st.session_state.xc_correct:
            err.append("请填正确答案")
        if err:
            st.warning("；".join(err))
        else:
            q = st.session_state.xc_question
            if st.session_state.xc_note:
                q += f"\n\n【备注】{st.session_state.xc_note}"
            with st.spinner("分析中..."):
                sp, up = xingce.build_prompt(module, q, st.session_state.xc_user, st.session_state.xc_correct)
                r = call_deepseek(sp, up)
            st.markdown("### 分析报告")
            st.markdown(r)
            add_record("行测错题", f"[{module}] {st.session_state.xc_question[:40]}", r)

# ==================== 历史 ====================
with tab4:
    st.subheader("📋 批改历史")
    records = get_records(50)
    if not records:
        st.info("暂无记录，批改过的题目会显示在这里")
    else:
        for r in records:
            with st.expander(f"[{r['category']}] {r['title']} — {r['time']}"):
                st.markdown(r["result"])

# ==================== 素材库 ====================
with tab5:
    col_l, col_r = st.columns([3, 1])
    with col_l:
        st.subheader("📰 人民日报申论素材库")
    with col_r:
        if st.button("➕ 添加素材", key="btn_add_material", use_container_width=True):
            st.session_state.show_add_form = True

    # 话题筛选
    all_topics = get_all_topics()
    topic_names = [t[0] for t in all_topics]
    if topic_names:
        selected_topics = st.multiselect(
            "🏷️ 按话题筛选", topic_names, default=[],
            help="多选标签过滤文章",
        )

    # 搜索
    search_q = st.text_input("🔍 搜索素材", placeholder="输入关键词搜索...")

    # 添加表单
    if st.session_state.show_add_form:
        with st.container(border=True):
            st.markdown("##### 添加人民日报素材")
            c1, c2, c3 = st.columns(3)
            with c1:
                art_title = st.text_input("标题", key="add_title")
            with c2:
                art_author = st.text_input("作者", key="add_author")
            with c3:
                art_column = st.text_input("栏目", placeholder="人民论坛等", key="add_column")
            art_url = st.text_input("原文链接（可选）", key="add_url")
            art_full = st.text_area("原文全文", height=180, key="add_full",
                                   placeholder="建议粘贴全文，方便回头复习…")
            art_input = st.text_area("AI分析用内容（可粘贴全文或摘要）", height=180, key="material_input")
            cb1, cb2 = st.columns([1, 3])
            with cb1:
                if st.button("🤖 AI分析并保存", key="btn_analyze"):
                    if not api_key:
                        st.error("请填入 API Key")
                    elif not art_input.strip():
                        st.warning("请粘贴文章内容")
                    else:
                        with st.spinner("AI分析…"):
                            sp, up = material_prompt(art_input)
                            r = call_deepseek(sp, up)
                            if r.startswith("API调用失败") or r.startswith("配置错误"):
                                st.error(r)
                            else:
                                add_article({
                                    "title": art_title or "",
                                    "author": art_author or "",
                                    "column": art_column or "",
                                    "source": "人民日报",
                                    "url": art_url or "",
                                    "full_text": art_full or art_input,
                                    "date": datetime.now().strftime("%Y-%m-%d"),
                                    "analysis_raw": r,
                                })
                                for k in ["add_title", "add_author", "add_column", "add_url", "add_full", "material_input"]:
                                    st.session_state[k] = ""
                                st.session_state.show_add_form = False
                                st.success("✅ 已保存")
                                st.rerun()
            with cb2:
                if st.button("取消", key="btn_add_cancel"):
                    st.session_state.show_add_form = False
                    st.rerun()

    # 文章列表
    if search_q:
        articles = search_materials(search_q)
    elif selected_topics:
        articles = get_articles_by_topic(selected_topics[0])
        for t in selected_topics[1:]:
            extra = get_articles_by_topic(t)
            articles = [a for a in articles if a in extra]  # 交集
    else:
        articles = get_all_articles()

    if not articles:
        st.info("📭 没有匹配的素材")
    else:
        for art in articles:
            title = art.get("title") or "人民日报文章"
            tags = art.get("tags", [])
            author = art.get("author", "")
            col_name = art.get("column", "")
            art_url = art.get("url", "")

            with st.expander(f"📰 {title} — {art.get('date', '')}", expanded=False):
                # 元信息
                parts = [f"来源：{art.get('source', '人民日报')}"]
                if col_name:
                    parts.append(f"栏目：{col_name}")
                if author:
                    parts.append(f"作者：{author}")
                st.caption(" | ".join(parts))

                if tags:
                    st.markdown(render_tags(tags), unsafe_allow_html=True)

                if art_url:
                    st.markdown(f"[🔗 原文链接]({art_url})")

                full_text = art.get("full_text", "")
                if full_text:
                    with st.expander("📖 原文全文", expanded=False):
                        st.markdown(full_text)

                analysis = art.get("analysis_raw", "")
                if analysis:
                    st.markdown("---")
                    st.markdown(analysis)

                # tips
                st.markdown('<div class="tip-box">💡 <b>备考建议：</b>把这篇文章的金句抄到你的素材本上，标注起来，下次写同类话题时直接用。</div>', unsafe_allow_html=True)

                del_col, _ = st.columns([1, 5])
                with del_col:
                    if st.button("🗑️", key=f"del_{art['id']}"):
                        delete_article(art["id"])
                        st.rerun()

# ---------- 页脚 ----------
st.divider()
st.markdown(
    '<div style="text-align:center;color:#aaa;font-size:0.8em">'
    '公考AI批改助手 · 每日8:03自动收录人民日报素材 · 仅供学习参考</div>',
    unsafe_allow_html=True,
)
