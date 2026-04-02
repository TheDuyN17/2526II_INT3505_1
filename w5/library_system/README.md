# Library Management System

Hệ thống quản lý thư viện sách viết bằng **Flask**, hỗ trợ đầy đủ CRUD, 3 kiểu phân trang tự động, tìm kiếm/lọc/sắp xếp và HATEOAS links.

---

## Mục lục

1. [Data Model & Schema](#1-data-model--schema)
2. [Danh sách Endpoints](#2-danh-sách-endpoints)
3. [Hướng dẫn cài đặt & chạy](#3-hướng-dẫn-cài-đặt--chạy)
4. [curl Examples](#4-curl-examples)
5. [3 Kiểu phân trang — So sánh chi tiết](#5-3-kiểu-phân-trang--so-sánh-chi-tiết)

---

## 1. Data Model & Schema

### Bảng `books`

| Cột         | Kiểu      | Ràng buộc    | Mô tả                      |
|-------------|-----------|--------------|----------------------------|
| `id`        | INTEGER   | PK, AUTO INC | Khóa chính                 |
| `title`     | TEXT      | NOT NULL     | Tên sách                   |
| `author`    | TEXT      | NOT NULL     | Tên tác giả                |
| `genre`     | TEXT      | NOT NULL     | Thể loại sách              |
| `year`      | INTEGER   | NOT NULL     | Năm xuất bản               |
| `pages`     | INTEGER   | NOT NULL     | Số trang                   |
| `available` | BOOLEAN   | DEFAULT true | Sách có sẵn hay đang mượn  |
| `rating`    | REAL      | DEFAULT 0.0  | Điểm đánh giá (0.0 – 5.0) |
| `isbn`      | TEXT      | UNIQUE       | Mã ISBN                    |

### ERD (Entity Relationship Diagram)

```
┌─────────────────────────────────────────┐
│                  BOOKS                  │
├─────────────────────────────────────────┤
│ PK  id        INTEGER  NOT NULL         │
│     title     TEXT     NOT NULL         │
│     author    TEXT     NOT NULL         │
│     genre     TEXT     NOT NULL         │
│     year      INTEGER  NOT NULL         │
│     pages     INTEGER  NOT NULL         │
│     available BOOLEAN  DEFAULT TRUE     │
│     rating    REAL     DEFAULT 0.0      │
│     isbn      TEXT     UNIQUE           │
└─────────────────────────────────────────┘

(Trong hệ thống này dùng in-memory list; schema trên
 là thiết kế tương đương cho SQL như SQLite / PostgreSQL)
```

### SQL tạo bảng (tham khảo)

```sql
CREATE TABLE books (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT    NOT NULL,
    author    TEXT    NOT NULL,
    genre     TEXT    NOT NULL,
    year      INTEGER NOT NULL,
    pages     INTEGER NOT NULL CHECK(pages > 0),
    available BOOLEAN NOT NULL DEFAULT TRUE,
    rating    REAL    NOT NULL DEFAULT 0.0 CHECK(rating BETWEEN 0 AND 5),
    isbn      TEXT    UNIQUE
);

-- Index để tối ưu tìm kiếm và cursor pagination
CREATE INDEX idx_books_genre  ON books(genre);
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_books_year   ON books(year);
CREATE INDEX idx_books_id     ON books(id);   -- Dùng cho cursor-based
```

---

## 2. Danh sách Endpoints

### Bảng tổng quan

| Method   | URL                      | Mô tả                            |
|----------|--------------------------|----------------------------------|
| `GET`    | `/`                      | Demo UI interactive              |
| `GET`    | `/api/books`             | Lấy danh sách sách (có phân trang) |
| `GET`    | `/api/books/<id>`        | Lấy chi tiết 1 sách              |
| `POST`   | `/api/books`             | Tạo sách mới                     |
| `PUT`    | `/api/books/<id>`        | Cập nhật sách                    |
| `DELETE` | `/api/books/<id>`        | Xóa sách                         |
| `GET`    | `/api/books/genres`      | Danh sách thể loại               |
| `GET`    | `/api/books/stats`       | Thống kê tổng quan               |
| `GET`    | `/api/pagination-info`   | Thông tin về 3 kiểu phân trang   |

### Chi tiết từng endpoint

#### `GET /api/books` — Danh sách sách

**Query parameters:**

| Param      | Kiểu    | Mặc định | Mô tả                              |
|------------|---------|----------|------------------------------------|
| `q`        | string  | —        | Tìm kiếm theo tên sách / tác giả  |
| `genre`    | string  | —        | Lọc theo thể loại                  |
| `author`   | string  | —        | Lọc theo tác giả (chứa từ khóa)   |
| `available`| boolean | —        | Lọc sách có sẵn (`true`/`false`)  |
| `year_from`| integer | —        | Năm xuất bản từ                    |
| `year_to`  | integer | —        | Năm xuất bản đến                   |
| `sort_by`  | string  | `id`     | Sắp xếp: `id/title/author/year/rating/pages` |
| `order`    | string  | `asc`    | Thứ tự: `asc` / `desc`           |
| `page`     | integer | 1        | **Page-based**: số trang           |
| `per_page` | integer | 5        | **Page-based**: số sách mỗi trang  |
| `offset`   | integer | 0        | **Offset-limit**: bỏ qua N sách   |
| `limit`    | integer | 5        | **Offset-limit / Cursor**: lấy N sách |
| `cursor`   | string  | —        | **Cursor-based**: con trỏ vị trí  |

**Auto-detect pagination:** API tự phát hiện kiểu phân trang dựa trên params:
- Có `cursor` → cursor-based
- Có `page` → page-based
- Có `offset` → offset-limit
- Không có gì → page-based (mặc định)

**Response:**
```json
{
  "data": [ { "id": 1, "title": "...", "_links": { ... } } ],
  "meta": {
    "pagination_type": "page-based",
    "page": 1,
    "per_page": 5,
    "total_items": 25,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  },
  "_links": {
    "self":  "http://127.0.0.1:5000/api/books?page=1&per_page=5",
    "next":  "http://127.0.0.1:5000/api/books?page=2&per_page=5",
    "first": "http://127.0.0.1:5000/api/books?page=1&per_page=5",
    "last":  "http://127.0.0.1:5000/api/books?page=5&per_page=5"
  }
}
```

#### `GET /api/books/<id>` — Chi tiết sách

**Response 200:**
```json
{
  "id": 1,
  "title": "Dế Mèn Phiêu Lưu Ký",
  "author": "Tô Hoài",
  "genre": "Thiếu nhi",
  "year": 1941,
  "pages": 196,
  "available": true,
  "rating": 4.8,
  "isbn": "978-604-1-01234-1",
  "_links": {
    "self":       "http://127.0.0.1:5000/api/books/1",
    "update":     "http://127.0.0.1:5000/api/books/1",
    "delete":     "http://127.0.0.1:5000/api/books/1",
    "collection": "http://127.0.0.1:5000/api/books"
  }
}
```

#### `POST /api/books` — Tạo sách mới

**Request body (JSON):**
```json
{
  "title":     "Tên sách",
  "author":    "Tác giả",
  "genre":     "Thể loại",
  "year":      2024,
  "pages":     200,
  "rating":    4.5,
  "isbn":      "978-...",
  "available": true
}
```
- Các trường bắt buộc: `title`, `author`, `genre`, `year`, `pages`
- **Response:** 201 Created + header `Location: /api/books/<id>`

#### `PUT /api/books/<id>` — Cập nhật sách

Gửi JSON với các trường cần cập nhật (partial update). **Response:** 200 OK.

#### `DELETE /api/books/<id>` — Xóa sách

**Response:** 200 OK với message xác nhận.

---

## 3. Hướng dẫn cài đặt & chạy

### Yêu cầu

- Python 3.10+
- pip

### Các bước

```bash
# 1. Vào thư mục project
cd w5/library_system

# 2. (Tuỳ chọn) Tạo virtual environment
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. Cài đặt dependencies
pip install flask

# hoặc dùng requirements.txt
pip install -r requirements.txt

# 4. Chạy server
python app.py
```

Server sẽ khởi động tại `http://127.0.0.1:5000`.

Mở trình duyệt vào `http://127.0.0.1:5000` để xem Demo UI.

---

## 4. curl Examples

### Lấy danh sách — Page-Based

```bash
# Trang 1, 5 sách/trang (mặc định)
curl "http://127.0.0.1:5000/api/books"

# Trang 2, 3 sách/trang
curl "http://127.0.0.1:5000/api/books?page=2&per_page=3"

# Tìm kiếm + lọc thể loại + sắp xếp
curl "http://127.0.0.1:5000/api/books?q=Nguyễn&genre=Thiếu%20nhi&sort_by=rating&order=desc&page=1&per_page=5"
```

### Lấy danh sách — Offset-Limit

```bash
# Bỏ qua 10 sách đầu, lấy 5 sách tiếp theo
curl "http://127.0.0.1:5000/api/books?offset=10&limit=5"

# Offset 0, limit 3
curl "http://127.0.0.1:5000/api/books?offset=0&limit=3"

# Kết hợp filter
curl "http://127.0.0.1:5000/api/books?offset=5&limit=5&genre=Tiểu%20thuyết"
```

### Lấy danh sách — Cursor-Based

```bash
# Lần đầu (không cần cursor)
curl "http://127.0.0.1:5000/api/books?limit=5"

# Lấy trang tiếp (dùng next_cursor từ response trước)
# Ví dụ cursor từ response: "Ng=="
curl "http://127.0.0.1:5000/api/books?cursor=Ng%3D%3D&limit=5"

# Với filter
curl "http://127.0.0.1:5000/api/books?cursor=Ng%3D%3D&limit=5&genre=Tiểu%20thuyết"
```

### Chi tiết sách

```bash
# Lấy sách ID=1
curl "http://127.0.0.1:5000/api/books/1"

# Sách không tồn tại → 404
curl "http://127.0.0.1:5000/api/books/999"
```

### Tạo sách mới

```bash
curl -X POST "http://127.0.0.1:5000/api/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lập Trình Python Cơ Bản",
    "author": "Nguyễn Văn A",
    "genre": "Kỹ thuật",
    "year": 2024,
    "pages": 350,
    "rating": 4.5,
    "available": true
  }'
```

### Cập nhật sách

```bash
# Cập nhật trạng thái và rating của sách ID=1
curl -X PUT "http://127.0.0.1:5000/api/books/1" \
  -H "Content-Type: application/json" \
  -d '{"available": false, "rating": 4.9}'
```

### Xóa sách

```bash
curl -X DELETE "http://127.0.0.1:5000/api/books/1"
```

### Thống kê & thể loại

```bash
# Thống kê tổng quan
curl "http://127.0.0.1:5000/api/books/stats"

# Danh sách thể loại
curl "http://127.0.0.1:5000/api/books/genres"

# Thông tin về 3 kiểu phân trang
curl "http://127.0.0.1:5000/api/pagination-info"
```

### Lọc nâng cao

```bash
# Sách có sẵn, sắp xếp theo rating giảm dần
curl "http://127.0.0.1:5000/api/books?available=true&sort_by=rating&order=desc"

# Sách xuất bản từ 1990 đến 2010
curl "http://127.0.0.1:5000/api/books?year_from=1990&year_to=2010&sort_by=year"

# Tìm theo tác giả Nguyễn Nhật Ánh
curl "http://127.0.0.1:5000/api/books?author=Nguyễn%20Nhật%20Ánh"
```

---

## 5. 3 Kiểu phân trang — So sánh chi tiết

### 5.1 Page-Based Pagination

**Cách dùng:** `?page=2&per_page=5`

**SQL tương đương:**
```sql
-- Trang 2, mỗi trang 5 bản ghi
SELECT * FROM books
ORDER BY id
LIMIT 5 OFFSET 5;   -- OFFSET = (page-1) * per_page
```

**Cơ chế hoạt động:**
```
Dữ liệu: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ...]
                     ↑page=1↑  ↑page=2↑  ↑page=3↑
                    (per_page=5)
```

**Ưu điểm:**
- Thân thiện người dùng: "Trang 1/10", "Trang 5/10"
- Dễ implement số trang trên UI (Google-style)
- Người dùng có thể nhảy đến bất kỳ trang nào
- Dễ cache theo từng trang

**Nhược điểm:**
- **OFFSET scan problem**: Database phải đọc và bỏ qua tất cả rows trước → chậm khi trang lớn
  ```sql
  -- Trang 1000, per_page=10 → OFFSET 9990 → scan 9990 rows!
  SELECT * FROM books LIMIT 10 OFFSET 9990;
  ```
- **Phantom read**: Nếu có INSERT/DELETE khi đang duyệt:
  ```
  Ban đầu: [A, B, C, D, E, F]
  User đọc page 1: [A, B, C]
  Ai đó xóa B: [A, C, D, E, F]
  User đọc page 2: [D, E, F]  ← bỏ qua C!
  ```

**Real-world examples:** Google Search, Shopee, Tiki, blog WordPress

---

### 5.2 Offset-Limit Pagination

**Cách dùng:** `?offset=10&limit=5`

**SQL tương đương:**
```sql
-- Bỏ qua 10 rows đầu, lấy 5 rows tiếp theo
SELECT * FROM books
ORDER BY id
LIMIT 5 OFFSET 10;
```

**Cơ chế hoạt động:**
```
Dữ liệu: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, ...]
                              ↑─────skip 10─────↑ ↑take 5↑
                              offset=10            limit=5
```

**So sánh với Page-Based:**

| Đặc điểm      | Page-Based            | Offset-Limit          |
|---------------|-----------------------|-----------------------|
| Params        | `page`, `per_page`   | `offset`, `limit`     |
| Linh hoạt     | Theo trang cố định   | Bất kỳ row bắt đầu   |
| Thân thiện UI | ✅ Cao               | ⚠️ Thấp hơn          |
| Use case      | User-facing UI        | API, export, analytics|

**Ưu điểm:**
- Trực tiếp mapping 1:1 với SQL OFFSET/LIMIT
- Linh hoạt: bắt đầu ở bất kỳ row nào
- Tốt cho data export, batch processing
- Dễ tính toán vị trí hiện tại

**Nhược điểm:**
- Cùng vấn đề hiệu suất O(n) với offset lớn như page-based
- Không thân thiện người dùng bằng page-based
- Phantom read problem tương tự
- API ít trực quan hơn với end-user

**Real-world examples:** REST API export, admin panels, analytics dashboards, ETL pipelines

---

### 5.3 Cursor-Based Pagination (Keyset Pagination)

**Cách dùng:** `?cursor=Ng==&limit=5`

*(cursor là Base64 encode của ID cuốn sách cuối trong trang trước)*

**SQL tương đương:**
```sql
-- Lần đầu (không có cursor)
SELECT * FROM books
ORDER BY id
LIMIT 6;   -- Lấy limit+1 để detect has_next

-- Có cursor (id > cursor_value)
SELECT * FROM books
WHERE id > 5         -- cursor decode ra id=5
ORDER BY id
LIMIT 6;
```

**Cơ chế hoạt động:**
```
Lần 1: SELECT * WHERE id > 0  LIMIT 6 → [1,2,3,4,5, 6*]
        cursor_next = encode(5) = "NQ=="   (* phần tử thứ 6 chứng tỏ has_next)

Lần 2: SELECT * WHERE id > 5  LIMIT 6 → [6,7,8,9,10, 11*]
        cursor_next = encode(10)

Lần 3: SELECT * WHERE id > 10 LIMIT 6 → [11,12,13,14,15, 16*]
        ...
```

**Tại sao nhanh hơn?**
```sql
-- Page-based OFFSET 10000: phải scan 10000 rows
SELECT * FROM books LIMIT 5 OFFSET 10000;  -- SLOW O(n)

-- Cursor-based: dùng B-tree index, nhảy thẳng đến vị trí
SELECT * FROM books WHERE id > 10000 ORDER BY id LIMIT 5;  -- FAST O(log n)
```

**Ưu điểm:**
- **Hiệu suất O(log n)**: Dùng B-tree index, không scan rows thừa
- **Stable pagination**: Không bị phantom read khi có INSERT/DELETE
  ```
  Ban đầu: [A, B, C, D, E, F]
  Cursor sau trang 1: cursor=C
  Ai đó xóa B: [A, C, D, E, F]
  Trang 2 với cursor=C → [D, E, F] ← chính xác!
  ```
- **Scalable**: Hoạt động tốt với hàng triệu records
- Phù hợp cho real-time data (news feed, notifications)

**Nhược điểm:**
- Không thể nhảy đến trang bất kỳ (chỉ next, không có prev dễ dàng)
- Không hiển thị "Trang X / Y" được
- Cursor phải là unique và ordered field (thường là `id` hoặc `created_at`)
- Phức tạp hơn khi implement multi-column sort
- Cursor là opaque (không đọc được trực tiếp)

**Real-world examples:**
- Twitter/X timeline (`?max_id=...`)
- Instagram feed (`?after=...`)
- Facebook Graph API (`?after=cursor`)
- GitHub API (`Link` header với cursor)
- Elasticsearch `search_after`

---

### 5.4 Bảng so sánh tổng hợp

| Tiêu chí                  | Page-Based       | Offset-Limit     | Cursor-Based        |
|---------------------------|------------------|------------------|---------------------|
| **Query params**          | `page, per_page` | `offset, limit`  | `cursor, limit`     |
| **SQL**                   | `LIMIT x OFFSET (page-1)*x` | `LIMIT x OFFSET y` | `WHERE id > y ORDER BY id LIMIT x+1` |
| **Hiệu suất**             | O(n) — chậm     | O(n) — chậm      | O(log n) — nhanh    |
| **Nhảy trang tự do**      | ✅ Có            | ✅ Có            | ❌ Không            |
| **Hiển thị "Trang X/Y"**  | ✅ Có            | ✅ Có            | ❌ Không            |
| **Ổn định dữ liệu**       | ❌ Có thể lệch   | ❌ Có thể lệch   | ✅ Luôn đúng        |
| **Scalability**           | ❌ Kém           | ❌ Kém           | ✅ Xuất sắc         |
| **Độ phức tạp implement** | ⭐ Đơn giản      | ⭐ Đơn giản      | ⭐⭐⭐ Phức tạp hơn |
| **Thân thiện người dùng** | ✅ Cao           | ⚠️ Trung bình   | ❌ Thấp (cho UI)    |
| **Dùng cho UI**           | ✅ Phù hợp       | ⚠️ Được          | ⚠️ Infinite scroll  |
| **Dùng cho API/export**   | ⚠️ Được          | ✅ Phù hợp       | ✅ Phù hợp          |

### 5.5 Khi nào dùng loại nào?

```
Cần UI thân thiện với số trang?     → Page-Based
Cần linh hoạt offset cho export?    → Offset-Limit
Cần scale với dữ liệu lớn?         → Cursor-Based
Real-time feed / infinite scroll?   → Cursor-Based
Admin panel / analytics?            → Offset-Limit
Google-style search results?        → Page-Based
```

---

## Cấu trúc project

```
library_system/
├── app.py                    # Flask application chính
├── requirements.txt          # Dependencies
├── README.md                 # Tài liệu này
├── pagination/               # Package phân trang
│   ├── __init__.py           # Auto-detect + exports
│   ├── page_based.py         # Page-based pagination
│   ├── offset_limit.py       # Offset-limit pagination
│   └── cursor_based.py       # Cursor-based pagination
└── templates/
    └── index.html            # Demo UI interactive
```
