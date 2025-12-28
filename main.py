# main.py
"""
主程序入口 (Entry Point)

功能：
    作为系统的调度中心 (Controller/Orchestrator)。
    职责仅限于流程控制：
    1. 环境配置与资源审计
    2. 数据摄入 (Ingest)
    3. 并行计算调度 (Map-Reduce)
    4. 数据交付 (Export)
"""
import os
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

# --- 模块导入 (Imports) ---
from src.raw_file_processor import unzip_file, scan_assignment_files, get_raw_zip_file
from src.pdf_handler import enrich_data
from src.exporter import save_to_excel
from src.utils import print_progress

# --- 1.全局路径配置 ---
# 使用相对路径确保跨平台兼容性
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "2_final_report.xlsx")


def main():

    print("=== EduCoder 预警系统启动 (Phase 2 Refactored) ===")
    # 1. 数据摄入 (Data Ingestion)
    # 1.1 获取源文件
    zip_path = get_raw_zip_file(RAW_DIR)
    if not zip_path:
        print(f"[Error] data/raw 目录下未找到 ZIP 文件，请检查路径。")
        return

    # 1.2 解压处理 (IO 密集型，单线程执行)
    # 注意：内部已通过 src.utils 修复了中文乱码问题
    if not unzip_file(zip_path, PROCESSED_DIR):
        return

    # 1.3 构建任务清单
    files_list = scan_assignment_files(PROCESSED_DIR)
    total_files = len(files_list)
    if total_files == 0:
        print("[Warn] 未扫描到 PDF 文件。")
        return

    # 2. 资源调度 (Resource Scheduling)
    # 获取 CPU 核心数
    cpu_count = os.cpu_count() or 1

    # 策略：N-2 策略 (高性能机型) 或 N-1 策略 (普通机型)，保底 1 进程
    if cpu_count > 4:
        workers = cpu_count - 2
    else:
        workers = max(1, cpu_count - 1)

    print(f"\n[系统配置] CPU核心数: {cpu_count} | 启用进程数: {workers}")
    print(f"[任务启动] 准备处理 {total_files} 份作业数据...")
    print("-" * 50)

    # 3. 并行计算 (Parallel Computing)
    start_time = time.time()
    results = []

    # 启动进程池
    with ProcessPoolExecutor(max_workers=workers) as executor:
        # Map: 将 "基础数据" 映射给 "enrich_data" 函数
        # enrich_data 会负责调用 pdfplumber/OCR 并合并结果
        futures = executor.map(enrich_data, files_list)

        # Reduce: 实时收集结果并反馈进度
        for i, res in enumerate(futures):
            results.append(res)
            print_progress(i + 1, total_files, res.get('姓名', 'Unknown'))

    duration = time.time() - start_time
    print(f"\n\n[执行完毕] 总耗时: {duration:.2f}s | 平均速度: {duration / total_files:.2f}s/file")

    # 4. 数据交付 (Data Delivery)
    save_to_excel(results, OUTPUT_FILE)


if __name__ == '__main__':
    # 跨平台多进程保护 (Windows/macOS 必需)
    multiprocessing.freeze_support()
    main()