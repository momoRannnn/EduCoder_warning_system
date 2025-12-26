# src/exporter.py
"""
模块功能：
    本模块专门负责将处理好的内存数据序列化为外部文件格式（如 Excel, CSV, JSON）。。

依赖关系：
    pandas: 用于数据帧构建和 Excel 写入
"""

import pandas as pd


def save_to_excel(data: list, output_path: str):
    """
    函数功能：
        将包含学生数据的字典列表导出为标准 Excel 报表。

    Args:
        data (list[dict]): 学生数据列表。
        output_path (str): 输出文件的绝对路径。
    """
    if not data:
        print("[WARN] 没有数据可供导出。")
        return

    try:
        df = pd.DataFrame(data)

        # 定义列顺序 (显式定义，保证报表美观)
        columns_order = ['班级', '学号', '姓名', '状态', '耗时', '识别方式', '是否有异常', '异常备注', '文件路径']

        # 补全缺失列
        for col in columns_order:
            if col not in df.columns:
                df[col] = ""

        # 排序：优先班级，次优先学号
        if '班级' in df.columns and '学号' in df.columns:
            df.sort_values(by=['班级', '学号'], inplace=True)

        # 裁剪并重排
        df = df[columns_order]

        # 导出 (index=False 去掉 dataframe 自带的行号)
        df.to_excel(output_path, index=False)
        print(f"[INFO] 报表已生成: {output_path}")

    except Exception as e:
        print(f"[ERROR] Excel 导出失败: {e}")