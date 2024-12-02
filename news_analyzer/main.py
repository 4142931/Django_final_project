import requests

from crawler import start_crawling
from database import initialize_sqlite

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from collections import Counter
import re
from database import fetch_news_data  # SQLite에서 뉴스 데이터를 가져오는 함수

def main():
    # Step 1: 데이터베이스 초기화
    print("Step 1: 데이터베이스 초기화")
    initialize_sqlite()

    # Step 2: 크롤링 실행
    print("Step 2: 크롤링 실행")
    start_crawling()

    # Step 3: 작업 완료 메시지
    print("작업 완료")

#불용어 리스트 로드
def load_stopwords():
    url = "https://raw.githubusercontent.com/stopwords-iso/stopwords-ko/master/stopwords-ko.txt"
    response = requests.get(url)
    stopwords = response.text.splitlines()
    return stopwords

def extract_top_keywords_with_tfidf():
    # SQLite에서 뉴스 데이터를 가져옴
    news_content = fetch_news_data()

    # 모든 뉴스 기사 텍스트를 하나로 결합
    all_text = " ".join(news_content)

    # 한글 명사 추출을 위한 정규표현식
    korean_noun_pattern = re.compile(r'\b[가-힣]{2,}\b')
    nouns = korean_noun_pattern.findall(all_text)

    # 불용어 로드 및 제거
    stopwords = load_stopwords()
    filtered_nouns = [word for word in nouns if len(word) > 2 and word not in stopwords]

    # TF-IDF Vectorizer 사용
    # TF-IDF Vectorizer 사용
    vectorizer = TfidfVectorizer(
        token_pattern=r'\b[가-힣]{2,}\b',
        max_df=1,
        min_df=1
    )
    tfidf_matrix = vectorizer.fit_transform([" ".join(filtered_nouns)])
    feature_names = vectorizer.get_feature_names_out()

    # TF-IDF 점수와 단어를 매핑
    tfidf_scores = tfidf_matrix.toarray()[0]
    tfidf_result = [(feature_names[i], tfidf_scores[i]) for i in range(len(feature_names))]

    # 점수 기준으로 상위 10개 추출
    top_keywords = sorted(tfidf_result, key=lambda x: x[1], reverse=True)[:10]

    return top_keywords

if __name__ == "__main__":
    keywords = extract_top_keywords_with_tfidf()
    print("Top 10 Keywords :")
    for keyword, score in keywords:
        print(f"{keyword}: {score:.4f}")