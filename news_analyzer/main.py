import requests

from crawler import start_crawling
from database import initialize_sqlite

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from collections import Counter
import re
from database import fetch_news_data  # SQLite에서 뉴스 데이터를 가져오는 함수

def main():
    # Step 1: 데이터베이스 초기화
    # print("Step 1: 데이터베이스 초기화")
    # initialize_sqlite()

    # Step 2: 크롤링 실행
    print("Step 2: 크롤링 실행")
    start_crawling()

    # Step 3: 작업 완료 메시지
    print("작업 완료")


# 불용어 리스트 로드
def load_stopwords():
    url = "https://raw.githubusercontent.com/stopwords-iso/stopwords-ko/master/stopwords-ko.txt"
    response = requests.get(url)
    response.raise_for_status()  # HTTP 상태 확인
    stopwords = response.text.splitlines()
    # 추가 커스터마이징 불용어
    custom_stopwords = ["목표가", "전망", "가능성", "발표", "상승", "하락", "내년","투자","마감","기관","증시","주가"]
    stopwords.extend(custom_stopwords)
    return set(stopwords)



# 명사 추출 함수
def extract_nouns(text):
    korean_noun_pattern = re.compile(r'\b[가-힣]{2,}\b')
    return korean_noun_pattern.findall(text)


# TF-IDF 기반 키워드 추출
def calculate_tfidf(filtered_nouns, max_features=20):
    if not filtered_nouns:
        raise ValueError("필터링 후 유효한 명사가 없습니다.")

    vectorizer = TfidfVectorizer(
        token_pattern=r'\b[가-힣]{2,}\b',
        max_features=max_features,  # 상위 N개의 단어만 선택
        max_df=1,
        min_df=1
    )
    tfidf_matrix = vectorizer.fit_transform([" ".join(filtered_nouns)])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[0]

    return sorted(zip(feature_names, tfidf_scores), key=lambda x: x[1], reverse=True)


# 뉴스 데이터 처리 및 TF-IDF 키워드 추출
def extract_top_keywords_with_tfidf():
    # SQLite에서 뉴스 데이터 가져오기
    news_content = fetch_news_data()  # 사용자 정의 함수로 대체

    # 모든 뉴스 기사 텍스트 결합
    all_text = " ".join(news_content)

    # 명사 추출
    nouns = extract_nouns(all_text)

    # 불용어 제거
    stopwords = load_stopwords()
    filtered_nouns = [word for word in nouns if word not in stopwords]

    # TF-IDF 계산 및 상위 키워드 반환
    return calculate_tfidf(filtered_nouns)


# 상위 키워드 출력 함수
def print_top_keywords():
    try:
        top_keywords = extract_top_keywords_with_tfidf()
        if not top_keywords:
            print("키워드가 충분하지 않습니다.")
            return
        print("TF-IDF 기반 상위 키워드:")
        for rank, (word, score) in enumerate(top_keywords, start=1):
            print(f"{rank}. {word} (점수: {score:.4f})")
    except ValueError as e:
        print(f"오류 발생: {e}")
    except Exception as e:
        print(f"예기치 못한 오류: {e}")


# 실행
if __name__ == "__main__":
    print_top_keywords()