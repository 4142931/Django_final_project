from datetime import datetime, timedelta  # 날짜와 시간 관련 모듈
import requests  # HTTP 요청 처리
import schedule
from bs4 import BeautifulSoup  # HTML 파싱
from database import insert_into_sqlite, initialize_sqlite  # SQLite 삽입 함수
import time  # 요청 대기 시간 처리를 위한 모듈

def start_crawling():
    headers = {'User-Agent': 'Mozilla/5.0'}
    base_url = 'https://finance.naver.com/news/mainnews.naver'

    # 일주일 간 날짜 설정
    start_date = datetime.now().date()
    end_date = start_date - timedelta(days=6)

    current_date = start_date

    while current_date >= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        print(f"\n[날짜별 뉴스 확인: {date_str}]")

        for page in range(1, 13):  # 각 날짜에 대해 12페이지 크롤링
            news_list_url = f'{base_url}?date={date_str}&page={page}'
            print(f"[페이지 URL] {news_list_url}")

            try:
                response = requests.get(news_list_url, headers=headers, timeout=10)
                response.raise_for_status()
            except Exception as e:
                print(f"페이지 요청 실패: {news_list_url} - {e}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('dl > dd.articleSubject > a')

            if not articles:
                print("해당 페이지에서 기사를 찾을 수 없습니다.")
                continue

            for article in articles:
                first_article_link = 'https://finance.naver.com' + article['href']

                try:
                    article_response = requests.get(first_article_link, headers=headers, timeout=10)
                    article_response.raise_for_status()
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')

                    # 리디렉션 처리
                    script_tag = article_soup.find('script')
                    if script_tag and 'top.location.href' in script_tag.text:
                        redirected_url = script_tag.text.split("'")[1]
                        article_response = requests.get(redirected_url, headers=headers, timeout=10)
                        article_response.raise_for_status()
                        article_soup = BeautifulSoup(article_response.text, 'html.parser')
                        first_article_link = redirected_url

                    # 기사 정보 추출
                    try:
                        title = article_soup.select_one('#title_area span').get_text(strip=True)
                    except AttributeError:
                        title = "제목 없음"

                    try:
                        reporter_tag = article_soup.select_one('em.media_end_head_journalist_name')
                        reporter = reporter_tag.get_text(strip=True) if reporter_tag else "기자 정보 없음"
                    except AttributeError:
                        reporter = "기자 정보 없음"

                    try:
                        date = article_soup.select_one(
                            'span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME').get_text(strip=True)
                    except AttributeError:
                        date = date_str

                    try:
                        content = article_soup.select_one('article#dic_area').get_text(strip=True)
                    except AttributeError:
                        content = "내용 없음"

                    # 삽입 데이터 확인용 출력
                    print("\n[삽입 데이터 확인]")
                    print(f"제목: {title}")
                    print(f"기자: {reporter}")
                    print(f"날짜: {date}")
                    print(f"내용(일부): {content[:100]}...")
                    print(f"URL: {first_article_link}")

                    # 데이터 저장        (title, content, url, date, author)
                    insert_into_sqlite(title, content,first_article_link, date, reporter)

                except Exception as e:
                    print(f"기사 페이지 요청 실패: {first_article_link} - {e}")
                    continue

        # 날짜 감소
        current_date -= timedelta(days=1)

# 스케줄링 함수
def schedule_crawling():
    print("3시간마다 크롤링을 실행합니다.")
    schedule.every(3).hours.do(start_crawling)

    while True:
        schedule.run_pending()
        time.sleep(1)

# 실행부
if __name__ == "__main__":
    initialize_sqlite()  # 데이터베이스 초기화
    start_crawling()  # 시작 시 실행
    schedule_crawling()  # 이후 3시간마다 실행
