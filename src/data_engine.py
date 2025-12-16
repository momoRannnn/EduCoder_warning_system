# 文件位置: src/data_engine.py
import os
import zipfile
import shutil
import pandas as pd


def fix_text_encoding(text):
    """
    自适应编码修复函数：尝试多种解码方式，直到找到可读的中文
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
    通用解压函数，自动处理 Mac/Windows 编码差异及 __MACOSX 垃圾文件
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
    扫描解压后的文件夹，提取班级、学号、姓名
    """
    pdf_files = []
    print(f"正在扫描 PDF 文件...")

    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith(".pdf") and not file.startswith("._"):
                full_path = os.path.join(root, file)

                # 解析文件名
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

                pdf_files.append({
                    "班级": class_name,
                    "学号": s_id,
                    "姓名": s_name,
                    "文件路径": full_path
                })

    return pdf_files