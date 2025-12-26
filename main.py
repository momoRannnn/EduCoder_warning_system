# main.py
"""
流程：
    1. 准备阶段: 调用 raw_file_processor 获取并解压源数据。
    2. 处理阶段: 调度 pdf_handler 和 ocr_engine 解析每一份报告。
    3. 输出阶段: 调用 exporter 生成最终的 Excel 报表。

使用方法:
    python main.py
"""

import os
import time


from src.raw_file_processor import get_raw_zip_file, unzip_file, scan_assignment_files# raw_file_processor: 负责处理原始输入
from src.pdf_handler import parse_pdf_report# pdf_handler: 负责核心业务解析
from src.utils import print_progress# utils: 负责界面显示
from src.exporter import save_to_excel# exporter: 负责结果输出

# --- 全局路径配置 ---
# 使用相对路径确保跨平台兼容性
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "2_final_report.xlsx")


def main():
    print("EduCoder Warning System v1.0")
    print("-" * 50)

    # --- 第一阶段：环境准备与数据提取 ---
    # 1. 寻找原料
    zip_path = get_raw_zip_file(RAW_DATA_DIR)
    if not zip_path:
        print(f"[ERROR] 未找到原始数据。请将 ZIP 文件放入 '{RAW_DATA_DIR}' 目录。")
        return

    # 2. 清洗原料 (仅当需要时解压)
    if not os.path.exists(PROCESSED_DIR) or not os.listdir(PROCESSED_DIR):
        print(f"[INFO] 正在解压并清洗原始数据...")
        if not unzip_file(zip_path, PROCESSED_DIR):
            return  # 解压失败直接退出

    # 3. 建立索引
    file_list = scan_assignment_files(PROCESSED_DIR)
    total_files = len(file_list)

    if total_files == 0:
        print("[WARN] 解压成功，但未扫描到任何 PDF 文件。")
        return

    print(f"[INFO] 发现 {total_files} 份作业报告，准备开始解析...")
    print("-" * 50)

    # --- 第二阶段：核心业务解析 ---
    final_data = []
    start_time = time.time()

    # 初始化 UI
    print_progress(0, total_files, current_item="系统启动中...")

    for i, student in enumerate(file_list):
        # 实时更新进度条
        print_progress(i + 1, total_files, current_item=student['姓名'])

        try:
            # === 调用核心逻辑 ===
            # 将文件路径交给 pdf_handler，它会自动决策是直读还是 OCR
            parse_result = parse_pdf_report(student['文件路径'])
        except Exception as e:
            # 容错机制：单个文件的失败不应导致整个程序崩溃
            parse_result = {
                "状态": "SystemError",
                "耗时": "0",
                "识别方式": "Error",
                "是否有异常": True,
                "异常备注": str(e)
            }

        # 将学生基本信息(姓名/学号)与解析结果(状态/耗时)合并
        final_data.append({**student, **parse_result})

    # 进度条跑完后换行
    print()
    print("-" * 50)
    print(f"[SUCCESS] 全量解析完成，总耗时 {time.time() - start_time:.2f} 秒。")

    # --- 第三阶段：数据持久化 ---
    # 将内存中的数据移交给导出模块
    save_to_excel(final_data, OUTPUT_FILE)


if __name__ == "__main__":
    main()