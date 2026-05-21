# Week 11-12: API Design Patterns

Tổng hợp các mẫu thiết kế API phổ biến, khi nào dùng từng kiến trúc, và cách kết hợp nhiều patterns trong thực tế.

## Cài đặt

```bash
cd w11-12
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 1. Khi nào dùng REST, gRPC, GraphQL?

| Tiêu chí | REST | GraphQL | gRPC |
| :--- | :--- | :--- | :--- |
| **Bản chất** | Resource-based | Query-based | RPC (gọi hàm từ xa) |
| **Giao thức** | HTTP/1.1 | HTTP/1.1 hoặc HTTP/2 | HTTP/2 (bắt buộc) |
| **Định dạng** | JSON, XML | JSON | Protocol Buffers (binary) |
| **Ưu điểm** | Dễ hiểu, chuẩn hóa, dễ cache | Lấy đúng dữ liệu cần, tránh Over/Under-fetching | Cực kỳ nhanh, type-safe, streaming 2 chiều |
| **Dùng khi** | Public API, CRUD tiêu chuẩn, tích hợp bên thứ ba | Frontend phức tạp lấy dữ liệu từ nhiều nguồn | Microservices nội bộ, hệ thống cần hiệu năng cao |

## 2. Các API Design Patterns

### 2.1. CRUD Pattern — `crud/app.py` (port 5001)

Pattern cơ bản nhất: ánh xạ HTTP methods vào thao tác dữ liệu.

| HTTP Method | Endpoint | Hành động |
| :--- | :--- | :--- |
| `POST` | `/users` | Create |
| `GET` | `/users` | Read (danh sách) |
| `GET` | `/users/{id}` | Read (một bản ghi) |
| `PUT` | `/users/{id}` | Update (toàn bộ) |
| `DELETE` | `/users/{id}` | Delete |

```bash
cd crud && python app.py

# Tạo user
curl -X POST http://localhost:5001/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Charlie", "role": "user"}'

# Lấy danh sách
curl http://localhost:5001/users
```

### 2.2. Query Pattern — `query/app.py` (port 5002)

Cho phép client lọc, sắp xếp, phân trang qua query parameters. Tránh Over-fetching.

```bash
cd query && python app.py

# Filter + Sort + Paginate
curl "http://localhost:5002/products?category=A&sort=-price&page=1&limit=5"
```

Response:
```json
{
  "data": [...],
  "meta": {"total": 50, "page": 1, "limit": 5}
}
```

### 2.3. HATEOAS Pattern — `hateoas/app.py` (port 5003)

API trả về dữ liệu kèm `_links` chỉ các hành động được phép ở trạng thái hiện tại. Client không cần hard-code URL hay logic business.

**State machine của Order:**
```
PENDING → (pay) → PAID → (ship) → SHIPPED
        → (cancel) → CANCELLED
PAID    → (refund) → REFUNDED
```

```bash
cd hateoas && python app.py

# ORD123 đang PENDING → trả về link pay và cancel
curl http://localhost:5003/orders/ORD123

# Thực hiện action: chuyển sang PAID
curl -X POST http://localhost:5003/orders/ORD123/pay

# Thử action không hợp lệ
curl -X POST http://localhost:5003/orders/ORD123/ship
# → 422: "Action 'ship' không hợp lệ ở trạng thái 'PENDING'"
```

### 2.4. Webhook / Event-driven Pattern — `webhook/` (port 5004)

Server chủ động push dữ liệu khi có sự kiện, thay vì client liên tục polling.

**Bảo mật:** Sử dụng **HMAC-SHA256** để ký và xác thực payload (giống Stripe, GitHub).

```
Publisher → ký payload → POST /webhook/notifications (Header: X-Webhook-Signature)
Receiver  → xác thực chữ ký → xử lý sự kiện → 200 OK
```

```bash
# Terminal 1
cd webhook && python receiver.py

# Terminal 2
cd webhook && python publisher.py
```

## 3. Kết hợp nhiều Patterns

Trong thực tế, các hệ thống thường dùng nhiều patterns cùng lúc. Ví dụ một hệ thống thương mại điện tử:

| Tình huống | Pattern phù hợp |
| :--- | :--- |
| Quản lý sản phẩm, người dùng | CRUD |
| Tìm kiếm, lọc, phân trang danh sách | Query |
| Luồng trạng thái đơn hàng | HATEOAS |
| Thông báo khi thanh toán xong | Webhook (Event-driven) |
| Giao tiếp giữa các service nội bộ | gRPC |

## 4. Case Studies: Stripe & GitHub

Xem phân tích chi tiết: [`case_studies/STRIPE_GITHUB_ANALYSIS.md`](case_studies/STRIPE_GITHUB_ANALYSIS.md)

**Stripe:** CRUD (RESTful chuẩn) + Idempotency Key + Webhook bắt buộc cho async payment.

**GitHub:** REST (CRUD) + HATEOAS pagination headers + GraphQL v4 cho complex queries + Webhook cho CI/CD.

## Bảng tổng hợp kiến thức

| Yêu cầu | File | Điểm chính |
| :--- | :--- | :--- |
| CRUD Pattern | `crud/app.py` | POST/GET/PUT/DELETE ánh xạ đúng HTTP semantics |
| Query Pattern | `query/app.py` | Filter, sort, paginate qua query params |
| HATEOAS Pattern | `hateoas/app.py` | `_links` theo state, validate transition |
| Webhook/Event-driven | `webhook/publisher.py`, `webhook/receiver.py` | HMAC-SHA256 signature, async push |
| REST vs gRPC/GraphQL | `README.md` (bảng so sánh) | Chọn đúng kiến trúc theo use case |
| Phân tích Stripe/GitHub | `case_studies/STRIPE_GITHUB_ANALYSIS.md` | Pattern combination thực tế |
