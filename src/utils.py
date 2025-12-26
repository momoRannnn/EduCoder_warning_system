# src/utils.py
"""
模块功能：
    本模块类似于一个工具箱，里面包含了一些小工具
    1.打印动态进度条
    2.把数据录入到 excel 文件（暂时演示功能）

依赖关系：
    sys：打印进度条
"""

import sys

def print_progress(iteration, total, current_item="", bar_length=40):
    """
    函数功能：
        在控制台中显示单行动态进度条。

    Args:
        iteration (int): 当前进度（分子）。
        total (int): 总任务数（分母）。
        current_item (str): 当前正在处理的项目名称（用于显示在进度条后面）。
        bar_length (int): 进度条的长度字符数。
    """
    if total == 0:
        return

    percent = 100 * (iteration / float(total))
    filled_length = int(bar_length * iteration // total)
    bar = '#' * filled_length + '-' * (bar_length - filled_length)

    # 截断过长的文件名，保持 UI 整洁
    if len(current_item) > 20:
        current_item = current_item[:17] + "..."

    # 使用 \r 回车符实现单行刷新
    sys.stdout.write(f'\r[{bar}] {percent:.1f}% | Processing: {current_item:<20}')
    sys.stdout.flush()