#src/raw_file_processor.py
"""
模块功能：
    这个模块主要负责解压文件，并根据文件夹结构构建基本的学生信息框架（班级，学号，姓名）

说明：
    因为我开发的平台是 mac，和 Windows 平台会有不兼容的情况，为了增加兼容性，我添加了编码修复函数，防止乱码的出现

依赖关系：
    os:文件路径操作
    zipfile：解压文件
    shutil：清理文件夹
"""
import os
import zipfile
import shutil


def fix_text_encoding(text):
    """
    函数功能：
        自适应编码修复函数：尝试多种解码方式，直到找到可读的中文
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
        return text# 如果无法编码回 cp437，说明它可能已经被正确处理过，或者也是乱码

    encodings = ['utf-8', 'gbk']# 定义尝试列表：优先尝试 UTF-8 (Mac/Linux)，然后尝试 GBK (Windows)

    for enc in encodings:
        try:
            return raw_bytes.decode(enc)
        except:
            continue

    return text# 如果都失败了，返回原始乱码，至少比报错强


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
                # 1. 修复文件名编码
                original_name = file_info.filename
                decoded_name = fix_text_encoding(original_name)

                # 2. 过滤 Mac 系统生成的垃圾文件 (关键！)
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