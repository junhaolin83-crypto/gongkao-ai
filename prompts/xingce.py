SYSTEM_PROMPT = """你是一位公考行测辅导老师，擅长各模块（言语理解、判断推理、资料分析、数量关系、常识判断）的解题方法。你能够精准定位学生的思维漏洞，给出清晰的解题思路和避坑技巧。"""


def build_prompt(module: str, question: str, user_answer: str, correct_answer: str) -> tuple[str, str]:
    user_prompt = f"""请分析以下行测错题：

【所属模块】
{module}

【题目】
{question}

【考生选的答案】
{user_answer}

【正确答案】
{correct_answer}

请按以下格式输出：

===错误归因===
属于：知识点盲区 / 审题粗心 / 逻辑陷阱 / 计算失误 / 其他

===正确解题步骤===
一步一步写出正确的解题过程，让考生能跟着你的思路走

===速解技巧===
如果这是选择题，有没有30秒内的快速解法？请说明

===避坑提醒===
这道题最易错的陷阱是什么？下次遇到类似题应该注意什么？

===同类推荐===
针对这个知识点，出一道同类变式题的题干（只出题，不写答案）
"""
    return SYSTEM_PROMPT, user_prompt
