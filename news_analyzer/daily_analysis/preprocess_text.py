"""
텍스트 전처리 함수
"""

import pandas as pd
import re
import os


def preprocess_text(text, stopwords=None, hanja_changes=None):
    """텍스트 전처리 함수"""
    if pd.isna(text):
        return ""

    text = str(text)

    # 한자 변환
    if hanja_changes:
        for hanja, change in hanja_changes.items():
            text = text.replace(hanja, change)

    # 한자 제거
    text = re.sub(r'[\u4e00-\u9fff]+', '', text)

    # 특수문자 제거
    text = re.sub(r'[^\w\s]', ' ', text)

    # 영문자, 숫자 제거
    text = re.sub(r'[a-z0-9]', ' ', text)

    # 연속된 공백 제거 및 양쪽 공백 제거
    text = re.sub(r'\s+', ' ', text).strip()

    # 불용어 제거
    if stopwords:
        text = ' '.join(word for word in text.split() if word not in stopwords)

    return text


def load_dictionaries():
    """사전 데이터 로드"""
    try:
        # 파일 경로 설정
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csv')

        # 불용어 및 한자 변환 사전 로드
        dict_data = pd.read_excel(os.path.join(base_path, 'dict.xlsx'), sheet_name=None)
        stopwords = dict_data['불용어']['stopwords'].tolist()
        hanja_changes = dict_data['한자'].set_index('hanja')['change'].to_dict()

        # 회사명 데이터 로드
        companies_data = pd.read_csv(os.path.join(base_path, 'company_names.csv'))
        company_names = companies_data['name'].tolist()

        return stopwords, hanja_changes, company_names

    except Exception as e:
        print(f"Dictionary loading error: {str(e)}")
        return [], {}, []