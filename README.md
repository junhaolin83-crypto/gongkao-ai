# 📝 公考AI批改助手

基于 DeepSeek V4 Pro API 的智能公考备考工具，支持申论小题批改、大作文多维评分、行测错题归因分析。

## 功能

- **申论小题批改** — 踩点分析 + 失分归因 + 优化答案 + 预估得分
- **申论大作文批改** — 审题立意 / 结构逻辑 / 论据内容 / 语言表达 四维评分
- **行测错题分析** — 错误归因 + 步骤拆解 + 速解技巧 + 避坑提醒 + 同类推荐
- **📷 拍照OCR识别** — 支持图片上传和手机拍照，自动识别文字填入批改框
- **批改历史** — 本地存储，随时回顾

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置API Key
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key

# 3. 启动
streamlit run app.py
```

## 技术栈

- Python 3.10+ / Streamlit / DeepSeek V4 Pro API
- Prompt Engineering 结构化输出设计
- 本地 JSON 持久化存储

## 项目结构

```
gongkao-ai/
├── app.py                 # Streamlit 主入口
├── prompts/               # Prompt 模板
│   ├── xiaoti.py          # 小题批改
│   ├── dazhuowen.py       # 大作文批改
│   └── xingce.py          # 行测分析
├── utils/
│   ├── api.py             # DeepSeek API 调用封装
│   ├── history.py         # 历史记录管理
│   └── ocr.py             # 拍照文字识别（EasyOCR）
├── data/                  # 本地存储（自动生成）
├── .env.example
├── requirements.txt
└── README.md
```
