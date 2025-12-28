# src/utils.py
"""
模块功能：
    本模块类似于一个工具箱 (Utility Belt)，存放通用的、不依赖于具体业务逻辑的底层工具函数。
    1. 打印动态进度条 (UI)
    2. 文本编码自适应修复 (String Processing)

依赖关系：
    sys: 打印进度条
"""

import sys

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