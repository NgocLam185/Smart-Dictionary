Bạn hãy **copy toàn bộ đoạn nội dung bên dưới** và dán vào ô soạn thảo của file `README.md` trên màn hình trình duyệt của bạn nhé:

```markdown
# 📚 SMART DICTIONARY - BACKEND API

Dự án Backend cho ứng dụng **Smart Dictionary**, xây dựng bằng **FastAPI**, cơ sở dữ liệu **SQLite**, kết hợp cấu trúc dữ liệu **Trie** và thuật toán **Levenshtein Distance** phục vụ tra cứu nhanh, gợi ý từ tự động và tìm kiếm gần đúng khi gõ sai từ.

---

## 🛠️ 1. Công Nghệ & Thư Viện Sử Dụng

- **Ngôn ngữ:** Python 3.10+ (Khuyên dùng Python 3.11 - 3.13)
- **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/) - Hiệu năng cao, tự động sinh tài liệu Swagger UI.
- **ASGI Server:** [Uvicorn](https://www.uvicorn.org/) - Chạy máy chủ bất đồng bộ.
- **Xác thực dữ liệu:** [Pydantic v2](https://docs.pydantic.dev/) - Định nghĩa schema request/response.
- **Cơ sở dữ liệu:** SQLite3 (tích hợp sẵn trong Python) với B-Tree index trên cột tra cứu.
- **Cấu trúc dữ liệu & Thuật toán:**
  - **Cây Trie (Prefix Tree):** Tra cứu chính xác $O(k)$ và gợi ý tiền tố (Autocomplete).
  - **Levenshtein Distance:** Quy hoạch động tính khoảng cách chỉnh sửa chuỗi để sửa lỗi chính tả (Fuzzy Search).
- **Kiểm thử tự động:** `pytest` + `httpx`.

---

## 🚀 2. Hướng Dẫn Cài Đặt & Khởi Chạy

### Bước 1: Mở Terminal và vào thư mục backend
```bash
cd backend
```

### Bước 2: Tạo và kích hoạt môi trường ảo (Virtual Environment)
- **Trên Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **Trên macOS / Linux / Git Bash:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Bước 3: Cài đặt các thư viện phụ thuộc
```bash
pip install -r requirements.txt
```

### Bước 4: Khởi tạo Database & Nạp dữ liệu mẫu
```bash
python app/database.py
python seed.py
```
*(Lệnh này sẽ tạo file database `dictionary.db` và nạp sẵn các từ mẫu: `computer`, `algorithm`, `software`).*

### Bước 5: Khởi động Server FastAPI
```bash
uvicorn app.main:app --reload
```
Sau khi chạy, server sẽ hoạt động tại:
- **API URL:** `http://127.0.0.1:8000`
- **Tài liệu Swagger UI tương tác trực tiếp:** 👉 **`http://127.0.0.1:8000/docs`**

---

## 🧪 3. Hướng Dẫn Chạy Test Tự Động
Hệ thống đi kèm bộ kiểm thử toàn diện toàn bộ các endpoints bằng `pytest`:
```bash
pytest test_api.py -v
```

---

## 📡 4. Danh Sách Các API Endpoints

### A. Nhóm Quản Lý Từ Vựng (CRUD API)
- `GET /api/words`: Lấy danh sách toàn bộ từ vựng trong từ điển.
- `POST /api/words`: Thêm một từ mới (tự động nạp vào cây Trie, chống trùng lặp).
  - **Body JSON:** `{"word": "string", "meaning": "string", "part_of_speech": "string", "example": "string"}`
- `PUT /api/words/{word_id}`: Sửa nghĩa, loại từ hoặc ví dụ của từ theo ID.
- `DELETE /api/words/{word_id}`: Xóa từ khỏi SQLite và đồng thời xóa khỏi cây Trie.

### B. Nhóm Thuật Toán Tìm Kiếm (Search Engine)
- `GET /api/search?q={từ_khóa}`: Tìm kiếm chính xác cực nhanh bằng cây Trie ($O(k)$).
- `GET /api/suggestions?q={tiền_tố}&limit=5`: Gợi ý tự động hoàn thành từ (Autocomplete) dựa trên duyệt nhánh Trie.
  - *Ví dụ:* `GET /api/suggestions?q=com` $\rightarrow$ `["computer"]`.
- `GET /api/search/fuzzy?q={từ_gõ_sai}&max_distance=2&limit=5`: Tìm kiếm gần đúng dựa trên khoảng cách Levenshtein.
  - *Ví dụ:* `GET /api/search/fuzzy?q=computr` $\rightarrow$ `[{"word": "computer", "distance": 1}]`.

---

## 📂 5. Cấu Trúc Dự Án
```text
Smart-Dictionary/
├── .gitignore
├── README.md
└── backend/
    ├── app/
    │   ├── database.py             # Kết nối SQLite & Index
    │   ├── schemas.py              # Pydantic models
    │   ├── main.py                 # FastAPI app, Router & Middleware
    │   └── services/
    │       ├── trie_service.py     # Cây Trie (Exact & Autocomplete)
    │       └── fuzzy_service.py    # Thuật toán Levenshtein
    ├── dictionary.db               # SQLite database
    ├── requirements.txt            # Thư viện
    ├── seed.py                     # Script nạp từ mẫu
    └── test_api.py                 # Test tự động pytest
```

---
*Thực hiện bởi: Lâm (Backend Developer)*
```

---

### Sau khi dán xong:
1. Bấm nút màu xanh lá cây **"Commit changes..."** ở góc trên bên phải.
2. Một cửa sổ nhỏ hiện lên, bạn chỉ cần bấm tiếp **"Commit changes"** là file `README.md` sẽ được lưu ngay trên nhánh `feature/backend-api` của repo!
