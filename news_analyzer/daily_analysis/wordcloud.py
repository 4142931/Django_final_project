import pandas as pd
import re
from collections import Counter
import ast
import os


def extract_keywords(news_data):
    # DataFrame 생성 시 세 개의 컬럼 모두 지정
    df = pd.DataFrame(news_data, columns=['title', 'content', 'author'])

    # 필요한 컬럼(title, content)만 선택
    df = df[['title', 'content']]  # author 컬럼 제외

    # CSV 파일들의 경로 설정
    # 프로젝트의 base 경로를 명시적으로 설정
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'news_analyzer', 'csv')

    # 동의어 사전 로드
    synonyms_df = pd.read_csv(os.path.join(base_path, 'Synonyms_Dict.csv'))
    synonyms_df['Synonyms'] = synonyms_df['Synonyms'].apply(ast.literal_eval)
    synonym_to_word_map = {}
    for index, row in synonyms_df.iterrows():
        for synonym in row['Synonyms']:
            synonym_to_word_map[synonym] = row['word']

    # 불용어 사전 로드
    dict_data = pd.read_excel(os.path.join(base_path, 'dict.xlsx'), sheet_name=None)
    stopwords = dict_data['불용어']['stopwords'].tolist()

    # 감성어 사전 로드
    senti_lex = pd.read_csv(os.path.join(base_path, 'SentiWord_Dict.csv'))
    positive_words = set(senti_lex[senti_lex['polarity'] > 0]['word'])
    negative_words = set(senti_lex[senti_lex['polarity'] < 0]['word'])

    def preprocess_text(text):
        """텍스트 전처리 함수"""
        if pd.isna(text):
            return ""

        text = str(text)
        # 특수문자, 영어, 숫자 제거
        text = re.sub(r'[^가-힣\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # 불용어 제거
        words = text.split()
        words = [word for word in words if word not in stopwords]

        return ' '.join(words)

    def replace_synonyms(text):
        """동의어 처리 함수"""
        words = text.split()
        replaced_words = [synonym_to_word_map.get(word, word) for word in words]
        return ' '.join(replaced_words)

    def extract_words(text):
        """단어 추출 함수"""
        # 2글자 이상의 한글 단어만 추출
        words = text.split()
        return [word for word in words if len(word) >= 2]

    # 텍스트 전처리
    df['processed_content'] = df['title'] + ' ' + df['content']
    df['processed_content'] = df['processed_content'].apply(preprocess_text)
    df['processed_content'] = df['processed_content'].apply(replace_synonyms)

    # 단어 추출
    all_words = []
    for text in df['processed_content']:
        words = extract_words(text)
        all_words.extend(words)

    # 단어 빈도수 계산
    word_counts = Counter(all_words)

    # 상위 50개 단어 선택
    top_words = word_counts.most_common(50)

    # 워드클라우드 데이터 생성 (감성 분석 포함)
    cloud_data = [
        {
            'text': word,
            'size': min(count * 2, 100),  # 크기 조정
            'sentiment': 'positive' if word in positive_words else
            'negative' if word in negative_words else
            'neutral'
        }
        for word, count in top_words
    ]

    return cloud_data