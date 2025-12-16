import os
import pandas as pd
from src.data_engine import unzip_file, scan_assignment_files

"""动态配置路径"""
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def find_zip_file():
    """自动寻找 raw 文件夹下的第一个 zip 文件"""
    if not os.path.exists(RAW_DATA_DIR):
        os.makedirs(RAW_DATA_DIR)
        return None

    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith('.zip')]
    if files:
        return os.path.join(RAW_DATA_DIR, files[0])  # 返回找到的第一个
    else:
        return None


def main():
    print("=== 学业预警系统 (EduCoder Warning) 启动 ===")

    # 1. 自动寻找 ZIP 包
    zip_path = find_zip_file()
    if not zip_path:
        print(f"错误：在 {RAW_DATA_DIR} 下未找到 .zip 文件。")
        print("请将头歌导出的压缩包放入 data/raw 文件夹中！")
        return

    # 2. 解压
    if unzip_file(zip_path, PROCESSED_DIR):

        # 3. 扫描文件
        # 注意：解压后通常会有一层以作业名命名的文件夹
        # 我们扫描整个 processed 文件夹即可
        all_data = scan_assignment_files(PROCESSED_DIR)

        if not all_data:
            print("⚠️ 未扫描到任何 PDF 文件，请检查解压内容。")
            return

        # 4. 导出初步名单
        df = pd.DataFrame(all_data)
        print(f"\n扫描成功！共发现 {len(df)} 份作业。")
        print("前 5 条数据预览：")
        print(df[['班级', '姓名', '学号']].head())

        # 保存到 data 目录
        output_file = os.path.join(BASE_DIR, "data", "1_file_list.xlsx")
        df.to_excel(output_file, index=False)
        print(f"\n文件清单已保存至: {output_file}")
        print("下一步：我们将读取这些 PDF 中的'通关状态'和'耗时'...")


if __name__ == "__main__":
    main()