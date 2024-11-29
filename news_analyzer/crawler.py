import requests
from bs4 import BeautifulSoup
import time
from database import initialize_sqlite, insert_into_sqlite

def start_crawling():
    # User-Agent 설정
    headers = {'User-Agent': 'Mozilla/5.0'}

    # 뉴스 기사 목록 URL
    news_list_url = 'https://finance.naver.com/news/mainnews.naver'

    ###### 크롤링 1차 작업 : 뉴스 리스트에서 각 주소에 대한 링크를 추출

    # 뉴스 기사 목록 페이지 요청 및 파싱
    response = requests.get(news_list_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 뉴스 목록에서 선택자를 이용해 가져올 부분 변수에 담기
    articles = soup.select('dl > dd.articleSubject > a')

    # 제대로 오는 지 확인
    # print(articles)
    # print(articles[0]['href'])

    # 뉴스 목록 링크 추출
    article_links = ['https://finance.naver.com' + article['href'] for article in articles  ]
    #print(article_links)


    ###### 크롤링 2차 작업 : 추출한 링크로 각 기사의 상세페이지에서 정보를 추출

    for link in article_links:
        time.sleep(1)  # 각 요청 사이에 1초 대기
        article_response = requests.get(link)
        article_soup = BeautifulSoup(article_response.text, 'html.parser')
        #print(article_soup)

        # 리디렉션 URL 추출
        script_tag = article_soup.find('script') # 다를 수도 있으니 참고
        # print(script_tag) # <script> 까지 나온 부분
        # print(script_tag.text) # <script>제외 글만 나온다.
        if script_tag and 'top.location.href' in script_tag.text:
            #URL 주소
            redirected_url = script_tag.text.split("'")[1]  # 최종 URL 추출 ('를 기준으로 나눈다)
            #print(redirected_url)
            article_response = requests.get(redirected_url, headers=headers)  # 최종 URL 요청
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
        # 기사 제목
        title = article_soup.select_one('#title_area span').get_text(strip=True)

        # 기자 이름
        reporter_tag = article_soup.select_one('em.media_end_head_journalist_name')
        if reporter_tag:  # 태그가 존재하면
            reporter = reporter_tag.get_text(strip=True)
        else:  # 태그가 없으면 기본값 설정
            reporter = "기자 정보 없음"

        # 작성 날짜
        date = article_soup.select_one('span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME').get_text(strip=True)

        # 기사 내용
        content = article_soup.select_one('article#dic_area').get_text(strip=True)
        #get_text() : HTML 태그 제거, 태크 안 텍스트만 출력
        #strip=True : 앞 뒤 공백 삭제
        #text : HTML 구조와 텍스트를 함께 반환
        # URL



        # SQLite에 데이터 삽입
        insert_into_sqlite(title, content, redirected_url, date, reporter)