from preprocessing import preprocess_article
from database import fetch_news_data

def main():


    # Step 1: 데이터 로드
    print("Step 1: 데이터 로드")
    raw_articles = fetch_news_data()  # [(title, content), ...]
    if not raw_articles:
        print("데이터가 없습니다. 크롤링 후 다시 시도하세요.")
        return

    # Step 2: 전처리
    print("Step 2: 전처리")
    processed_titles = [" ".join(preprocess_article(title, content)[0]) for title, content in raw_articles]
    processed_contents = [" ".join(preprocess_article(title, content)[1]) for title, content in raw_articles]

    print("전처리된 제목 5개:")
    for i, title in enumerate(processed_titles[:5]):
        print(f"{i + 1}. {title}")

    print("\n전처리된 본문 5개:")
    for i, content in enumerate(processed_contents[:5]):
        print(f"{i + 1}. {content}")


if __name__ == "__main__":
    main()
