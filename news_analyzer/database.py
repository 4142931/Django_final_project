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
    # SQLite3에 데이터 삽입
    conn = sqlite3.connect("inbest.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO news (title, content, url, date, author)
        VALUES (?, ?, ?, ?, ?)
        """, (title, content, url, date, author))
        conn.commit()
        print("SQLite 데이터 삽입 완료.")
    except sqlite3.IntegrityError:
        print("중복된 URL로 인해 데이터가 삽입되지 않았습니다.")
    finally:
        conn.close()