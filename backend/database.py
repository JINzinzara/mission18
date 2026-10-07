import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent / "movies.db"


def get_conn():
    """DB에 연결. 요청마다 새로 열고, 쓰고 나면 close"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    conn = get_conn()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        title         TEXT NOT NULL,
        release_date  TEXT NOT NULL,
        director      TEXT NOT NULL,
        genre         TEXT NOT NULL,
        poster_url      TEXT NOT NULL
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id        INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
        author          TEXT NOT NULL,
        text            TEXT NOT NULL,
        created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        sentiment       TEXT NOT NULL,
        sentiment_score REAL NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def fetch_all(sql, params=()):
    """SELECT 결과 전부를 dict 리스트로 담음"""
    conn = get_conn()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_one(sql, params=()):
    """SELECT 결과 한 줄을 dict로, 없으면 None 반환"""
    conn = get_conn()
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return dict(row) if row else None


def execute(sql, params=()):
    """INSERT / DELETE 를 실행하고 저장. 추가한 데이터의 id를 반환"""
    conn = get_conn()
    cur = conn.execute(sql, params)
    conn.commit()
    conn.close()
    return cur.lastrowid


if __name__ == "__main__":
    create_tables()

    insert_sql = """
        INSERT INTO movies
            (title, release_date, director, genre, poster_url)
        VALUES (?, ?, ?, ?, ?)
    """

    movie_params = (
        "오디세이",
        "2026-08-05",
        "크리스토퍼 놀란",
        "전쟁, 드라마, 액션, 모험, 스릴러, 판타지, 가상역사극, 서사시",
        "https://i.namu.wiki/i/9E-vQ4uyTToFcmYd74EaaWVTevnxAfR6W-OiULnvrlzbxvAVJ2s4_EdWC0VGcmBFbjBKO14DHy47OZXIo4CP3lLW_6488bPY97p0KG_pJklq4vYAsOtFhIFSSPxqIhfKhKgpVvk_vgrU5NIYOhUq7A.webp",
    )

    new_id = execute(insert_sql, movie_params)
    print("등록 ID:", new_id)

    saved_movie = fetch_one("SELECT * FROM movies WHERE id = ?", (new_id,))
    print("등록 후 조회:", saved_movie)

    execute("DELETE FROM movies WHERE id = ?", (new_id,))
    print("삭제 후 조회:", fetch_one("SELECT * FROM movies WHERE id = ?", (new_id,)))
