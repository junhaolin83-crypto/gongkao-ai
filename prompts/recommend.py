"""智能素材推荐Prompt"""

SYSTEM_PROMPT = """你是一位公考申论辅导老师。请基于用户的素材库和当前写作话题，推荐最相关的素材并说明原因。"""


def build_prompt(topic: str, essay_prompt: str, materials: list[dict]) -> tuple[str, str]:
    """基于当前写作话题和素材库生成推荐。"""
    summary = []
    for m in materials[:15]:
        title = m.get("title", "未知")
        tags = ", ".join(m.get("tags", []))
        snippet = m.get("analysis_raw", "")[:500]
        summary.append(f"【{title}】[标签: {tags}]\n摘要: {snippet}")

    user_prompt = f"""当前写作话题：{topic}
作文要求：{essay_prompt}

素材库内容：
{chr(10).join(summary)}

请从素材库中推荐3-5条最有用的素材，按以下格式：

🔖 推荐素材一：
文章标题 | 推荐理由（1句话） | 如何使用（具体建议，如：用于分论点X作为论据）

🔖 推荐素材二：
...

最后用一句话总结：这组素材的组合打法是什么（如：先引XX数据压倒对方论证，再用XX案例递进深化）。
"""
    return SYSTEM_PROMPT, user_prompt
