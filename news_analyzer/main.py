from crawler import start_crawling
from database import initialize_sqlite

def main():
    # Step 1: 데이터베이스 초기화
    print("Step 1: 데이터베이스 초기화")
    initialize_sqlite()

    # Step 2: 크롤링 실행
    print("Step 2: 크롤링 실행")
    start_crawling()

    # Step 3: 작업 완료 메시지
    print("작업 완료")

if __name__ == "__main__":
    main()