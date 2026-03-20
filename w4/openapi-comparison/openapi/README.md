# OpenAPI Specification

## Giới thiệu

OpenAPI (trước đây là Swagger) là chuẩn phổ biến nhất để mô tả REST API. File được viết bằng YAML hoặc JSON.

## Demo trực tuyến

- **Swagger UI:** [https://theduyn17.github.io/2526II_INT3505_1/w4/openapi-comparison/openapi/index.html](https://theduyn17.github.io/2526II_INT3505_1/w4/openapi-comparison/openapi/index.html)
- **API Server:** Deployed trên Render (chọn server production trong Swagger UI để test)

## Cài đặt & Chạy local

### 1. Cài đặt dependencies

```bash
cd w4/openapi-comparison/openapi
pip install -r requirements.txt
```

### 2. Chạy backend server

```bash
python app.py
```

Server chạy tại `http://localhost:3000`

### 3. Chạy Swagger UI

Mở terminal mới:

```bash
npx http-server . -p 8081 -c-1
```

Mở trình duyệt: [http://localhost:8081/index.html](http://localhost:8081/index.html)

### 4. Test API

Trên Swagger UI, bấm **Try it out** ở bất kỳ endpoint nào rồi bấm **Execute** để gọi API thật.

## Deploy lên Render (production)

### Bước 1: Tạo tài khoản Render

Vào [render.com](https://render.com), đăng ký/đăng nhập bằng GitHub.

### Bước 2: Tạo Web Service

1. Bấm **New → Web Service**
2. Kết nối repo `2526II_INT3505_1`
3. Cấu hình:
   - **Root Directory:** `w4/openapi-comparison/openapi`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Chọn plan **Free** → bấm **Create Web Service**

### Bước 3: Cập nhật server URL

Sau khi deploy xong, Render cấp link dạng `https://library-api-xxxx.onrender.com`. Cập nhật link này vào phần `servers` trong file `library-api.yaml`.

## Cấu trúc thư mục

```
openapi/
├── library-api.yaml   # OpenAPI 3.0 specification
├── index.html         # Swagger UI render
├── app.py             # Flask backend server
├── requirements.txt   # Python dependencies
├── render.yaml        # Render deploy config
└── README.md
```

## Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/books` | Lấy danh sách sách (hỗ trợ search, filter) |
| POST | `/api/books` | Thêm sách mới |
| GET | `/api/books/{id}` | Lấy sách theo ID |
| PUT | `/api/books/{id}` | Cập nhật sách |
| DELETE | `/api/books/{id}` | Xóa sách |

## Đặc điểm

- **Format:** YAML / JSON
- **Ưu điểm:** Chuẩn công nghiệp, hệ sinh thái tool rất lớn (Swagger UI, Codegen, Editor)
- **Nhược điểm:** File YAML có thể dài dòng với API phức tạp
