import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


def _get_client():
    """懒加载：每次调用时创建客户端，确保能读到运行时设置的API Key。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("未设置API Key。请在侧边栏填入或创建.env文件")
    return OpenAI(api_key=api_key, base_url=BASE_URL)


def call_deepseek(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """调用DeepSeek API，返回模型回复文本。"""
    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            stream=False,
        )
        return resp.choices[0].message.content
    except ValueError as e:
        return f"配置错误：{e}"
    except Exception as e:
        return f"API调用失败：{e}"
