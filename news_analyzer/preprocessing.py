import re
from konlpy.tag import Okt

okt = Okt()

def clean_text(text):
    # 1. 소문자 변환 및 특수 문자 제거 (한글, 영문, 숫자, 공백만 남김)
    text = text.lower()
    text = re.sub(r"[^ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9\s]", "", text)

    # 2. 불용어 제거 (주요 조사, 접속사 등)
    stopwords = {"은", "는", "이", "가", "를", "을", "에", "의", "와", "과", "들", "도", "다", "고", "하", "한", "합니다"}
    text = " ".join(word for word in text.split() if word not in stopwords)
    return text

def extract_nouns(text):
    """
    형태소 분석 및 토큰화 함수:
    - 텍스트를 형태소 단위로 분리하고, 명사만 추출하여 리스트로 반환합니다.
    - `Okt.nouns`를 사용하여 명사 기반의 토큰화를 수행합니다.
    """
    # 명사 추출 (형태소 분석 + 명사 토큰화)
    nouns = okt.nouns(text)
    return nouns

def preprocess_article(title, content):
    """
    기사 데이터 전처리 함수:
    - 제목과 본문 텍스트를 정규화(clean_text)하고,
      형태소 분석과 토큰화(extract_nouns)를 통해 명사 리스트로 변환합니다.
    """
    # 제목 정규화
    title = clean_text(title)
    # 본문 정규화
    content = clean_text(content)
    # 제목에서 명사 추출 (형태소 분석 및 토큰화)
    nouns_title = extract_nouns(title)
    # 본문에서 명사 추출 (형태소 분석 및 토큰화)
    nouns_content = extract_nouns(content)
    return nouns_title, nouns_content
