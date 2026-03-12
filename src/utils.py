# src/utils.py
"""
模块功能：
    本模块类似于一个工具箱，存放通用的、不依赖于具体业务逻辑的底层工具函数。
    1. 打印动态进度条 (UI)
    2. 文本编码自适应修复
    3. 将“x天x小时x分钟x秒”转化为对应的分钟数

依赖关系：
    sys: 打印进度条
    re: 从字符串中提取出对应的时间正则式
"""

import sys
import re


def parse_time_to_minutes(time_str: str) -> float:
    """
        函数功能：
            将文本耗时转化为总分钟数 (Float)

        Args:
            time_str (str): 从 pdf 文件中提取出的表示时间的字符串

        Returns:
            float：统一转化为分钟数并返回
        """
    if not time_str or str(time_str).strip() in ["0", "--", "无法判定", "OCR失败"]:
        return 0.0
    clean_str = str(time_str).replace(" ", "")#防止读出来带空格的字符串导致无法识别
    total_minutes = 0.0
    matches = re.findall(r'(\d+)(天|小时|时|分|秒)', clean_str)

    for val, unit in matches:
        num = float(val)
        if unit == '天':
            total_minutes += num * 24 * 60
        elif unit in ['时', '小时']:
            total_minutes += num * 60
        elif unit == '分':
            total_minutes += num
        elif unit == '秒':
            total_minutes += num / 60.0

    return round(total_minutes, 2)


def fix_text_encoding(text):
    """
    函数功能：
        自适应编码修复函数：尝试多种解码方式，直到找到可读的中文。

    Args:
        text (str): 可能包含乱码的原始字符串。

    Returns:
        str: 修复后的字符串。如果所有解码尝试都失败，则原样返回。
    """
    try:
        # 0. 如果本身就是正常的 unicode 字符串，先尝试编码回 bytes
        # Python 的 zipfile 有时会把文件名读成 cp437 编码的字符串
        raw_bytes = text.encode('cp437')
    except:
        return text # 如果无法编码回 cp437，说明它可能已经被正确处理过，或者也是乱码

    encodings = ['utf-8', 'gbk'] # 定义尝试列表：优先尝试 UTF-8 (Mac/Linux)，然后尝试 GBK (Windows)

    for enc in encodings:
        try:
            return raw_bytes.decode(enc)
        except:
            continue

    return text # 如果都失败了，返回原始乱码，至少比报错强


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