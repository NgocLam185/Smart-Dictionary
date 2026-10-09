# 📖 HƯỚNG DẪN TOÀN TẬP VÀ KIẾN TRÚC BACKEND (SMART DICTIONARY)

Dự án **Smart Dictionary Backend** được xây dựng bằng **FastAPI** và cơ sở dữ liệu **SQLite**, kết hợp cấu trúc dữ liệu **Trie** và thuật toán **Levenshtein Distance** nhằm phục vụ tra cứu nhanh, gợi ý từ tự động và sửa lỗi gõ sai.

---

## 📁 1. Cấu Trúc Thư Mục Dự Án

```text
Smart-Dictionary/
└── backend/
    ├── .venv/                      # Môi trường ảo Python
    ├── app/
    │   ├── __init__.py             # Đánh dấu package app
    │   ├── database.py             # Kết nối SQLite & khởi tạo bảng words (Laam-01, Laam-02)
    │   ├── schemas.py              # Định nghĩa Pydantic schemas xác thực dữ liệu (Laam-01, Laam-05)
    │   ├── main.py                 # FastAPI app, Router, Middleware CORS & Endpoints
    │   └── services/               # Tầng xử lý thuật toán & logic nghiệp vụ
    │       ├── __init__.py
    │       ├── trie_service.py     # Cây Trie cho Exact Search & Autocomplete (Laam-06, Laam-07)
    │       └── fuzzy_service.py    # Thuật toán Levenshtein cho Fuzzy Search (Laam-08)
    ├── dictionary.db               # File database SQLite
    ├── requirements.txt            # Danh sách thư viện phụ thuộc
    ├── seed.py                     # Script nạp dữ liệu mẫu ban đầu (Laam-03)
    ├── README.md                   # Tài liệu này
    └── .gitignore                  # Bỏ qua .venv, *.db, cache khi push Git
```

---

## 🗄️ 2. Cơ Sở Dữ Liệu & Data Schema (Task Laam-01, Laam-02, Laam-03)

### Cấu trúc bảng `words` (SQLite)
Được cấu hình trong `app/database.py`:
- `id`: `INTEGER PRIMARY KEY AUTOINCREMENT` - Định danh từ.
- `word`: `TEXT UNIQUE NOT NULL COLLATE NOCASE` - Từ khóa tra cứu (không phân biệt hoa/thường, không trùng lặp).
- `meaning`: `TEXT NOT NULL` - Nghĩa của từ (tiếng Việt).
- `part_of_speech`: `TEXT` - Loại từ (noun, verb, adjective,...).
- `example`: `TEXT` - Câu ví dụ minh họa.

### Dữ liệu mẫu (Seed Data)
Được tạo trong `seed.py` với các từ mẫu: `computer`, `algorithm`, `software`.
Chạy nạp dữ liệu mẫu bằng lệnh:
```powershell
python seed.py
```

---

## 🌐 3. Danh Sách API Endpoints (FastAPI)

Tài liệu Swagger UI tương tác trực tiếp tại: **`http://127.0.0.1:8000/docs`**

| Nhóm | Phương thức | Đường dẫn API | Mô tả | Chi tiết / Tham số |
| :--- | :---: | :--- | :--- | :--- |
| **CRUD** | `GET` | `/api/words` | Lấy danh sách toàn bộ từ | Trả về danh sách dạng `List[WordResponse]` |
| **CRUD** | `POST` | `/api/words` | Thêm từ mới | Body: `word`, `meaning`, `part_of_speech`, `example`. Bắt lỗi 409 nếu trùng |
| **CRUD** | `PUT` | `/api/words/{id}` | Cập nhật thông tin từ | Sửa nghĩa, từ loại, hoặc ví dụ của từ theo `id` |
| **CRUD** | `DELETE` | `/api/words/{id}` | Xóa từ khỏi từ điển | Xóa khỏi SQLite và đồng thời xóa khỏi cây Trie |
| **Search** | `GET` | `/api/search?q={word}` | Tìm kiếm chính xác (Exact Search) | Tra cứu O(k) trên cây Trie (Fallback SQLite) |
| **Search** | `GET` | `/api/suggestions?q={prefix}&limit=5` | Gợi ý từ (Autocomplete) | Tìm kiếm các từ bắt đầu bằng tiền tố trên cây Trie |
| **Search** | `GET` | `/api/search/fuzzy?q={word}&max_distance=2&limit=5` | Tìm gần đúng (Fuzzy Search) | Sử dụng Levenshtein để phát hiện và sửa từ gõ sai |

---

## 🧠 4. Giải Thích Các Thuật Toán Cốt Lõi

### A. Cây Trie (`app/services/trie_service.py`)
- **Mục đích:** Hỗ trợ tìm kiếm từ khóa với độ phức tạp $O(k)$ ($k$ là độ dài từ), độc lập với kích thước cơ sở dữ liệu.
- **Tính năng Autocomplete (`get_suggestions`):**
  1. Duyệt từ gốc cây xuống đến nút kết thúc tiền tố `prefix`.
  2. Dùng thuật toán DFS (Duyệt theo chiều sâu) để gom các từ con hợp lệ.
  3. Trả về danh sách gợi ý theo giới hạn `limit`.

### B. Khoảng Cách Levenshtein (`app/services/fuzzy_service.py`)
- **Mục đích:** Tính số phép biến đổi tối thiểu (thêm, xóa, thay thế ký tự) giữa chuỗi người dùng nhập và các từ trong từ điển.
- **Ứng dụng:** Khi người dùng gõ sai (ví dụ `computr` thay vì `computer`), API sẽ tính khoảng cách bằng 1 và gợi ý từ đúng.

### C. Cơ Chế Đồng Bộ DB $\leftrightarrow$ Trie (`Task Laam-09`)
- **Khi Server khởi động (`lifespan` trong `main.py`):** Tự động truy vấn SQLite và load toàn bộ từ vào cây Trie.
- **Khi Thêm từ (`POST /api/words`):** Ghi vào SQLite thành công $\rightarrow$ nạp ngay vào Trie.
- **Khi Sửa từ (`PUT /api/words/{id}`):** Ghi vào SQLite $\rightarrow$ cập nhật data trong Trie.
- **Khi Xóa từ (`DELETE /api/words/{id}`):** Xóa khỏi SQLite $\rightarrow$ gọi `trie_service.delete()` để xóa khỏi Trie.

---

## 🚀 5. Hướng Dẫn Vận Hành Cho Lập Trình Viên

### Bước 1: Kích hoạt môi trường ảo
Mở PowerShell trong thư mục dự án:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

### Bước 2: Khởi động Server
```powershell
uvicorn app.main:app --reload
```
- Server chạy tại: `http://127.0.0.1:8000`
- API Documentation: `http://127.0.0.1:8000/docs`
- Dừng Server: Bấm tổ hợp phím `Ctrl + C` trong Terminal.

---

## 🎯 6. Bảng Tổng Kết 10 Tasks

- [x] **Laam-01:** Thiết kế schema SQLite & Pydantic.
- [x] **Laam-02:** Tạo SQLite database `dictionary.db`.
- [x] **laam-03:** Seed dữ liệu từ điển mẫu (`seed.py`).
- [x] **laam-04:** Tạo khung FastAPI, CORS, app architecture.
- [x] **Laam-05:** Hoàn thành trọn bộ CRUD API (`GET`, `POST`, `PUT`, `DELETE`).
- [x] **laam-06:** Hoàn thành Search API chính xác qua Trie.
- [x] **Laam-07:** Hoàn thành Suggestion API tiền tố qua Trie.
- [x] **Laam-08:** Hoàn thành Fuzzy API tìm kiếm gần đúng qua Levenshtein.
- [x] **Laam-09:** Cơ chế đồng bộ 2 chiều giữa SQLite và cây Trie (Khởi động, Thêm, Sửa, Xóa).
- [x] **Laam-10:** Kiểm thử API tự động & hoàn thiện tài liệu Swagger `/docs`.
