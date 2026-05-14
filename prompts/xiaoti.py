SYSTEM_PROMPT = """你是一位资深的国考申论阅卷老师，阅卷经验丰富，熟悉国考和省考的评分标准。

请严格按照以下格式批改这道申论小题。批改要一针见血，不要只说好话，要明确指出问题。"""


def build_prompt(material: str, question: str, requirement: str, answer: str) -> tuple[str, str]:
    """返回 (system_prompt, user_prompt)"""

    user_prompt = f"""请批改以下申论小题：

【题目】
{question}

【要求】
{requirement}

【给定材料】
{material}

【考生答案】
{answer}

请按以下格式输出：

===踩点分析===
列出本题所有得分点，逐个标注考生的作答情况：（✅ 踩中 / ⚠️ 部分踩中 / ❌ 遗漏）

===失分原因===
从以下维度分析：概括不到位 / 遗漏关键词 / 逻辑混乱 / 超出字数 / 审题偏差 / 其他

===优化答案===
基于材料给出一个高分答案（注意字数限制）

===预估得分===
格式：XX分 / 满分XX分

===改进建议===
给考生2-3条具体、可操作的改进建议
"""
    return SYSTEM_PROMPT, user_prompt
