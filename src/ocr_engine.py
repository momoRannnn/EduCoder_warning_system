# src/ocr_engine.py
"""
模块功能：
    这个模块可以调用 paddlepaddle 模型进行图像识别，并提取出其中的文字

说明：
    paddlepaddle 是轻量化的ocr 库，足以完成本项目的任务，github 链接：https://github.com/PaddlePaddle/PaddleOCR
    过程中直接把 pdf 文件转化为矩阵数据传给内存，而不存储在硬盘中，提高速度
    采用了正则表达式来准确提取出时间，不会受到干扰

Dependencies:
    paddleocr：图像识别模型
    pdfplumber：pdf 转换成 image
    re：正则表达式提取
    numpy:把 image 转化为矩阵
"""
import warnings
# 强力屏蔽 ccache 相关的警告
warnings.filterwarnings("ignore", message=".*ccache.*")
import logging
import re
import pdfplumber
import numpy as np
from paddleocr import PaddleOCR

logging.getLogger("ppocr").setLevel(logging.ERROR)# 减少状态输出，防止刷屏，保持安静

# 初始化模型的设定
ocr_model = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False, show_log=False)


def ocr_process_pdf(pdf_path):
    """
    函数功能：
        从 pdf 中提取学生完成作业的状态及耗时

    Args:
        pdf_path (str): pdf 文件的绝对路径

    Returns:
        dict: 一个包含了状态和耗时的字典
            - '状态' (Status): 例如'按时通关', '未通关'
            - '耗时' (Duration): 例如：'3天6时', '0'
    """
    # 默认返回值
    result = {"状态": "OCR失败", "耗时": "0", "识别方式": "OCR-AI"}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return result
            page = pdf.pages[0]
            # 将 pdf 文件转化为 image，再把 image 转化为矩阵传给内存
            img = page.to_image(resolution=150).original
            img_np = np.array(img)

            ocr_res = ocr_model.ocr(img_np, cls=True)

            if ocr_res and ocr_res[0]:
                all_texts = [line[1][0] for line in ocr_res[0]]
                full_text = " ".join(all_texts)

                # 提取状态
                if "按时通关" in full_text:
                    result["状态"] = "按时通关"
                elif "未通关" in full_text:
                    result["状态"] = "未通关"
                elif "未开启" in full_text:
                    result["状态"] = "未开启"
                else:
                    if "通关" in full_text and "按时" in full_text:# 防止 ocr 模型误认为“按时 通关”
                        result["状态"] = "按时通关"
                    else:
                        result["状态"] = "无法判定"

                # 提取耗时时长
                    # 处理有时长的
                pattern_standard = r'((\d+)\s*(天|时|分(?!班)|秒)\s*)+'# 防止匹配到“分班”的分
                matches = list(re.finditer(pattern_standard, full_text))

                best_match = None
                for m in matches:
                    val = m.group(0).replace(" ", "")
                    # 优先处理秒和天，因为“分”在“分班”中也有
                    if "秒" in val or "天" in val:
                        best_match = val
                        break
                    if not best_match: best_match = val

                if best_match:
                    result["耗时"] = best_match
                else:
                        # 处理时长为 0 的
                    match_context = re.search(r"(页面停留时长|实训总耗时)\s*(\S+)", full_text)
                    if match_context:
                        val = match_context.group(2)
                        if val == "0" or val == "--":
                            result["耗时"] = val

    except Exception as e:
        print(f"[OCR Error] {e}")

    return result