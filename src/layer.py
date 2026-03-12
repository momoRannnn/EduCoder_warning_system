# src/warning_model.py
"""
模块功能：
    负责将学生按照时间进行分类
    分类逻辑：对于通关时间在4小时以内的，判断为正常
            对于通关时间大于4小时的，判断为数据失真，不符合常理
            对于通关时间小于 15分钟的，时间过短，有 ai 作弊或抄袭的嫌疑
            对于通关时间大于中位数两倍的，可能存在学习吃力，可以稍作注意
            通关状态为未完成的，也是同样的预警，没有按时完成作业

依赖关系：
    pandas: 利用其的 dataframe 作为存储的数据结构，且 pandas 计算中位数比较方便快捷
    utils：使用该模块的parse_time_to_minutes将字符串转化为分钟数便于计算
"""
import pandas as pd
from src.utils import parse_time_to_minutes


def classify(results: list) -> pd.DataFrame:
    """
    功能：
    将原始字典列表转化为 DataFrame，并进行分层预警分类。

    Args：
    results(list): 识别完 pdf得到的 dictionary 列表

    Return：
    pd.DataFrame：转化为 dataframe 便于计算和展示
    """
    if not results:
        return pd.DataFrame()

    #1.载入原始数据
    df = pd.DataFrame(results)
    df['耗时(分钟)'] = df['耗时'].apply(parse_time_to_minutes)
    df['分类标签'] = '正常'  # 默认状态

    #2.划定“高质量有效数据”用于计算基准
    valid_data = df[(df['耗时(分钟)'] > 0) &#条件：耗时大于0，小于12小时(720分钟)，且包含“通关”字眼
                    (df['耗时(分钟)'] <= 720) &
                    (df['状态'].str.contains('通关', na=False))]

    #3.计算每个班级的动态边界
    if not valid_data.empty:
        baselines = valid_data.groupby('班级')['耗时(分钟)'].agg(# 分组计算第一四分位数和第三四分位数
            Q1=lambda x: x.quantile(0.25),
            Q3=lambda x: x.quantile(0.75),
            Median = 'median'
        ).reset_index()

        #计算四分位距和边界
        baselines['IQR'] = baselines['Q3'] - baselines['Q1']
        baselines['下界_lower'] = baselines.apply(
            lambda x: max(20.0, x['Median'] * 0.35) if x['Median'] > 40 else x['Median'] * 0.4,
            axis=1
        )
        baselines['上界_upper'] = baselines['Q3'] + 1.5 * baselines['IQR']
        baselines.loc[baselines['IQR'] == 0, '上界_upper'] += 60.0

        #将算好的边界贴回原表格中对应的班级
        df = df.merge(baselines[['班级', '下界_lower', '上界_upper']], on='班级', how='left')
    else:
        #极端情况：如果全校没有一个正常数据
        df['下界_lower'] = 10.0
        df['上界_upper'] = 240.0

    #填补某些没有基准的班级(例如该班全员跨天，导致 valid_data 为空)
    df['下界_lower'] = df['下界_lower'].fillna(10.0)
    df['上界_upper'] = df['上界_upper'].fillna(240.0)

    #4.打标签
        # A. 跨天/数据失真 (大于12小时)
    df.loc[df['耗时(分钟)'] > 720, '分类标签'] = '灰色 (跨天/数据失真)'

        # B. 学习吃力 (未跨天，且大于该班级的动态上界)
    df.loc[(df['耗时(分钟)'] <= 720) & (df['耗时(分钟)'] > df['上界_upper']), '分类标签'] = '黄色 (学习吃力)'

        # C. 秒刷作弊
    df.loc[(df['耗时(分钟)'] >0) & (df['耗时(分钟)'] < df['下界_lower']), '分类标签'] = '红色 (疑似秒刷)'

        # D. 截止后补交
    df.loc[df['状态'] == '截止后通关', '分类标签'] = '黄色 (截止后补交作业)'

        # E. 未完成
    df.loc[df['状态'].isin(['未通关', '未开启', '无法判定', 'OCR失败']), '分类标签'] = '红色 (未完成)'

    # 5. 精简列并返回
    final_columns = ['姓名', '学号', '班级', '耗时(分钟)', '状态', '分类标签']
    return df[final_columns]