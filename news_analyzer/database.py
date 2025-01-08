import sqlite3  # SQLite 데이터베이스 처리 모듈


def initialize_sqlite():
    # SQLite3 데이터베이스 연결
    conn = sqlite3.connect("inbest.db")  # 데이터베이스 파일 생성 또는 연결
    cursor = conn.cursor()

    # 뉴스 데이터 테이블 생성
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE,
        date DATETIME,
        author TEXT
    );
    """)
    conn.commit()  # 변경 사항 저장
    conn.close()  # 연결 종료
    print("SQLite 테이블 초기화 완료.")


def insert_into_sqlite(title, content, url, date, author):
    conn = sqlite3.connect("inbest.db")
    cursor = conn.cursor()

    conn = sqlite3.connect("inbest.db")
    cursor = conn.cursor()

    try:
        # 중복 확인 및 데이터 삽입
        cursor.execute("SELECT 1 FROM news WHERE url = ?", (url,))
        if cursor.fetchone():
            print(f"이미 존재하는 URL, 삽입 생략: {url}")
        else:
            cursor.execute("""
             INSERT INTO news (title, content, url, date, author)
             VALUES (?, ?, ?, ?, ?)
             """, (title, content, url, date, author))
            conn.commit()
            print(f"데이터 삽입 완료: {url}")
    except sqlite3.Error as e:
        print(f"SQLite 오류: {e}")
    finally:
        conn.close()

# def fetch_news_data():
#     conn = sqlite3.connect("inbest.db") # SQLite 데이터베이스 연결
#     cursor = conn.cursor()
#     cursor.execute("SELECT title, content FROM news")  # 뉴스 제목만 가져오기
#     rows = cursor.fetchall()  # [(제목1, 내용1), (제목2, 내용2), ...]
#     conn.close()
#     return rows


# news_content = fetch_news_data()
# print(f"뉴스 데이터 {len(news_content)}건 로드 완료.")

DB_PATH = "C:/Django_final_project/news_analyzer/inbest.db"
def fetch_news_data():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # 테이블에서 데이터 가져오기
        cursor.execute("SELECT title, content, url FROM news ORDER BY date DESC")
        rows = cursor.fetchall()  # [(제목, 내용, url), (제목, 내용, url), ...]
    except sqlite3.Error as e:
        print(f"SQLite 오류: {e}")
        rows = []
    finally:
        conn.close()
    return rows
