# KYCdb/utils.py

import pandas as pd


def extract_data(file):
    data = pd.read_excel(file)  # 假设上传的是 Excel 文件
    extracted_data = {}

    # 自动识别“时间”和“金额”等常用字段
    if '时间' in data.columns:
        extracted_data['时间'] = data['时间'].tolist()
    if '金额' in data.columns:
        extracted_data['金额'] = data['金额'].tolist()
    # 可以根据需要扩展字段

    return extracted_data
