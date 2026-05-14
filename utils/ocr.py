"""OCR模块：支持拍照/图片上传后自动识别中文文字"""

import io
import logging

import numpy as np
from PIL import Image

try:
    import easyocr

    _EASYOCR_AVAILABLE = True
except ImportError:
    _EASYOCR_AVAILABLE = False

_reader = None
logger = logging.getLogger(__name__)


def _get_reader():
    """懒加载EasyOCR Reader（首次调用时下载模型）。"""
    global _reader
    if _reader is None:
        if not _EASYOCR_AVAILABLE:
            raise ImportError(
                "EasyOCR 未安装，请运行: pip install easyocr\n"
                "首次运行会自动下载识别模型（约100MB），请保持网络畅通。"
            )
        logger.info("正在加载OCR模型（首次加载需下载约100MB模型文件）...")
        _reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
        logger.info("OCR模型加载完成")
    return _reader


def ocr_image_bytes(image_bytes: bytes) -> str:
    """识别图片中的文字，返回合并后的文本。"""
    reader = _get_reader()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_array = np.array(image)
    results = reader.readtext(img_array)
    # 按从上到下、从左到右排列
    lines = [res[1] for res in results]
    return "\n".join(lines)
