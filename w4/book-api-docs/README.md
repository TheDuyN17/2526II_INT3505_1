# 📚 Book Management API - Buổi 4: OpenAPI Specification & Swagger

## Giới thiệu

Bài tập thực hành Buổi 4 - Viết OpenAPI YAML cho API quản lý sách và render Swagger UI.

## 🔗 Demo

**Swagger UI (GitHub Pages):** [https://theduyn17.github.io/2526II_INT3505_1/w4/book-api-docs/index.html](https://theduyn17.github.io/2526II_INT3505_1/w4/book-api-docs/index.html)

## Tính năng API

### Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/books` | Lấy danh sách sách (hỗ trợ tìm kiếm, lọc, sắp xếp, phân trang) |
| POST | `/books` | Thêm sách mới |
| GET | `/books/{id}` | Lấy thông tin sách theo ID |
| PUT | `/books/{id}` | Cập nhật thông tin sách |
| DELETE | `/books/{id}` | Xóa sách |
| GET | `/books/stats` | Thống kê sách (tổng số, theo thể loại) |
| GET | `/genres` | Lấy danh sách thể loại |

### Tính năng nâng cao

- **Tìm kiếm:** theo tên sách hoặc tác giả (`?search=Python`)
- **Lọc:** theo thể loại (`?genre=Technology`)
- **Sắp xếp:** theo tên, tác giả hoặc năm (`?sort_by=year&sort_order=desc`)
- **Phân trang:** (`?page=1&limit=10`)
- **Thống kê:** tổng số sách, số lượng theo từng thể loại

### Schemas

- **Book** — dữ liệu sách đầy đủ (id, title, author, year, genre)
- **BookInput** — dữ liệu đầu vào khi tạo/cập nhật sách (không có id)
- **BookListResponse** — response có phân trang (total, page, limit, data)
- **StatsResponse** — thống kê (total_books, by_genre, genres_list)

## Cấu trúc thư mục

```
w4/book-api-docs/
├── openapi.yaml       # OpenAPI 3.0 specification
├── index.html         # Swagger UI render
├── app.py             # Flask backend server
├── requirements.txt   # Python dependencies
└── README.md
```

## Hướng dẫn chạy local

### 1. Cài đặt dependencies

```bash
cd w4/book-api-docs
pip install flask flask-cors
```

### 2. Chạy backend server

```bash
python app.py
```

Server chạy tại `http://localhost:3000`

### 3. Chạy Swagger UI

Mở terminal mới:

```bash
npx http-server . -p 8080 -c-1
```

Mở trình duyệt: [http://localhost:8080/index.html](http://localhost:8080/index.html)

### 4. Test API

Trên Swagger UI, bấm **Try it out** ở bất kỳ endpoint nào để gọi API thật.

## Công nghệ sử dụng

- **OpenAPI 3.0.3** — chuẩn mô tả REST API
- **Swagger UI** — render tài liệu API tương tác
- **Flask** — Python web framework cho backend
- **GitHub Pages** — host Swagger UI online
