# Buổi 9 — API Versioning & Lifecycle Management

Dự án minh họa chiến lược versioning cho Payment API, bao gồm URL versioning, xử lý breaking changes, deprecation headers theo chuẩn RFC 8594, và idempotency.

---

## Mục lục

1. [Cấu trúc dự án](#cấu-trúc-dự-án)
2. [Cài đặt & Chạy](#cài-đặt--chạy)
3. [Các chiến lược Versioning](#các-chiến-lược-versioning)
4. [API v1 — Deprecated](#api-v1--deprecated)
5. [API v2 — Active](#api-v2--active)
6. [So sánh v1 và v2](#so-sánh-v1-và-v2)
7. [Deprecation Notice](#deprecation-notice--thông-báo-ngừng-hỗ-trợ)
8. [Migration Guide](#migration-guide--hướng-dẫn-nâng-cấp)
9. [Kế hoạch Timeline](#kế-hoạch-timeline)

---

## Cấu trúc dự án

```
w9/
├── server.py              # Flask app — đăng ký blueprint v1 & v2
├── client.py              # Script test tất cả endpoints
├── requirements.txt
├── README.md
├── v1/
│   └── __init__.py        # Blueprint API v1 (Deprecated)
└── v2/
    └── __init__.py        # Blueprint API v2 (Active)
```

---

## Cài đặt & Chạy

### 1. Cài dependencies

```bash
pip install -r requirements.txt
```

### 2. Khởi động server

```bash
cd w9
python server.py
```

Server chạy tại `http://localhost:5000`. Kiểm tra nhanh:

```
GET http://localhost:5000/         → thông tin tất cả versions
GET http://localhost:5000/health   → kiểm tra server còn sống
```

### 3. Chạy client test

Mở terminal thứ hai (giữ server đang chạy):

```bash
python client.py
```

Client sẽ lần lượt gọi tất cả endpoints và in kết quả ra màn hình.

---

## Các chiến lược Versioning

### So sánh 3 chiến lược phổ biến

| Chiến lược | Ví dụ | Ưu điểm | Nhược điểm |
|:---|:---|:---|:---|
| **URL Path** *(dự án này dùng)* | `/api/v2/payments` | Rõ ràng, dễ test bằng browser/curl, HTTP cache hoạt động tốt | URL dài hơn |
| **Request Header** | `API-Version: 2` | URL gọn, đúng spirit của REST | Khó test thủ công, dễ bị reverse proxy bỏ qua |
| **Query Parameter** | `/payments?version=2` | Linh hoạt, dễ switch nhanh | Dễ bị bỏ sót, không cache tốt, SEO kém |

### Tại sao chọn URL Path Versioning?

- Nhìn vào URL là biết ngay đang dùng version nào — không cần xem headers hay docs.
- Dễ dàng dùng các công cụ như curl, Postman, browser mà không cần cấu hình thêm.
- Phù hợp với mục tiêu học tập và demo.

---

## API v1 — Deprecated

> **Cảnh báo:** v1 sẽ bị tắt hoàn toàn vào **31/12/2026**. Hãy migrate sang v2.

### POST `/api/v1/payments` — Tạo thanh toán

**Request Body:**

```json
{
  "amount": 100.50,
  "currency": "USD"
}
```

| Trường | Bắt buộc | Kiểu | Mô tả |
|:---|:---:|:---|:---|
| `amount` | Có | `number > 0` | Số tiền cần thanh toán |
| `currency` | Không | `string` | Mặc định `USD`. Hợp lệ: `USD`, `EUR`, `VND`, `GBP` |

**Response `200 OK`:**

```json
{
  "status": "success",
  "message": "Successfully processed payment of 100.5 USD",
  "transaction_id": "a1b2c3d4-..."
}
```

**Deprecation Headers đi kèm mọi response v1:**

```
Deprecation: Thu, 07 May 2026 00:00:00 GMT
Sunset:      Thu, 31 Dec 2026 23:59:59 GMT
Link:        </api/v2/payments>; rel="successor-version"
Warning:     299 - "This API version is deprecated..."
```

---

### GET `/api/v1/payments/<transaction_id>` — Tra cứu giao dịch

Chức năng giới hạn — chỉ trả về thông tin cơ bản.

**Response `200 OK`:**

```json
{
  "status": "success",
  "transaction_id": "a1b2c3d4-...",
  "note": "Status lookup is limited in v1. Migrate to v2 for full transaction details."
}
```

---

## API v2 — Active

### POST `/api/v2/payments` — Tạo thanh toán

**Request Body:**

```json
{
  "amount": 250.00,
  "currency": "USD",
  "user_id": "usr_987654321",
  "payment_method": "CREDIT_CARD"
}
```

| Trường | Bắt buộc | Kiểu | Giá trị hợp lệ |
|:---|:---:|:---|:---|
| `amount` | Có | `number > 0` | Số dương bất kỳ |
| `user_id` | Có | `string` | ID người dùng |
| `payment_method` | Có | `string` | `CREDIT_CARD`, `DEBIT_CARD`, `E_WALLET`, `BANK_TRANSFER` |
| `currency` | Không | `string` | `USD` *(mặc định)*, `EUR`, `VND`, `GBP` |

**Response `201 Created`:**

```json
{
  "data": {
    "transaction_id": "f7e6d5c4-...",
    "status": "COMPLETED",
    "amount": 250.00,
    "currency": "USD",
    "payment_method": "CREDIT_CARD",
    "user_id": "usr_987654321",
    "timestamp": 1746662400
  },
  "meta": {
    "api_version": "v2",
    "idempotency_key": null
  }
}
```

**Response `400 Bad Request` (validation error):**

```json
{
  "error": "Validation Failed",
  "details": [
    "'user_id' is required",
    "'payment_method' must be one of: ['BANK_TRANSFER', 'CREDIT_CARD', 'DEBIT_CARD', 'E_WALLET']"
  ]
}
```

---

### Tính năng Idempotency

Idempotency đảm bảo rằng gửi cùng một request nhiều lần (do retry khi mạng lỗi) sẽ **không tạo ra giao dịch trùng lặp**.

**Cách dùng:** thêm header `Idempotency-Key` với giá trị unique cho mỗi lần thanh toán (nên dùng UUID).

```
POST /api/v2/payments
Idempotency-Key: req_550e8400-e29b-41d4-a716-446655440000
```

**Luồng hoạt động:**

```
Lần 1 (key chưa tồn tại):
  → Server xử lý thanh toán
  → Lưu kết quả vào cache với key đó (TTL: 24h)
  → Trả về 201 Created + header X-Idempotency-Cache: MISS

Lần 2+ (cùng key, trong 24h):
  → Server tìm thấy key trong cache
  → Trả về kết quả cũ ngay lập tức (không xử lý lại)
  → Trả về 200 OK + header X-Idempotency-Cache: HIT
```

| Lần gọi | HTTP Status | `X-Idempotency-Cache` | `transaction_id` |
|:---:|:---:|:---:|:---|
| Lần 1 | `201 Created` | `MISS` | Mới tạo |
| Lần 2, 3... | `200 OK` | `HIT` | Trùng với lần 1 |

> **Lưu ý production:** Triển khai thực tế nên dùng Redis hoặc database với TTL thay cho in-memory dict — để không mất cache khi server restart.

---

### GET `/api/v2/payments/<transaction_id>` — Tra cứu giao dịch

**Response `200 OK`:**

```json
{
  "data": {
    "transaction_id": "f7e6d5c4-...",
    "status": "COMPLETED",
    "note": "This is a simulated status response."
  },
  "meta": { "api_version": "v2" }
}
```

---

## So sánh v1 và v2

| Tiêu chí | v1 | v2 |
|:---|:---|:---|
| **Endpoint** | `/api/v1/payments` | `/api/v2/payments` |
| **Trường bắt buộc** | `amount` | `amount`, `user_id`, `payment_method` |
| **Validation** | Chỉ kiểm tra `amount` tồn tại | Kiểm tra type, giá trị, enum |
| **Cấu trúc response** | Flat JSON | Lồng trong `data` + `meta` |
| **HTTP status tạo mới** | `200 OK` | `201 Created` |
| **Idempotency** | Không có | Có (header `Idempotency-Key`, cache 24h) |
| **GET status lookup** | Giới hạn | Đầy đủ |
| **Deprecation headers** | Có (`Deprecation`, `Sunset`, `Link`, `Warning`) | Không có |
| **Trạng thái** | **Deprecated** — EOL 31/12/2026 | **Active** |

---

## Deprecation Notice — Thông báo ngừng hỗ trợ

**Ngày thông báo:** 07/05/2026  
**Phiên bản ảnh hưởng:** `/api/v1/*`  
**Ngày gỡ bỏ:** 31/12/2026

### Breaking Changes khi lên v2

**1. Trường request mới bắt buộc**

v1 chỉ cần `amount`. v2 bắt buộc thêm `user_id` và `payment_method` — thiếu bất kỳ trường nào sẽ nhận `400 Bad Request`.

**2. Cấu trúc response thay đổi**

```json
// v1 — flat
{ "status": "success", "transaction_id": "...", "message": "..." }

// v2 — có data wrapper
{ "data": { "transaction_id": "...", ... }, "meta": { "api_version": "v2" } }
```

**3. HTTP status code thay đổi**

Thao tác tạo mới: v1 trả `200`, v2 trả `201`. Cần cập nhật code kiểm tra status.

**4. Validation chặt hơn**

`currency` và `payment_method` phải thuộc danh sách giá trị hợp lệ — không còn chấp nhận chuỗi tùy ý.

---

## Migration Guide — Hướng dẫn nâng cấp

### Bước 1 — Đổi URL

```diff
- POST /api/v1/payments
+ POST /api/v2/payments
```

### Bước 2 — Cập nhật request body

```diff
  {
    "amount": 100.50,
    "currency": "USD",
+   "user_id": "usr_123456",
+   "payment_method": "CREDIT_CARD"
  }
```

### Bước 3 — Cập nhật xử lý response

```python
# v1
transaction_id = response["transaction_id"]

# v2
transaction_id = response["data"]["transaction_id"]
```

### Bước 4 — Thêm Idempotency Key cho retry logic

```python
import uuid

headers = {"Idempotency-Key": f"req_{uuid.uuid4()}"}
requests.post("/api/v2/payments", json=payload, headers=headers)
```

### Bước 5 — Cập nhật kiểm tra status code

```python
# v1 thành công trả 200, v2 trả 201
if response.status_code == 201:
    print("Thanh toán thành công!")
elif response.status_code == 200 and response.headers.get("X-Idempotency-Cache") == "HIT":
    print("Idempotency: kết quả đã được cache.")
```

---

## Kế hoạch Timeline

```
Hiện tại                    31/10/2026        31/12/2026
    |                            |                  |
    |---- Parallel Support ------|-- Sunset Period --|-- EOL
    |                            |                  |
    v1 & v2 chạy song song      v1 bắt đầu trả    v1 bị tắt
    v1 response có headers       lỗi ngẫu nhiên    hoàn toàn
    Deprecation + Sunset                            → 410 Gone
```

| Giai đoạn | Thời gian | Hành động |
|:---|:---|:---|
| **Parallel Support** | Nay — 31/10/2026 | v1 và v2 chạy song song. Mọi response v1 có `Deprecation` + `Sunset` header. |
| **Sunset Period** | 01/11/2026 — 30/12/2026 | v1 bắt đầu trả lỗi ngẫu nhiên (tỉ lệ tăng dần) để thúc đẩy migration. |
| **End of Life** | 31/12/2026 | v1 tắt hoàn toàn. Mọi request nhận `410 Gone`. |

### Cách monitoring headers để tự động cảnh báo

Hệ thống monitoring có thể bắt header `Deprecation` hoặc `Sunset` từ response để gửi alert:

```python
resp = requests.post("/api/v1/payments", json=payload)
if "Sunset" in resp.headers:
    sunset_date = resp.headers["Sunset"]
    alert(f"API đang dùng sắp bị tắt vào {sunset_date}. Hãy migrate!")
```
