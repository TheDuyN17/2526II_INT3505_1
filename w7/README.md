# Product Management API

CRUD Backend cho resource **Product**, được sinh từ **OpenAPI 3.0 spec** theo chuẩn
[openapi-generator](https://openapi-generator.tech/) template `python-flask`.

---

## Giới thiệu

Project này minh họa quy trình **API-first development**:

1. Viết OpenAPI spec (`openapi.yaml`) trước — định nghĩa toàn bộ contract
2. Dùng openapi-generator sinh code skeleton (models, controllers, routing)
3. Điền business logic vào controllers và thêm database layer

Kết quả: một REST API hoàn chỉnh có validation tự động, Swagger UI, và MongoDB persistence.

---

## Công nghệ

| Thành phần | Công nghệ |
|------------|-----------|
| Web framework | [Connexion](https://connexion.readthedocs.io) 2.x + Flask 2.3 |
| Spec-driven routing | OpenAPI 3.0.3 |
| Database | MongoDB 7 |
| Database driver | PyMongo 4.x |
| Containerisation | Docker + Docker Compose |
| Testing | pytest + unittest.mock |
| CI | Travis CI |

---

## Cách OpenAPI Generator hoạt động

```
openapi.yaml  ──► openapi-generator ──► Generated skeleton
    │                                         │
    │  định nghĩa:                            ├── models/         (data classes)
    │  - schemas                              ├── controllers/    (empty stubs)
    │  - endpoints                            ├── openapi/        (copy of spec)
    │  - operationId                          └── main.py         (Connexion app)
    │
    └── Connexion đọc spec ──► auto-wire operationId -> Python function
```

Connexion tự động:
- Tạo route từ `paths` trong spec
- Map `operationId` đến Python function trong controller
- Validate request/response theo `schemas`
- Serve Swagger UI tại `/api/ui/`

---

## Prerequisites

- Python >= 3.11
- Docker Desktop (cho Option A)
- MongoDB (local hoặc Atlas, cho Option B)

---

## Quick Start

### Option A — Docker (khuyến nghị)

```bash
cd w7

# Khởi động API + MongoDB
docker compose up --build -d

# Xem logs
docker compose logs -f app

# Seed dữ liệu mẫu (12 products)
docker compose --profile seed run seed
```

API sẽ chạy tại **http://localhost:8080**
Swagger UI tại **http://localhost:8080/api/ui/**

### Option B — Local

```bash
cd w7

# 1. Tạo và kích hoạt virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Cài dependencies
pip install -r requirements.txt

# 3. Cấu hình môi trường
cp .env.example .env
# Chỉnh MONGODB_URI nếu cần

# 4. Khởi động server
python -m openapi_server
```

Server chạy tại **http://localhost:8080**
Swagger UI tại **http://localhost:8080/api/ui/**

---

## Seed Data

```bash
# Chèn 12 sản phẩm mẫu vào MongoDB
python seed/seed.py

# Script tự động bỏ qua nếu collection đã có dữ liệu
```

Dữ liệu mẫu gồm 12 sản phẩm thuộc đủ 5 categories:
Electronics (4) · Clothing (2) · Books (2) · Food (2) · Sports (2)

---

## API Documentation

Swagger UI tự động được sinh từ `openapi.yaml` tại:
**http://localhost:8080/api/ui/**

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/products` | Lấy danh sách (phân trang, filter, search) |
| `POST` | `/api/products` | Tạo product mới |
| `GET` | `/api/products/{id}` | Lấy chi tiết theo ID |
| `PUT` | `/api/products/{id}` | Thay thế hoàn toàn product |
| `PATCH` | `/api/products/{id}` | Cập nhật một phần product |
| `DELETE` | `/api/products/{id}` | Xóa product |

### Query Parameters — GET /api/products

| Param | Type | Default | Mô tả |
|-------|------|---------|-------|
| `page` | integer | 1 | Số trang |
| `limit` | integer | 10 | Số items/trang (tối đa 100) |
| `sort` | string | `created_at:desc` | Field:direction, ví dụ `price:asc` |
| `category` | string | — | Lọc theo: Electronics, Clothing, Books, Food, Sports |
| `is_active` | boolean | — | Lọc theo trạng thái |
| `search` | string | — | Tìm kiếm theo tên (full-text) |

---

## Ví dụ curl

### Lấy danh sách có filter
```bash
curl "http://localhost:8080/api/products?page=1&limit=5&category=Electronics&sort=price:asc"
```

### Tìm kiếm theo tên
```bash
curl "http://localhost:8080/api/products?search=laptop&is_active=true"
```

### Tạo product mới
```bash
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptop RTX 4090",
    "description": "Laptop gaming hiệu năng cao",
    "price": 2999.99,
    "category": "Electronics",
    "stock": 10
  }'
```

### Lấy chi tiết theo ID
```bash
curl http://localhost:8080/api/products/64a7b2c3d4e5f6789012345a
```

### Cập nhật toàn bộ (PUT)
```bash
curl -X PUT http://localhost:8080/api/products/64a7b2c3d4e5f6789012345a \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptop Updated",
    "price": 2799.99,
    "category": "Electronics",
    "stock": 8
  }'
```

### Cập nhật một phần (PATCH)
```bash
curl -X PATCH http://localhost:8080/api/products/64a7b2c3d4e5f6789012345a \
  -H "Content-Type: application/json" \
  -d '{"price": 1999.99, "stock": 20}'
```

### Xóa product
```bash
curl -X DELETE http://localhost:8080/api/products/64a7b2c3d4e5f6789012345a
```

---

## Cấu trúc Project

```
w7/
├── .openapi-generator/
│   ├── FILES              # Danh sách file được generator tạo ra
│   └── VERSION            # Phiên bản generator (7.6.0)
│
├── openapi_server/        # Main package
│   ├── __init__.py
│   ├── __main__.py        # Entry point: python -m openapi_server
│   ├── main.py            # create_app() — khởi tạo Connexion + MongoDB
│   ├── encoder.py         # Custom JSON encoder (xử lý datetime, Model objects)
│   ├── typing_utils.py    # Typing helpers cho Python 3.8 compatibility
│   ├── util.py            # Deserialisation utilities
│   │
│   ├── controllers/
│   │   └── product_controller.py  # 6 handler functions cho 6 endpoints
│   │                               # Đây là nơi viết business logic
│   │
│   ├── models/            # Data models theo chuẩn openapi-generator
│   │   ├── base_model.py           # Base class: to_dict(), from_dict()
│   │   ├── product.py              # Product model đầy đủ (GET response)
│   │   ├── product_create.py       # Request body cho POST
│   │   ├── product_update.py       # Request body cho PUT/PATCH
│   │   ├── product_list_response.py # Response cho GET list (+ pagination)
│   │   └── error_response.py       # Error response format
│   │
│   ├── openapi/
│   │   └── openapi.yaml   # OpenAPI 3.0.3 spec — source of truth cho routing
│   │
│   ├── test/
│   │   └── test_product_controller.py  # 17 unit tests (mock MongoDB)
│   │
│   └── database/          # Thêm thủ công — không được generator tạo
│       ├── connection.py          # MongoClient với retry logic
│       └── product_repository.py # Class ProductRepository: CRUD operations
│
├── seed/
│   └── seed.py            # Chèn 12 sản phẩm mẫu (idempotent)
│
├── .dockerignore
├── .env.example           # Template cho file .env
├── .gitignore
├── .openapi-generator-ignore  # Files được bảo vệ khi regenerate
├── .travis.yml            # CI config
├── docker-compose.yaml    # API + MongoDB + Seed services
├── Dockerfile
├── git_push.sh
├── requirements.txt
├── setup.py
├── test-requirements.txt
└── tox.ini
```

### Giải thích kiến trúc

```
HTTP Request
    │
    ▼
Connexion (đọc openapi.yaml)
    │  - Validate request theo schema
    │  - Route theo operationId
    ▼
product_controller.py
    │  - Business logic
    │  - Validation bổ sung
    │  - Xử lý lỗi
    ▼
ProductRepository (database/)
    │  - CRUD operations
    │  - Chuyển đổi _id <-> id
    ▼
MongoDB (collection: products)
```

---

## Environment Variables

| Biến | Mặc định | Mô tả |
|------|----------|-------|
| `MONGODB_URI` | `mongodb://localhost:27017/product_db` | MongoDB connection string |
| `PORT` | `8080` | Port server lắng nghe |
| `FLASK_ENV` | `production` | `development` để bật debug mode |

---

## Testing

```bash
# Cài test dependencies
pip install -r test-requirements.txt

# Chạy tất cả tests
pytest openapi_server/test -v

# Chạy với coverage report
pytest openapi_server/test --cov=openapi_server --cov-report=term-missing

# Chạy qua tox (giống CI)
tox
```

Tests sử dụng `unittest.mock` để mock MongoDB — không cần MongoDB thật khi test.

---

## Deploy Production

### Bước 1 — Tạo MongoDB Atlas (miễn phí)

1. Đăng ký tại [cloud.mongodb.com](https://cloud.mongodb.com)
2. Tạo cluster **M0** (free tier)
3. **Database Access** → Tạo user với quyền `readWrite`
4. **Network Access** → Thêm IP `0.0.0.0/0` (cho phép mọi IP)
5. **Connect** → Copy connection string:
   ```
   mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/product_db
   ```

### Bước 2 — Push lên GitHub

```bash
git add .
git commit -m "feat(w7): product management API (openapi-generator python-flask)"
git push origin main
```

### Bước 3 — Deploy trên Render (miễn phí)

1. Đăng nhập [render.com](https://render.com)
2. **New** → **Web Service** → Connect GitHub repo
3. Cấu hình service:

   | Field | Giá trị |
   |-------|---------|
   | Name | `product-api` |
   | Root Directory | `w7` |
   | Runtime | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `python -m openapi_server` |
   | Instance Type | Free |

4. **Environment Variables** → Thêm:

   | Key | Value |
   |-----|-------|
   | `MONGODB_URI` | `mongodb+srv://...` (URI từ bước 1) |
   | `PORT` | `8080` |
   | `FLASK_ENV` | `production` |

5. **Create Web Service** → Chờ deploy ~2-3 phút

### Bước 4 — Seed dữ liệu lên production

```bash
MONGODB_URI="mongodb+srv://..." python seed/seed.py
```

### Bước 5 — Verify

```bash
# Health check
curl https://your-app.onrender.com/api/products

# Swagger UI
open https://your-app.onrender.com/api/ui/
```

### Deploy trên Railway (alternative)

```bash
# Cài Railway CLI
npm install -g @railway/cli

# Login và deploy
railway login
railway init
railway up

# Set environment variables
railway variables set MONGODB_URI="mongodb+srv://..."
railway variables set PORT=8080
```

---

## Re-generate từ OpenAPI spec

Khi update `openapi.yaml`, có thể regenerate code:

```bash
# Cài openapi-generator-cli
npm install -g @openapitools/openapi-generator-cli

# Regenerate (files trong .openapi-generator-ignore được BẢO VỆ)
openapi-generator-cli generate \
  -i openapi_server/openapi/openapi.yaml \
  -g python-flask \
  -o . \
  --package-name openapi_server
```

Files được bảo vệ (không bị overwrite) — khai báo trong `.openapi-generator-ignore`:
- `openapi_server/controllers/product_controller.py`
- `openapi_server/database/`
- `seed/`
- `docker-compose.yaml`
- `README.md`

---

## Troubleshooting

### Lỗi: `Cannot connect to MongoDB`
```
RuntimeError: Cannot connect to MongoDB after 5 attempts.
```
**Nguyên nhân**: MONGODB_URI sai hoặc MongoDB chưa chạy.
**Giải pháp**:
```bash
# Kiểm tra MongoDB local
mongosh --eval "db.adminCommand('ping')"

# Hoặc kiểm tra biến môi trường
echo $MONGODB_URI
```

### Lỗi: `No module named 'openapi_server'`
**Nguyên nhân**: Chưa install package hoặc virtual environment chưa activate.
**Giải pháp**:
```bash
source venv/bin/activate
pip install -r requirements.txt
# Chạy từ thư mục w7/
python -m openapi_server
```

### Lỗi: `swagger_ui_bundle not found`
**Giải pháp**:
```bash
pip install swagger-ui-bundle
```

### Lỗi: Port 8080 đã bị dùng
```bash
# Tìm process đang dùng port 8080
lsof -i :8080          # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Đổi port
PORT=9000 python -m openapi_server
```

### Docker: MongoDB chưa ready khi API start
App có retry logic (5 lần, mỗi lần cách 2 giây).
Nếu vẫn lỗi, kiểm tra healthcheck của MongoDB container:
```bash
docker compose ps
docker compose logs mongodb
```
