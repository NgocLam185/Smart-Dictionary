from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sqlite3

from app.database import get_db, init_db
from app import schemas
from app.services.trie_service import trie_service
from app.services.fuzzy_service import fuzzy_service


def sync_db_to_trie():
    """
    Load toàn bộ từ trong DB vào Trie khi khởi động hoặc đồng bộ (Task Laam-09).
    """
    conn = get_db()
    rows = conn.execute("SELECT * FROM words").fetchall()
    conn.close()
    for row in rows:
        data = dict(row)
        trie_service.insert(data["word"], data)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo DB nếu chưa có
    init_db()
    # Nạp dữ liệu từ SQLite vào cây Trie khi khởi động server
    sync_db_to_trie()
    yield


app = FastAPI(
    title="Smart Dictionary API",
    description="Backend API cho ứng dụng Smart Dictionary hỗ trợ Trie Search và Levenshtein Fuzzy Search.",
    version="1.0.0",
    lifespan=lifespan
)

# Cấu hình CORS để frontend React gọi được API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# Task Laam-05: CRUD APIs
# ==========================================================

@app.get("/api/words", response_model=List[schemas.WordResponse], summary="Lấy danh sách tất cả các từ")
def get_all_words():
    conn = get_db()
    rows = conn.execute("SELECT * FROM words").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/api/words", response_model=schemas.WordResponse, status_code=201, summary="Thêm từ mới vào từ điển")
def add_word(word_data: schemas.WordCreate):
    conn = get_db()
    try:
        clean_word = word_data.word.strip().lower()
        cursor = conn.execute(
            "INSERT INTO words (word, meaning, part_of_speech, example) VALUES (?, ?, ?, ?)",
            (clean_word, word_data.meaning, word_data.part_of_speech, word_data.example)
        )
        conn.commit()
        word_id = cursor.lastrowid
        result_data = {**word_data.model_dump(), "id": word_id, "word": clean_word}

        # Đồng bộ vào cây Trie (Task Laam-09)
        trie_service.insert(clean_word, result_data)

        return result_data
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Từ đã tồn tại trong từ điển!")
    finally:
        conn.close()


@app.put("/api/words/{word_id}", response_model=schemas.WordResponse, summary="Cập nhật thông tin từ")
def update_word(word_id: int, word_data: schemas.WordUpdate):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM words WHERE id = ?", (word_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy từ để cập nhật!")

        current_data = dict(row)
        clean_word = current_data["word"]
        updated_meaning = word_data.meaning if word_data.meaning is not None else current_data["meaning"]
        updated_pos = word_data.part_of_speech if word_data.part_of_speech is not None else current_data["part_of_speech"]
        updated_example = word_data.example if word_data.example is not None else current_data["example"]

        conn.execute(
            "UPDATE words SET meaning = ?, part_of_speech = ?, example = ? WHERE id = ?",
            (updated_meaning, updated_pos, updated_example, word_id)
        )
        conn.commit()

        updated_row = conn.execute("SELECT * FROM words WHERE id = ?", (word_id,)).fetchone()
        result_dict = dict(updated_row)

        # Cập nhật lại data trong Trie
        trie_service.insert(clean_word, result_dict)

        return result_dict
    finally:
        conn.close()


@app.delete("/api/words/{word_id}", summary="Xóa từ khỏi từ điển")
def delete_word(word_id: int):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM words WHERE id = ?", (word_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy từ để xóa!")

        word_text = row["word"]
        conn.execute("DELETE FROM words WHERE id = ?", (word_id,))
        conn.commit()

        # Đồng bộ xóa khỏi Trie (Task Laam-09)
        trie_service.delete(word_text)

        return {"message": f"Da xoa thanh cong tu '{word_text}' (ID: {word_id})"}
    finally:
        conn.close()


# ==========================================================
# Task Laam-06: Search API (Exact match sử dụng Trie)
# ==========================================================

@app.get("/api/search", summary="Tìm kiếm chính xác từ vựng (Trie Exact Search)")
def exact_search(q: str = Query(..., description="Từ khóa cần tìm kiếm")):
    word_query = q.strip().lower()

    # Bước 1: Kiểm tra nhanh trong Trie (O(k))
    word_data = trie_service.get_word_data(word_query)
    if word_data:
        return word_data

    # Bước 2: Fallback query SQLite nếu Trie chưa cache
    conn = get_db()
    row = conn.execute("SELECT * FROM words WHERE word = ?", (word_query,)).fetchone()
    conn.close()
    if row:
        data = dict(row)
        trie_service.insert(word_query, data)
        return data

    raise HTTPException(status_code=404, detail=f"Không tìm thấy từ '{q}'")


# ==========================================================
# Task Laam-07: Suggestion API (Autocomplete theo tiền tố Trie)
# ==========================================================

@app.get("/api/suggestions", response_model=List[str], summary="Gợi ý từ tự động hoàn thành (Trie Autocomplete)")
def get_suggestions(
    q: str = Query(..., description="Tiền tố từ khóa"),
    limit: int = 5
):
    prefix = q.strip().lower()
    if not prefix:
        return []
    max_count = int(limit) if not hasattr(limit, "default") else 5
    return trie_service.get_suggestions(prefix, limit=max_count)


# ==========================================================
# Task Laam-08: Fuzzy API (Tìm kiếm gần đúng khi gõ sai từ)
# ==========================================================

@app.get("/api/search/fuzzy", summary="Tìm kiếm gần đúng (Levenshtein Fuzzy Search)")
def fuzzy_search(
    q: str = Query(..., description="Từ gõ sai hoặc cần tìm tương tự"),
    max_distance: int = 2,
    limit: int = 5
):
    query = q.strip().lower()
    if not query:
        return []

    dist = int(max_distance) if not hasattr(max_distance, "default") else 2
    max_count = int(limit) if not hasattr(limit, "default") else 5

    # Lấy danh sách tất cả các từ trong database để so sánh khoảng cách
    conn = get_db()
    rows = conn.execute("SELECT word FROM words").fetchall()
    conn.close()

    candidate_words = [r["word"] for r in rows]
    return fuzzy_service.search(query, candidate_words, max_distance=dist, limit=max_count)
