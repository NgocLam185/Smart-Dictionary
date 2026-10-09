import sqlite3
from pathlib import Path

# File DB sẽ được tạo ngay trong thư mục backend
DB_PATH = Path(__file__).resolve().parent.parent / "dictionary.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Trả kết quả dạng dict, cực kỳ tiện khi làm API
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL COLLATE NOCASE,
                meaning TEXT NOT NULL,
                part_of_speech TEXT,
                example TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_words_word ON words(word COLLATE NOCASE)
        """)
    print("Database da duoc khoi tao thanh cong!")

if __name__ == "__main__":
    init_db()
