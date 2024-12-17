from datetime import datetime, timedelta  # 날짜와 시간 관련 모듈
import random  # 랜덤 대기 시간 생성
import requests  # HTTP 요청 처리
from bs4 import BeautifulSoup  # HTML 파싱
from database import insert_into_sqlite  # SQLite 삽입 함수
import time  # 요청 대기 시간 처리를 위한 모듈

def start_crawling():
    # User-Agent 설정: 웹 크롤링 시 브라우저 정보를 포함
    headers = {'User-Agent': 'Mozilla/5.0'}
    base_url = 'https://finance.naver.com/news/mainnews.naver'  # 네이버 금융 뉴스 URL

    # 크롤링 시작과 종료 날짜 설정
    start_date = datetime.strptime('2024-12-15', '%Y-%m-%d')  # 시작 날짜
    end_date = datetime.strptime('2024-12-15', '%Y-%m-%d')  # 종료 날짜
    delta = timedelta(days=1)  # 하루씩 감소시키는 간격

    # 날짜별 크롤링 루프
    current_date = start_date
    while current_date >= end_date:
        date_str = current_date.strftime('%Y-%m-%d')  # yyyy-mm-dd 형식으로 날짜 변환
        print(f"==== {date_str} 크롤링 시작 ====")

        last_articles = None  # 중복 데이터 확인을 위한 변수
        for page in range(1, 20):  # 각 날짜에 대해 최대 20 페이지 크롤링
            news_list_url = f'{base_url}?date={date_str}&page={page}'  # 페이지별 URL 생성
            try:
                # HTTP 요청
                response = requests.get(news_list_url, headers=headers, timeout=10)
                response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
            except requests.RequestException as e:
                print(f"Failed to fetch page {page} on {date_str}: {e}")
                break

            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('dl > dd.articleSubject > a')  # 뉴스 제목에 해당하는 a 태그 선택

            # 중복 데이터 확인
            article_links = ['https://finance.naver.com' + article['href'] for article in articles]
            if not articles or (last_articles and set(article_links) == set(last_articles)):
                print(f"중복 데이터 감지 또는 더 이상 데이터 없음 (Page: {page})")
                break
            last_articles = article_links

            # 각 뉴스 기사 크롤링
            for link in article_links:
                time.sleep(random.uniform(2, 5))  # 요청 간 랜덤 대기
                try:
                    article_response = requests.get(link, headers=headers, timeout=10)
                    article_response.raise_for_status()
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                except requests.RequestException as e:
                    print(f"Failed to fetch article: {link} - {e}")
                    continue

                # 리디렉션 URL 처리
                script_tag = article_soup.find('script')
                if script_tag and 'top.location.href' in script_tag.text:
                    redirected_url = script_tag.text.split("'")[1]  # 리디렉션 URL 추출
                    try:
                        article_response = requests.get(redirected_url, headers=headers, timeout=10)
                        article_response.raise_for_status()
                        article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    except requests.RequestException as e:
                        print(f"Failed to fetch redirected article: {redirected_url} - {e}")
                        continue
                else:
                    redirected_url = link

                # 기사 정보 추출
                try:
                    title = article_soup.select_one('#title_area span').get_text(strip=True)  # 제목
                except AttributeError:
                    title = "제목 없음"

                try:
                    reporter_tag = article_soup.select_one('em.media_end_head_journalist_name')  # 기자 정보
                    reporter = reporter_tag.get_text(strip=True) if reporter_tag else "기자 정보 없음"
                except AttributeError:
                    reporter = "기자 정보 없음"

                try:
                    date = article_soup.select_one(
                        'span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME').get_text(strip=True)  # 날짜
                except AttributeError:
                    date = "날짜 정보 없음"

                try:
                    content = article_soup.select_one('article#dic_area').get_text(strip=True)  # 본문
                except AttributeError:
                    content = "내용 없음"

                # SQLite에 데이터 삽입
                insert_into_sqlite(title, content, redirected_url, date, reporter)
                print(f"삽입 데이터: 제목={title}, URL={redirected_url}, 작성자={reporter}, 날짜={date}")
            print(f"======================================{page}page 작업완료========================================")

        # 날짜를 하루 감소
        current_date -= delta
        print(f"==== {date_str} 크롤링 완료 ====")

if __name__ == '__main__':
    start_crawling()