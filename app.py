import os
from datetime import datetime
import streamlit as st

from utils.api import call_deepseek
from utils.history import add_record, get_records
from utils.material import add_article, update_article, get_all_articles, delete_article
from prompts import xiaoti, dazhuowen, xingce
from prompts.material_analysis import build_prompt as material_prompt

st.set_page_config(page_title="公考AI批改助手", page_icon="📝", layout="wide")

# 部署到 Streamlit Cloud 时，从 Secrets 读取 API Key
if "DEEPSEEK_API_KEY" not in os.environ:
    try:
        os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]
    except (KeyError, Exception):
        pass

st.title("📝 公考AI批改助手")
st.markdown("调DeepSeek V4 Pro，帮你批改申论、分析行测错题")

# ---------- 初始化 session_state ----------
_KEYS = [
    # 小题
    "xiaoti_material", "xiaoti_question", "xiaoti_requirement", "xiaoti_answer",
    # 大作文
    "dzw_material", "dzw_question", "dzw_answer",
    # 行测
    "xc_question", "xc_user", "xc_correct", "xc_note",
]
for k in _KEYS:
    if k not in st.session_state:
        st.session_state[k] = ""


# ---------- OCR 公共组件 ----------
def ocr_uploader(expand_label: str, target_key: str, btn_label: str = "填入上方"):
    """显示图片上传+拍照+OCR按钮，识别结果直接填入 target_key 对应的 text_area。"""
    with st.expander(f"📷 {expand_label}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            up = st.file_uploader(
                "选择图片",
                type=["jpg", "jpeg", "png", "bmp", "webp"],
                key=f"up_{target_key}",
            )
        with col2:
            cam = st.camera_input("拍照", key=f"cam_{target_key}")

        image_bytes = None
        if up is not None:
            image_bytes = up.getvalue()
        elif cam is not None:
            image_bytes = cam.getvalue()

        if image_bytes and st.button("🔍 识别文字", key=f"ocr_{target_key}"):
            with st.status("识别中，首次加载需下载模型约100MB，请稍候..."):
                try:
                    from utils.ocr import ocr_image_bytes
                    text = ocr_image_bytes(image_bytes)
                    if text.strip():
                        st.session_state[target_key] = text
                        st.success("✅ 已填入对应输入框")
                    else:
                        st.warning("未识别到文字，请检查图片清晰度")
                except ImportError as e:
                    st.error(f"❌ {e}")
                except Exception as e:
                    st.error(f"识别失败：{e}")


# ---------- 侧边栏 ----------
with st.sidebar:
    st.header("⚙️ 配置")
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        help="不会保存，仅本次会话有效",
    )
    if api_key:
        import os

        os.environ["DEEPSEEK_API_KEY"] = api_key
        st.success("API Key 已设置")
    else:
        st.warning("请填入 API Key 后才能使用")

    st.divider()
    st.markdown(
        "**使用说明**\n\n"
        "1. 填入 DeepSeek API Key\n"
        "2. 选择功能标签页\n"
        "3. 输入题目和你的答案\n"
        "4. 也可拍照自动识别文字\n"
        "5. 点击批改按钮"
    )

# ---------- 标签页 ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📄 申论小题批改", "📃 大作文批改", "🧮 行测错题分析", "📋 批改历史", "📰 人民日报素材"]
)

# ==================== 小题 ====================
with tab1:
    st.subheader("申论小题批改")
    st.caption("支持概括题、分析题、对策题等小题型")

    col1, col2 = st.columns(2)
    with col1:
        ocr_uploader("拍材料", "xiaoti_material", "填入材料")
        st.text_area("📄 给定材料", key="xiaoti_material", height=250)
        st.text_area("📌 题目要求", key="xiaoti_question", height=80)

    with col2:
        ocr_uploader("拍答案", "xiaoti_answer", "填入答案")
        st.text_area("📏 作答要求（如：不超过200字）", key="xiaoti_requirement", height=80)
        st.text_area("✍️ 你的答案", key="xiaoti_answer", height=250)

    if st.button("🚀 开始批改", key="btn_xiaoti", use_container_width=True):
        err = []
        if not api_key:
            err.append("请先在侧边栏填入 API Key")
        if not st.session_state.xiaoti_material:
            err.append("请填写给定材料")
        if not st.session_state.xiaoti_answer:
            err.append("请填写你的答案")
        if err:
            st.warning("\n".join(err))
        else:
            with st.spinner("AI阅卷中..."):
                sp, up = xiaoti.build_prompt(
                    st.session_state.xiaoti_material,
                    st.session_state.xiaoti_question,
                    st.session_state.xiaoti_requirement,
                    st.session_state.xiaoti_answer,
                )
                result = call_deepseek(sp, up)
            st.markdown("### 📊 批改报告")
            st.markdown(result)
            add_record("申论小题", st.session_state.xiaoti_question[:30] or "小题", result)

# ==================== 大作文 ====================
with tab2:
    st.subheader("申论大作文批改")
    st.caption("从审题立意、结构逻辑、论据内容、语言表达四个维度评分")

    col1, col2 = st.columns(2)
    with col1:
        ocr_uploader("拍材料", "dzw_material", "填入材料")
        st.text_area("📄 给定资料/题干", key="dzw_material", height=250)
        st.text_area("📌 作答要求", key="dzw_question", height=80)

    with col2:
        ocr_uploader("拍作文", "dzw_answer", "填入作文")
        st.text_area("✍️ 你的作文（全文）", key="dzw_answer", height=350)

    if st.button("🚀 开始批改", key="btn_dzw", use_container_width=True):
        err = []
        if not api_key:
            err.append("请先在侧边栏填入 API Key")
        if not st.session_state.dzw_material:
            err.append("请填写给定资料")
        if not st.session_state.dzw_answer:
            err.append("请填写你的作文")
        if err:
            st.warning("\n".join(err))
        else:
            with st.spinner("AI阅卷中..."):
                sp, up = dazhuowen.build_prompt(
                    st.session_state.dzw_material,
                    st.session_state.dzw_question,
                    st.session_state.dzw_answer,
                )
                result = call_deepseek(sp, up)
            st.markdown("### 📊 批改报告")
            st.markdown(result)
            add_record("大作文", st.session_state.dzw_question[:30] or "大作文", result)

# ==================== 行测 ====================
with tab3:
    st.subheader("行测错题分析")
    st.caption("输入做错的题，AI帮你归因 + 拆解 + 避坑")

    module = st.selectbox(
        "📂 所属模块",
        [
            "言语理解-逻辑填空",
            "言语理解-片段阅读",
            "言语理解-语句表达",
            "判断推理-图形推理",
            "判断推理-定义判断",
            "判断推理-类比推理",
            "判断推理-逻辑判断",
            "数量关系",
            "资料分析",
            "常识判断",
        ],
        key="xc_module",
    )

    col1, col2 = st.columns(2)
    with col1:
        ocr_uploader("拍题目", "xc_question", "填入题目")
        st.text_area("📄 题目内容", key="xc_question", height=200)

    with col2:
        st.text_input("❌ 你选的答案", key="xc_user")
        st.text_input("✅ 正确答案", key="xc_correct")

    st.text_area("💬 备注（可选，如当时为什么选错）", key="xc_note", height=80)

    if st.button("🚀 分析错题", key="btn_xc", use_container_width=True):
        err = []
        if not api_key:
            err.append("请先在侧边栏填入 API Key")
        if not st.session_state.xc_question:
            err.append("请填写题目内容")
        if not st.session_state.xc_user:
            err.append("请填写你选的答案")
        if not st.session_state.xc_correct:
            err.append("请填写正确答案")
        if err:
            st.warning("\n".join(err))
        else:
            full_question = st.session_state.xc_question
            if st.session_state.xc_note:
                full_question += f"\n\n【考生备注】{st.session_state.xc_note}"
            with st.spinner("分析中..."):
                sp, up = xingce.build_prompt(
                    module, full_question, st.session_state.xc_user, st.session_state.xc_correct
                )
                result = call_deepseek(sp, up)
            st.markdown("### 📊 分析报告")
            st.markdown(result)
            add_record("行测错题", f"[{module}] {st.session_state.xc_question[:40]}", result)

# ==================== 历史记录 ====================
with tab4:
    st.subheader("批改历史记录")
    records = get_records(50)
    if not records:
        st.info("暂无批改记录，批改过的题目会显示在这里")
    else:
        for r in records:
            with st.expander(f"[{r['category']}] {r['title']} — {r['time']}"):
                st.markdown(r["result"])

# ==================== 人民日报素材 ====================
with tab5:
    st.subheader("📰 人民日报申论素材库")
    st.caption("每日精选人民日报文章 → AI结构化分析 → 直接用于大作文")

    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown("#### 📚 已收录文章")
    with col_right:
        if st.button("➕ 添加新素材", key="btn_add_material", use_container_width=True):
            st.session_state.show_add_form = True

    # 初始化
    if "show_add_form" not in st.session_state:
        st.session_state.show_add_form = False
    if "material_text" not in st.session_state:
        st.session_state.material_text = ""

    # 添加表单
    if st.session_state.show_add_form:
        with st.container(border=True):
            st.markdown("##### 粘贴人民日报文章内容")
            st.caption("填入文章信息，AI自动生成结构化素材分析")
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                art_title = st.text_input("标题", key="add_title")
            with col_t2:
                art_author = st.text_input("作者", key="add_author")
            with col_t3:
                art_column = st.text_input("栏目", placeholder="人民论坛/人民时评等", key="add_column")
            art_url = st.text_input("原文链接（可选）", key="add_url", placeholder="http://paper.people.com.cn/...")
            art_full = st.text_area("📄 原文全文（建议粘贴，方便后续复习）", height=200, key="add_full",
                                   placeholder="粘贴人民日报文章全文...")
            text = st.text_area(
                "文章内容摘要（AI分析用）",
                value=st.session_state.material_text,
                height=200,
                key="material_input",
                placeholder="粘贴文章全文或摘要...",
            )
            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                if st.button("🤖 AI分析并保存", key="btn_analyze", use_container_width=True):
                    if not api_key:
                        st.error("请先在侧边栏填入 API Key")
                    elif not text.strip():
                        st.warning("请粘贴文章内容")
                    else:
                        with st.spinner("AI分析中..."):
                            sp, up = material_prompt(text)
                            result = call_deepseek(sp, up)
                            if result.startswith("API调用失败") or result.startswith("配置错误"):
                                st.error(result)
                            else:
                                add_article({
                                    "title": art_title or "",
                                    "author": art_author or "",
                                    "column": art_column or "",
                                    "source": "人民日报",
                                    "url": art_url or "",
                                    "full_text": art_full or text,
                                    "date": datetime.now().strftime("%Y-%m-%d"),
                                    "raw": text,
                                    "analysis_raw": result,
                                })
                                for k in ["add_title", "add_author", "add_column", "add_url", "add_full"]:
                                    st.session_state[k] = ""
                                st.session_state.material_text = ""
                                st.session_state.show_add_form = False
                                st.success("✅ 素材已保存！")
                                st.rerun()
            with col_btn2:
                if st.button("取消", key="btn_cancel_material"):
                    st.session_state.show_add_form = False
                    st.rerun()

    # 文章列表
    articles = get_all_articles()
    if not articles:
        st.info(
            "📭 暂无素材\n\n"
            "点击「添加新素材」粘贴人民日报文章，AI会自动帮你提炼分论点、论据和金句。\n\n"
            "你也可以每天早上让我搜索人民日报文章，然后添加到这里。"
        )
    else:
        for art in articles:
            title = art.get("title", "")
            if not title:
                for line in art.get("analysis_raw", "").split("\n"):
                    if "标题：" in line:
                        title = line.split("：", 1)[-1].strip()
                        break
                if not title:
                    title = f"人民日报 {art.get('date', '')}"

            with st.expander(f"📰 {title} — {art.get('date', '')}", expanded=False):
                # 来源信息
                src = art.get("source", "人民日报")
                col = art.get("column", "")
                author = art.get("author", "")
                art_url = art.get("url", "")
                info_parts = [f"**来源：** {src}"]
                if col:
                    info_parts.append(f"**栏目：** {col}")
                if author:
                    info_parts.append(f"**作者：** {author}")
                st.markdown(" | ".join(info_parts))
                if art_url:
                    st.markdown(f"[🔗 原文链接]({art_url})")

                # 全文
                full_text = art.get("full_text", "")
                if full_text:
                    with st.expander("📖 查看原文全文", expanded=False):
                        st.markdown(full_text)

                # 结构化分析
                analysis = art.get("analysis_raw", "暂无分析")
                st.markdown("---")
                st.markdown(analysis)

                col_del, _ = st.columns([1, 5])
                with col_del:
                    if st.button("🗑️ 删除", key=f"del_{art['id']}"):
                        delete_article(art["id"])
                        st.rerun()


# ---------- 页脚 ----------
st.divider()
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.8em'>"
    "公考AI批改助手 · 调用 DeepSeek V4 Pro API · 仅供学习参考</div>",
    unsafe_allow_html=True,
)
