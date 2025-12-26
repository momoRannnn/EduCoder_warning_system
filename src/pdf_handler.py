# src/pdf_handler.py
"""
模块功能：
    这个模块担任了 pdf 处理助手的职务，他会优先尝试使用 pdfplumber 进行文本提取，如果文件本身只是一张图片，就调用 ocr_engine模块的 ocr 模型

说明：
    pdfplumer 阅读文本的速度极快，如果 pdf 文件是文本型，将大大减少时间，实在不行了再调用 ocr 模型
    同时把它叫做 handler 而不是 processor 是因为它会像人一样根据特定的策略来处理 pdf

依赖关系：
    - pdfplumer：用于阅读文本型 pdf
    - src.ocr_engine: 用于解析扫描件/图片型 PDF
"""

import pdfplumber
from src.ocr_engine import ocr_process_pdf


def parse_pdf_report(pdf_path: str) -> dict:
    """
    函数功能：
        阅读 pdf 文件，提取其中的文本数据

    参数：
        - pdf_path (str): pdf 文件的路径

    返回值：
        dict: 包含了状态和持续时间的dict
    """
    # 默认data
    data = {
        "状态": "读取失败",
        "耗时": "0",
        "识别方式": "TEXT",
        "异常备注": ""
    }

    try:
        # 尝试使用 pdfplumer 进行快速处理
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                data["异常备注"] = "Empty PDF"
                return data

            first_page = pdf.pages[0]
            text = first_page.extract_text()

            # 如果 text 长度小于 5，那就是一张图片，需要调用 ocr
            if not text or len(text.strip()) < 5:
                return ocr_process_pdf(pdf_path)

            # 如果是文本型的 pdf
                # 提取状态
            lines = text.split('\n')
            for line in lines[:10]:
                if "按时通关" in line:
                    data["状态"] = "按时通关"
                    break
                elif "未通关" in line:
                    data["状态"] = "未通关"
                    break
                elif "未开启" in line:
                    data["状态"] = "未开启"
                    break

                # 提取耗时时长
            tables = first_page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        row_str = str(row)
                        if "实训总耗时" in row_str:
                            for cell in row:
                                if cell and ("天" in cell or "时" in cell or "分" in cell) and "实训" not in cell:
                                    data["耗时"] = cell
                                    break

    except Exception as e:
        data["异常备注"] = str(e)
        data["状态"] = "Error"

    return data