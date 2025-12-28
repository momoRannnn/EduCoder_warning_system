#src/raw_file_processor.py
"""
模块功能：
    数据摄入层 (Ingest Layer)。
    主要负责解压原始文件，并扫描文件结构，构建最基础的学生信息列表（班级，学号，姓名，文件路径）。

依赖关系：
    os: 文件路径操作
    zipfile: 解压文件
    shutil: 清理文件夹
    src.utils: 调用文本修复工具
"""
import os
import zipfile
import shutil
from src.utils import fix_text_encoding


def unzip_file(zip_path, extract_to):
    """
    函数功能：
        通用解压函数，自动处理 Mac/Windows 编码差异及 __MACOSX 垃圾文件
    Args:
        zip_path (str): 压缩包的绝对路径。
        extract_to (str): 目标解压目录的路径。

    Returns:
        bool: 解压成功返回 True，过程中发生任何异常返回 False。
    """
    if os.path.exists(extract_to):
        try:
            shutil.rmtree(extract_to)
        except Exception as e:
            print(f"清理目录失败: {e}")

    os.makedirs(extract_to, exist_ok=True)
    print(f"正在解压: {os.path.basename(zip_path)} ...")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for file_info in zf.infolist():
                # 1. 修复文件名编码 (调用 imported utils 中的工具)
                original_name = file_info.filename
                decoded_name = fix_text_encoding(original_name)

                # 2. 过滤 Mac 系统生成的垃圾文件
                if decoded_name.startswith('__MACOSX') or '._' in decoded_name or decoded_name.endswith('.DS_Store'):
                    continue

                # 3. 重写文件名并解压
                # 我们需要保持目录结构，但使用修复后的名字
                file_info.filename = decoded_name
                zf.extract(file_info, extract_to)

        print("解压完成 (已自动过滤 Mac 系统文件)")
        return True
    except Exception as e:
        print(f"解压严重错误: {e}")
        return False


def scan_assignment_files(root_path):
    """
    函数功能：
        扫描解压后的文件夹，提取班级、学号、姓名
    Args:
        root_path (str): 解压后的根目录路径。

    Returns:
        list[dict]: 返回字典列表，每个字典代表一份作业。
    """
    basic_info = []
    print(f"正在扫描 PDF 文件...")

    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith(".pdf") and not file.startswith("._"):
                full_path = os.path.join(root, file)

                # 解析学号，姓名
                try:
                    name_part = file.replace('.pdf', '')
                    if '+' in name_part:
                        s_id, s_name = name_part.split('+', 1)
                    else:
                        s_id, s_name = "Unknown", name_part
                except:
                    s_id, s_name = "Error", "Error"

                # 解析班级
                try:
                    parent_dir = os.path.dirname(root)
                    class_name = os.path.basename(parent_dir)
                    if "班" not in class_name and "未分班" not in class_name:
                        # 简单的容错，防止取到中间层文件夹
                        pass
                except:
                    class_name = "未知"

                basic_info.append({
                    "班级": class_name,
                    "学号": s_id,
                    "姓名": s_name,
                    "文件路径": full_path
                })

    return basic_info


def get_raw_zip_file(raw_dir: str) -> str:
    """
    函数功能：
        从原始数据目录中提取第一个 ZIP 文件路径。

    Args:
        raw_dir (str): 原始数据文件夹路径。

    Returns:
        str: ZIP 文件的绝对路径，如果未找到则返回 None。
    """
    if not os.path.exists(raw_dir):
        return None
    files = [f for f in os.listdir(raw_dir) if f.endswith('.zip')]
    return os.path.join(raw_dir, files[0]) if files else None