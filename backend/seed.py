from app.database import get_db

words = [
    ("computer", "máy tính", "noun", "I bought a new computer."),
    ("algorithm", "thuật toán", "noun", "Trie is a fast algorithm."),
    ("software", "phần mềm", "noun", "Software engineering is fun.")
]

def seed_data():
    with get_db() as conn:
        conn.executemany("""
            INSERT OR IGNORE INTO words (word, meaning, part_of_speech, example)
            VALUES (?, ?, ?, ?)
        """, words)
    print("Da nap du lieu mau thanh cong!")

if __name__ == "__main__":
    seed_data()
