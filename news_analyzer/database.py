import sqlite3

def initialize_sqlite():
    # SQLite3 데이터베이스 연결
    conn = sqlite3.connect("inbest.db")
    cursor = conn.cursor()

    # 테이블 생성
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
    conn.commit()
    conn.close()
    print("SQLite 테이블 초기화 완료.")

def insert_into_sqlite(title, content, url, date, author):
    conn = sqlite3.connect("inbest.db")
    cursor = conn.cursor()

    try:
        # 중복 확인
        cursor.execute("SELECT COUNT(*) FROM news WHERE url = ?", (url,))
        if cursor.fetchone()[0] > 0:
            print(f"URL 중복으로 삽입 생략: {url}")
            return

        # 데이터 삽입
        cursor.execute("""
        INSERT INTO news (title, content, url, date, author)
        VALUES (?, ?, ?, ?, ?)
        """, (title, content, url, date, author))
        conn.commit()
        print("SQLite 데이터 삽입 완료.")
    except sqlite3.Error as e:
        print(f"SQLite 오류: {e}")
    finally:
        conn.close()

def fetch_news_data():
    conn = sqlite3.connect("inbest.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM news")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

# news_content = fetch_news_data()
# print(f"뉴스 데이터 {len(news_content)}건 로드 완료.")


