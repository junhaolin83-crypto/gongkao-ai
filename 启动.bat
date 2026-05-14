@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动公考AI批改助手...
echo 首次启动可能需要下载OCR模型（约100MB），请耐心等待
echo.
"C:\Users\Agoni\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run app.py
pause
