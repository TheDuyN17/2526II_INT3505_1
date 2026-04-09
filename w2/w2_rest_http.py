"""
Buổi 2: Kiến trúc REST và HTTP Fundamentals
=============================================
Sinh viên: TheDuyN17
Repo: btvn/w2

Kiến thức cần đạt:
- Nắm 6 nguyên tắc của kiến trúc REST
- Hiểu HTTP methods, status codes, headers

Kỹ năng cần làm được:
- Thiết kế request/response HTTP cơ bản
- Đánh giá mức độ RESTful của một API
"""

import json
import base64
from datetime import datetime, timezone


# ============================================================================
# PHẦN 1: 6 NGUYÊN TẮC CỦA KIẾN TRÚC REST
# ============================================================================

REST_PRINCIPLES = {
    "1. Client-Server": {
        "mô_tả": "Tách biệt client (giao diện) và server (dữ liệu/logic). "
                  "Client không cần biết server lưu trữ thế nào, "
                  "server không cần biết client hiển thị ra sao.",
        "ví_dụ": "Mobile app và Web app cùng gọi chung một REST API server.",
        "lợi_ích": "Client và Server phát triển độc lập, dễ scale."
    },
    "2. Stateless": {
        "mô_tả": "Mỗi request phải chứa đủ thông tin để server xử lý. "
                  "Server không lưu trạng thái (session) của client.",
        "ví_dụ": "Mỗi request đều gửi kèm Authorization token, "
                  "server không nhớ ai đã đăng nhập từ request trước.",
        "lợi_ích": "Dễ scale horizontal, mỗi server đều xử lý được mọi request."
    },
    "3. Cacheable": {
        "mô_tả": "Response phải cho biết có thể cache được hay không. "
                  "Giúp giảm số lượng request tới server.",
        "ví_dụ": "Header 'Cache-Control: max-age=3600' cho phép cache 1 giờ.",
        "lợi_ích": "Giảm tải server, tăng tốc response cho client."
    },
    "4. Uniform Interface": {
        "mô_tả": "Giao diện thống nhất giữa client và server, gồm: "
                  "Resource identification (URI), Resource manipulation (HTTP methods), "
                  "Self-descriptive messages, HATEOAS.",
        "ví_dụ": "GET /users/1 → lấy user, DELETE /users/1 → xóa user. "
                  "Cùng resource, khác method → khác hành động.",
        "lợi_ích": "API dễ hiểu, dễ sử dụng, nhất quán."
    },
    "5. Layered System": {
        "mô_tả": "Hệ thống được chia thành nhiều lớp (load balancer, API gateway, "
                  "app server, database). Client không biết đang nói chuyện với lớp nào.",
        "ví_dụ": "Request đi qua: CDN → Load Balancer → API Gateway → App Server → DB.",
        "lợi_ích": "Tăng bảo mật, dễ scale từng lớp độc lập."
    },
    "6. Code on Demand (tùy chọn)": {
        "mô_tả": "Server có thể gửi code (JavaScript) để client thực thi. "
                  "Đây là nguyên tắc duy nhất không bắt buộc.",
        "ví_dụ": "Server trả về một đoạn JS để validate form phía client.",
        "lợi_ích": "Giảm logic cứng trên client, linh hoạt hơn."
    }
}


def print_rest_principles():
    """In ra 6 nguyên tắc REST."""
    print("=" * 70)
    print("6 NGUYÊN TẮC CỦA KIẾN TRÚC REST")
    print("=" * 70)
    for name, details in REST_PRINCIPLES.items():
        print(f"\n{'─' * 60}")
        print(f"📌 {name}")
        print(f"   Mô tả:   {details['mô_tả']}")
        print(f"   Ví dụ:   {details['ví_dụ']}")
        print(f"   Lợi ích: {details['lợi_ích']}")


# ============================================================================
# PHẦN 1.5: JWT — JSON WEB TOKEN
# ============================================================================

JWT_EXPLAINED = {
    "định_nghĩa": (
        "JWT (JSON Web Token) là chuẩn mở RFC 7519 để truyền thông tin "
        "dưới dạng JSON object được ký số. Server không lưu session — "
        "mọi thông tin cần thiết nằm trong token."
    ),
    "cấu_trúc": "header.payload.signature  (3 phần ngăn cách bởi dấu '.')",
    "phần": {
        "header": {
            "mô_tả": "Thuật toán ký và loại token",
            "ví_dụ": {"alg": "HS256", "typ": "JWT"}
        },
        "payload": {
            "mô_tả": "Claims — thông tin về user và token",
            "ví_dụ": {
                "sub": "42",           # subject (user id)
                "name": "Duy Nguyễn",
                "role": "admin",
                "iat": 1710000000,     # issued at
                "exp": 1710086400      # expires at (+24h)
            }
        },
        "signature": {
            "mô_tả": "HMACSHA256(base64(header) + '.' + base64(payload), secret)",
            "mục_đích": "Đảm bảo token không bị giả mạo hoặc chỉnh sửa"
        }
    },
    "liên_quan_REST": {
        "Stateless": (
            "JWT giúp đạt nguyên tắc Stateless — server không lưu session, "
            "mỗi request tự mang đủ thông tin xác thực trong Authorization header."
        ),
        "Client-Server": (
            "Client tự lưu JWT (localStorage / cookie), gửi kèm mỗi request. "
            "Server chỉ verify chữ ký, không cần shared session store."
        )
    }
}


def decode_jwt_demo(token: str) -> dict:
    """Giải mã phần payload của JWT (không verify signature — chỉ demo)."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {"error": "Token không hợp lệ"}
        # Thêm padding nếu thiếu
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload
    except Exception:
        return {"error": "Không thể decode token"}


def print_jwt_explained():
    """In ra giải thích về JWT và quan hệ với REST."""
    print("\n" + "=" * 70)
    print("JWT — JSON WEB TOKEN")
    print("=" * 70)

    print(f"\n📌 Định nghĩa: {JWT_EXPLAINED['định_nghĩa']}")
    print(f"\n📐 Cấu trúc:   {JWT_EXPLAINED['cấu_trúc']}")

    print("\n─── Ba phần của JWT ───────────────────────────────────────────────")
    for part_name, part_info in JWT_EXPLAINED["phần"].items():
        print(f"\n  [{part_name.upper()}]")
        print(f"  Mô tả: {part_info['mô_tả']}")
        if "ví_dụ" in part_info:
            print(f"  Ví dụ: {json.dumps(part_info['ví_dụ'], indent=10, ensure_ascii=False)}")
        if "mục_đích" in part_info:
            print(f"  Mục đích: {part_info['mục_đích']}")

    print("\n─── JWT và REST Principles ────────────────────────────────────────")
    for principle, explanation in JWT_EXPLAINED["liên_quan_REST"].items():
        print(f"\n  ✅ {principle}:")
        print(f"     {explanation}")

    # Demo token thực tế
    demo_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        ".eyJzdWIiOiI0MiIsIm5hbWUiOiJEdXkgTmd1eeG7hW4iLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3MTAwMDAwMDAsImV4cCI6MTcxMDA4NjQwMH0"
        ".SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    print("\n─── Demo decode JWT payload ───────────────────────────────────────")
    print(f"  Token: {demo_token[:60]}...")
    payload = decode_jwt_demo(demo_token)
    print(f"  Payload decoded: {json.dumps(payload, indent=4, ensure_ascii=False)}")


# ============================================================================
# PHẦN 2: THIẾT KẾ HTTP REQUEST CHO 5 TÌNH HUỐNG
# ============================================================================

class HTTPRequest:
    """Mô phỏng một HTTP Request."""

    def __init__(self, method, url, headers=None, body=None):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.body = body

    def display(self):
        print(f"\n{self.method} {self.url} HTTP/1.1")
        for key, value in self.headers.items():
            print(f"{key}: {value}")
        if self.body:
            print()
            print(json.dumps(self.body, indent=2, ensure_ascii=False))


class HTTPResponse:
    """Mô phỏng một HTTP Response."""

    def __init__(self, status_code, status_text, headers=None, body=None):
        self.status_code = status_code
        self.status_text = status_text
        self.headers = headers or {}
        self.body = body

    def display(self):
        print(f"\nHTTP/1.1 {self.status_code} {self.status_text}")
        for key, value in self.headers.items():
            print(f"{key}: {value}")
        if self.body:
            print()
            print(json.dumps(self.body, indent=2, ensure_ascii=False))


def scenario_0_jwt_login():
    """Tình huống 0: Đăng nhập và nhận JWT token."""
    print("\n" + "=" * 70)
    print("TÌNH HUỐNG 0: Đăng nhập — Nhận JWT Access Token")
    print("Mục đích: Xác thực người dùng, server trả về JWT để dùng các request sau")
    print("Method: POST — tạo 'session' (token), không idempotent")
    print("=" * 70)

    request = HTTPRequest(
        method="POST",
        url="/api/v1/auth/login",
        headers={
            "Host": "api.example.com",
            "Content-Type": "application/json"
        },
        body={
            "email": "duy@example.com",
            "password": "secret123"
        }
    )

    response = HTTPResponse(
        status_code=200,
        status_text="OK",
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "no-store"   # Token KHÔNG được cache
        },
        body={
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcxMDA4NjQwMH0.abc123",
            "token_type": "Bearer",
            "expires_in": 86400,          # 24 giờ (giây)
            "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
        }
    )

    print("\n📤 REQUEST:")
    request.display()
    print("\n📥 RESPONSE:")
    response.display()
    print("\n  💡 Sau bước này, client lưu access_token và gửi kèm")
    print("     header 'Authorization: Bearer <token>' trong mọi request tiếp theo.")


def scenario_0b_jwt_refresh():
    """Tình huống 0b: Refresh token khi access token hết hạn."""
    print("\n" + "=" * 70)
    print("TÌNH HUỐNG 0b: Refresh JWT Token")
    print("Mục đích: Lấy access_token mới khi token cũ hết hạn (exp)")
    print("Method: POST /auth/refresh — dùng refresh_token để đổi lấy token mới")
    print("=" * 70)

    request = HTTPRequest(
        method="POST",
        url="/api/v1/auth/refresh",
        headers={
            "Host": "api.example.com",
            "Content-Type": "application/json"
        },
        body={
            "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
        }
    )

    response_ok = HTTPResponse(
        status_code=200,
        status_text="OK",
        headers={"Content-Type": "application/json", "Cache-Control": "no-store"},
        body={
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.NEW_PAYLOAD.NEW_SIG",
            "token_type": "Bearer",
            "expires_in": 86400
        }
    )

    response_expired = HTTPResponse(
        status_code=401,
        status_text="Unauthorized",
        headers={"Content-Type": "application/json"},
        body={
            "error": "invalid_grant",
            "message": "Refresh token đã hết hạn hoặc bị thu hồi. Vui lòng đăng nhập lại."
        }
    )

    print("\n📤 REQUEST:")
    request.display()
    print("\n📥 RESPONSE (thành công — token mới):")
    response_ok.display()
    print("\n📥 RESPONSE (thất bại — refresh token hết hạn → redirect login):")
    response_expired.display()


def scenario_1_get_users():
    """Tình huống 1: Lấy danh sách người dùng."""
    print("\n" + "=" * 70)
    print("TÌNH HUỐNG 1: Lấy danh sách người dùng")
    print("Mục đích: Đọc dữ liệu, có phân trang và lọc theo role")
    print("Method: GET — chỉ đọc, không thay đổi server, có thể cache")
    print("=" * 70)

    request = HTTPRequest(
        method="GET",
        url="/api/v1/users?page=1&limit=20&role=admin",
        headers={
            "Host": "api.example.com",
            "Accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."
        }
    )

    response = HTTPResponse(
        status_code=200,
        status_text="OK",
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "max-age=60",
            "X-Total-Count": "45"
        },
        body={
            "data": [
                {"id": 1, "name": "Nguyễn Văn A", "email": "a@example.com", "role": "admin"},
                {"id": 2, "name": "Trần Thị B", "email": "b@example.com", "role": "admin"}
            ],
            "pagination": {
                "current_page": 1,
                "total_pages": 3,
                "total_items": 45,
                "limit": 20
            }
        }
    )

    print("\n📤 REQUEST:")
    request.display()
    print("\n📥 RESPONSE:")
    response.display()


def scenario_2_update_email():
    """Tình huống 2: Cập nhật email người dùng."""
    print("\n" + "=" * 70)
    print("TÌNH HUỐNG 2: Cập nhật email người dùng")
    print("Mục đích: Thay đổi một phần thông tin (partial update)")
    print("Method: PATCH — chỉ gửi trường cần sửa, không ảnh hưởng trường khác")
    print("So sánh: PUT sẽ yêu cầu gửi toàn bộ object, thiếu trường = bị null")
    print("=" * 70)

    request = HTTPRequest(
        method="PATCH",
        url="/api/v1/users/42",
        headers={
            "Host": "api.example.com",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."
        },
        body={
            "email": "newemail@example.com"
        }
    )

    response = HTTPResponse(
        status_code=200,
        status_text="OK",
        headers={"Content-Type": "application/json"},
        body={
            "id": 42,
            "name": "Nguyễn Văn A",
            "email": "newemail@example.com",
            "role": "user",
            "updated_at": "2026-03-12T10:30:00Z"
        }
    )

    print("\n📤 REQUEST:")
    request.display()
    print("\n📥 RESPONSE:")
    response.display()


def scenario_3_create_post():
    """Tình huống 3: Tạo bài viết mới."""
    print("\n" + "=" * 70)
    print("TÌNH HUỐNG 3: Tạo bài viết mới")
    print("Mục đích: Tạo mới resource trên server")
    print("Method: POST — server tự sinh id, trả về 201 Created")
    print("=" * 70)

    request = HTTPRequest(
        method="POST",
        url="/api/v1/posts",
        headers={
            "Host": "api.example.com",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."
        },
        body={
            "title": "Tìm hiểu về RESTful API",
            "content": "REST là một kiến trúc phần mềm được Roy Fielding giới thiệu năm 2000...",
            "tags": ["rest", "api", "http"],
            "status": "draft"
        }
    )

    response = HTTPResponse(
        status_code=201,
        status_text="Created",
        headers={
            "Content-Type": "application/json",
            "Location": "/api/v1/posts/156"
        },
        body={
            "id": 156,
            "title": "Tìm hiểu về RESTful API",
            "content": "REST là một kiến trúc phần mềm được Roy Fielding giới thiệu năm 2000...",
            "tags": ["rest", "api", "http"],
            "status": "draft",
            "author_id": 42,
            "created_at": "2026-03-12T11:00:00Z"
        }
    )

    print("\n📤 REQUEST:")
    request.display()
    print("\n📥 RESPONSE:")
    response.display()


def scenario_4_delete_comment():
    """Tình huống 4: Xóa một bình luận."""
    print("\n" + "=" * 70)
    print("TÌNH HUỐNG 4: Xóa bình luận")
    print("Mục đích: Xóa resource khỏi server")
    print("Method: DELETE — trả về 204 No Content (không cần body)")
    print("URL: Nested resource thể hiện quan hệ comment thuộc post")
    print("=" * 70)

    request = HTTPRequest(
        method="DELETE",
        url="/api/v1/posts/156/comments/789",
        headers={
            "Host": "api.example.com",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."
        }
    )

    response = HTTPResponse(
        status_code=204,
        status_text="No Content",
        headers={}
    )

    print("\n📤 REQUEST:")
    request.display()
    print("\n📥 RESPONSE:")
    response.display()
    print("   (Không có body)")


def scenario_5_replace_profile():
    """Tình huống 5: Thay thế toàn bộ thông tin profile."""
    print("\n" + "=" * 70)
    print("TÌNH HUỐNG 5: Cập nhật toàn bộ profile người dùng")
    print("Mục đích: Thay thế hoàn toàn resource (full replacement)")
    print("Method: PUT — idempotent, gọi nhiều lần kết quả giống nhau")
    print("So sánh: PATCH chỉ gửi 1 trường, PUT gửi toàn bộ object")
    print("=" * 70)

    request = HTTPRequest(
        method="PUT",
        url="/api/v1/users/42/profile",
        headers={
            "Host": "api.example.com",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."
        },
        body={
            "display_name": "Duy Nguyễn",
            "bio": "Backend Developer | Python Enthusiast",
            "location": "Hà Nội, Việt Nam",
            "website": "https://theduyn17.dev",
            "social_links": {
                "github": "https://github.com/TheDuyN17",
                "linkedin": "https://linkedin.com/in/theduyn17"
            }
        }
    )

    response = HTTPResponse(
        status_code=200,
        status_text="OK",
        headers={"Content-Type": "application/json"},
        body={
            "id": 42,
            "display_name": "Duy Nguyễn",
            "bio": "Backend Developer | Python Enthusiast",
            "location": "Hà Nội, Việt Nam",
            "website": "https://theduyn17.dev",
            "social_links": {
                "github": "https://github.com/TheDuyN17",
                "linkedin": "https://linkedin.com/in/theduyn17"
            },
            "updated_at": "2026-03-12T12:00:00Z"
        }
    )

    print("\n📤 REQUEST:")
    request.display()
    print("\n📥 RESPONSE:")
    response.display()


# ============================================================================
# PHẦN 3: PHÂN TÍCH MÃ LỖI HTTP
# ============================================================================

HTTP_ERROR_CODES = {
    # --- 4xx Client Errors ---
    400: {
        "tên": "Bad Request",
        "nhóm": "4xx Client Error",
        "nguyên_nhân": "Request sai cú pháp, thiếu field bắt buộc, hoặc dữ liệu không đúng format",
        "ví_dụ": 'POST /api/users với body {"email": "invalid-email"} → thiếu name, email sai format',
        "cách_xử_lý_client": "Validate dữ liệu trước khi gửi, đọc error message từ response",
        "cách_phòng_server": "Validate input kỹ, trả error message rõ ràng chỉ ra field nào sai"
    },
    401: {
        "tên": "Unauthorized",
        "nhóm": "4xx Client Error",
        "nguyên_nhân": "Chưa xác thực — thiếu token, token hết hạn, hoặc token không hợp lệ",
        "ví_dụ": "GET /api/users mà không gửi header Authorization",
        "cách_xử_lý_client": "Redirect về trang login, hoặc dùng refresh token để lấy token mới",
        "cách_phòng_server": "Dùng middleware xác thực, hỗ trợ token refresh mechanism"
    },
    403: {
        "tên": "Forbidden",
        "nhóm": "4xx Client Error",
        "nguyên_nhân": "Đã xác thực nhưng KHÔNG có quyền truy cập resource này",
        "ví_dụ": "User role=member cố gọi DELETE /api/admin/users/5",
        "cách_xử_lý_client": "Thông báo không đủ quyền, ẩn các chức năng user không có quyền",
        "cách_phòng_server": "Implement RBAC (Role-Based Access Control), check permission trước khi xử lý"
    },
    404: {
        "tên": "Not Found",
        "nhóm": "4xx Client Error",
        "nguyên_nhân": "Resource không tồn tại hoặc URL sai",
        "ví_dụ": "GET /api/users/99999 — user id 99999 không có trong database",
        "cách_xử_lý_client": "Hiển thị trang 404 thân thiện, kiểm tra lại URL",
        "cách_phòng_server": "Validate ID trước khi query, trả message rõ ràng"
    },
    405: {
        "tên": "Method Not Allowed",
        "nhóm": "4xx Client Error",
        "nguyên_nhân": "HTTP method không được hỗ trợ cho endpoint này",
        "ví_dụ": "DELETE /api/users → endpoint chỉ cho phép GET và POST",
        "cách_xử_lý_client": "Kiểm tra lại method, đọc API documentation",
        "cách_phòng_server": "Trả header Allow: GET, POST để client biết method nào được phép"
    },
    409: {
        "tên": "Conflict",
        "nhóm": "4xx Client Error",
        "nguyên_nhân": "Xung đột dữ liệu với trạng thái hiện tại của resource",
        "ví_dụ": "POST /api/users với email đã tồn tại trong hệ thống",
        "cách_xử_lý_client": "Thông báo trùng dữ liệu, gợi ý sửa giá trị bị trùng",
        "cách_phòng_server": "Check unique constraints trước khi insert, trả field nào bị trùng"
    },
    422: {
        "tên": "Unprocessable Entity",
        "nhóm": "4xx Client Error",
        "nguyên_nhân": "Cú pháp JSON đúng nhưng dữ liệu không hợp lệ về mặt logic",
        "ví_dụ": 'POST /api/orders với {"quantity": -5} → số lượng không thể âm',
        "cách_xử_lý_client": "Hiển thị lỗi validation cho từng field",
        "cách_phòng_server": "Validate business logic, trả danh sách lỗi chi tiết theo field"
    },
    429: {
        "tên": "Too Many Requests",
        "nhóm": "4xx Client Error",
        "nguyên_nhân": "Client gửi quá nhiều request trong khoảng thời gian cho phép (rate limit)",
        "ví_dụ": "Gửi 200 request/phút trong khi API chỉ cho phép 100 request/phút",
        "cách_xử_lý_client": "Đọc header Retry-After, áp dụng exponential backoff (1s → 2s → 4s → 8s)",
        "cách_phòng_server": "Dùng rate limiter (token bucket / sliding window), trả header X-RateLimit-*"
    },
    # --- 5xx Server Errors ---
    500: {
        "tên": "Internal Server Error",
        "nhóm": "5xx Server Error",
        "nguyên_nhân": "Lỗi không xác định phía server — exception chưa handle, bug logic, DB crash",
        "ví_dụ": "Code server chia cho 0, hoặc null pointer exception",
        "cách_xử_lý_client": "Hiển thị thông báo chung, cho phép retry, gửi request_id cho support",
        "cách_phòng_server": "Try-catch mọi nơi, logging đầy đủ, dùng monitoring (Sentry, Datadog)"
    },
    502: {
        "tên": "Bad Gateway",
        "nhóm": "5xx Server Error",
        "nguyên_nhân": "Proxy/gateway nhận response không hợp lệ từ upstream server",
        "ví_dụ": "Nginx proxy nhận lỗi từ backend Flask/Django server",
        "cách_xử_lý_client": "Retry sau vài giây, kiểm tra trạng thái service",
        "cách_phòng_server": "Health check upstream servers, thiết lập timeout hợp lý"
    },
    503: {
        "tên": "Service Unavailable",
        "nhóm": "5xx Server Error",
        "nguyên_nhân": "Server tạm thời không khả dụng — đang bảo trì hoặc quá tải",
        "ví_dụ": "Server đang deploy version mới, hoặc RAM/CPU đạt 100%",
        "cách_xử_lý_client": "Hiển thị trang maintenance, tự động retry với backoff",
        "cách_phòng_server": "Blue-green deployment, auto-scaling, trả header Retry-After"
    },
    504: {
        "tên": "Gateway Timeout",
        "nhóm": "5xx Server Error",
        "nguyên_nhân": "Proxy/gateway không nhận được response từ upstream trong thời gian cho phép",
        "ví_dụ": "Backend xử lý query quá lâu (> 30s), Nginx timeout",
        "cách_xử_lý_client": "Retry, hoặc báo user thao tác đang xử lý (async job)",
        "cách_phòng_server": "Optimize slow queries, dùng async processing cho task nặng"
    }
}


def analyze_error_codes():
    """Phân tích và in ra tất cả mã lỗi HTTP."""
    print("\n" + "=" * 70)
    print("PHÂN TÍCH MÃ LỖI HTTP")
    print("=" * 70)

    # Phân nhóm
    client_errors = {k: v for k, v in HTTP_ERROR_CODES.items() if 400 <= k < 500}
    server_errors = {k: v for k, v in HTTP_ERROR_CODES.items() if 500 <= k < 600}

    print("\n" + "─" * 70)
    print("📋 BẢNG TỔNG HỢP")
    print("─" * 70)
    print(f"{'Mã':<6} {'Tên':<28} {'Nhóm':<20}")
    print(f"{'─'*5} {'─'*27} {'─'*19}")
    for code, info in HTTP_ERROR_CODES.items():
        print(f"{code:<6} {info['tên']:<28} {info['nhóm']:<20}")

    print("\n\n" + "─" * 70)
    print("🔴 4xx CLIENT ERRORS — Lỗi do phía client gây ra")
    print("─" * 70)
    for code, info in client_errors.items():
        print(f"\n  ▸ {code} {info['tên']}")
        print(f"    Nguyên nhân:     {info['nguyên_nhân']}")
        print(f"    Ví dụ:           {info['ví_dụ']}")
        print(f"    Client xử lý:   {info['cách_xử_lý_client']}")
        print(f"    Server phòng:    {info['cách_phòng_server']}")

    print("\n\n" + "─" * 70)
    print("🟠 5xx SERVER ERRORS — Lỗi do phía server gây ra")
    print("─" * 70)
    for code, info in server_errors.items():
        print(f"\n  ▸ {code} {info['tên']}")
        print(f"    Nguyên nhân:     {info['nguyên_nhân']}")
        print(f"    Ví dụ:           {info['ví_dụ']}")
        print(f"    Client xử lý:   {info['cách_xử_lý_client']}")
        print(f"    Server phòng:    {info['cách_phòng_server']}")


# ============================================================================
# PHẦN 4: SO SÁNH 401 vs 403
# ============================================================================

def compare_401_vs_403():
    """So sánh chi tiết 401 Unauthorized và 403 Forbidden."""
    print("\n" + "=" * 70)
    print("SO SÁNH 401 UNAUTHORIZED vs 403 FORBIDDEN")
    print("=" * 70)

    comparison = [
        ("Xác thực",    "Chưa xác thực / Token sai",    "Đã xác thực thành công"),
        ("Nguyên nhân", "Thiếu hoặc sai credentials",    "Không đủ quyền (role)"),
        ("Ví dụ",       "Gọi API mà không gửi token",   "User thường gọi API admin"),
        ("Giải pháp",   "Đăng nhập lại / Refresh token", "Yêu cầu nâng quyền"),
    ]

    print(f"\n  {'Tiêu chí':<14} │ {'401 Unauthorized':<32} │ {'403 Forbidden':<32}")
    print(f"  {'─'*14}─┼─{'─'*32}─┼─{'─'*32}")
    for criteria, val_401, val_403 in comparison:
        print(f"  {criteria:<14} │ {val_401:<32} │ {val_403:<32}")

    # Demo request/response
    print("\n  📤 Demo 401:")
    print("  GET /api/v1/admin/users HTTP/1.1")
    print("  (Không có Authorization header)")
    print('  → 401 {"error": "Authentication required"}')

    print("\n  📤 Demo 403:")
    print("  GET /api/v1/admin/users HTTP/1.1")
    print("  Authorization: Bearer <valid_user_token>")
    print('  → 403 {"error": "Admin access required"}')


# ============================================================================
# PHẦN 5: ĐÁNH GIÁ MỨC ĐỘ RESTFUL CỦA MỘT API
# ============================================================================

def evaluate_restfulness():
    """Đánh giá mức độ RESTful của một API theo Richardson Maturity Model."""
    print("\n" + "=" * 70)
    print("ĐÁNH GIÁ MỨC ĐỘ RESTFUL — Richardson Maturity Model")
    print("=" * 70)

    levels = {
        "Level 0 — The Swamp of POX": {
            "mô_tả": "Dùng 1 endpoint duy nhất, 1 method (POST) cho mọi thứ",
            "ví_dụ_xấu": "POST /api → body: {action: 'getUser', id: 1}",
            "đánh_giá": "❌ Không RESTful"
        },
        "Level 1 — Resources": {
            "mô_tả": "Mỗi resource có URI riêng, nhưng chỉ dùng POST",
            "ví_dụ_xấu": "POST /api/users/1 → body: {action: 'get'}",
            "đánh_giá": "⚠️ Bắt đầu RESTful"
        },
        "Level 2 — HTTP Verbs": {
            "mô_tả": "Dùng đúng HTTP methods (GET, POST, PUT, DELETE) + status codes",
            "ví_dụ_tốt": "GET /api/users/1 → 200 OK",
            "đánh_giá": "✅ RESTful (hầu hết API dừng ở đây)"
        },
        "Level 3 — HATEOAS": {
            "mô_tả": "Response chứa links tới các action tiếp theo",
            "ví_dụ_tốt": 'GET /api/users/1 → {"name": "A", "_links": {"update": "/api/users/1", "delete": "/api/users/1"}}',
            "đánh_giá": "🏆 Fully RESTful (ít API đạt được)"
        }
    }

    for level_name, details in levels.items():
        print(f"\n  📊 {level_name}")
        print(f"     Mô tả: {details['mô_tả']}")
        if "ví_dụ_xấu" in details:
            print(f"     Ví dụ: {details['ví_dụ_xấu']}")
        if "ví_dụ_tốt" in details:
            print(f"     Ví dụ: {details['ví_dụ_tốt']}")
        print(f"     {details['đánh_giá']}")


# ============================================================================
# PHẦN 6: BẢNG TỔNG HỢP HTTP METHODS
# ============================================================================

def summarize_http_methods():
    """Bảng tổng hợp HTTP Methods."""
    print("\n" + "=" * 70)
    print("TỔNG HỢP HTTP METHODS")
    print("=" * 70)

    methods = [
        ("GET",    "Đọc dữ liệu",         "Có",    "Không", "Có"),
        ("POST",   "Tạo mới resource",    "Không", "Có",    "Không"),
        ("PUT",    "Thay thế toàn bộ",    "Có",    "Có",    "Không"),
        ("PATCH",  "Cập nhật một phần",   "Không", "Có",    "Không"),
        ("DELETE", "Xóa resource",         "Có",    "Không", "Không"),
    ]

    print(f"\n  {'Method':<9} {'Mục đích':<22} {'Idempotent':<12} {'Có Body':<10} {'Cacheable':<10}")
    print(f"  {'─'*8} {'─'*21} {'─'*11} {'─'*9} {'─'*9}")
    for method, purpose, idempotent, has_body, cacheable in methods:
        print(f"  {method:<9} {purpose:<22} {idempotent:<12} {has_body:<10} {cacheable:<10}")

    print("\n  💡 Nguyên tắc chọn method:")
    print("     - Chỉ đọc dữ liệu      → GET")
    print("     - Tạo mới resource      → POST")
    print("     - Thay toàn bộ resource → PUT")
    print("     - Sửa một phần         → PATCH")
    print("     - Xóa resource          → DELETE")


# ============================================================================
# PHẦN 7: ĐÁNH GIÁ RESTFUL CỦA API DÙNG JWT
# ============================================================================

def evaluate_jwt_api_restfulness():
    """Đánh giá mức độ RESTful của một API cụ thể dùng JWT Auth."""
    print("\n" + "=" * 70)
    print("ĐÁNH GIÁ RESTFUL — API DÙNG JWT AUTHENTICATION")
    print("=" * 70)

    # API mẫu cần đánh giá
    SAMPLE_API = {
        "endpoints": [
            ("POST", "/api/v1/auth/login",           "Đăng nhập, trả JWT"),
            ("POST", "/api/v1/auth/refresh",          "Làm mới access token"),
            ("GET",  "/api/v1/users?page=1&role=admin","Danh sách users"),
            ("GET",  "/api/v1/users/42",              "Lấy user theo id"),
            ("PATCH","/api/v1/users/42",              "Cập nhật email"),
            ("PUT",  "/api/v1/users/42/profile",      "Thay toàn bộ profile"),
            ("POST", "/api/v1/posts",                 "Tạo bài viết"),
            ("DELETE","/api/v1/posts/156/comments/789","Xóa comment"),
        ]
    }

    criteria = [
        {
            "nguyên_tắc": "1. Client-Server",
            "điểm": "✅ ĐẠT",
            "nhận_xét": (
                "Frontend (React/Mobile) và Backend REST API tách biệt hoàn toàn. "
                "JWT trả về cho client tự quản lý — server không cần biết client là gì."
            )
        },
        {
            "nguyên_tắc": "2. Stateless",
            "điểm": "✅ ĐẠT",
            "nhận_xét": (
                "JWT mang đủ thông tin (sub, role, exp) trong payload. "
                "Server chỉ verify chữ ký — không lưu session. "
                "Mỗi request gửi kèm 'Authorization: Bearer <token>' là đủ để xử lý."
            )
        },
        {
            "nguyên_tắc": "3. Cacheable",
            "điểm": "⚠️ MỘT PHẦN",
            "nhận_xét": (
                "GET /users dùng Cache-Control: max-age=60 — đúng. "
                "POST /auth/login dùng Cache-Control: no-store — đúng (token không được cache). "
                "Cần đảm bảo các endpoint mutation (POST/PUT/PATCH) không bị cache."
            )
        },
        {
            "nguyên_tắc": "4. Uniform Interface",
            "điểm": "✅ ĐẠT",
            "nhận_xét": (
                "URI xác định resource rõ ràng (/users/42, /posts/156/comments/789). "
                "HTTP methods đúng ngữ nghĩa (GET đọc, POST tạo, PATCH partial, DELETE xóa). "
                "Response nhất quán có error message và status code đúng."
            )
        },
        {
            "nguyên_tắc": "5. Layered System",
            "điểm": "✅ ĐẠT",
            "nhận_xét": (
                "JWT cho phép nhiều server xử lý request mà không cần shared session store. "
                "API Gateway có thể verify JWT trước khi chuyển tiếp tới backend — "
                "client không cần biết kiến trúc bên trong."
            )
        },
        {
            "nguyên_tắc": "6. HATEOAS (Level 3)",
            "điểm": "❌ CHƯA ĐẠT",
            "nhận_xét": (
                "Response hiện tại không có '_links' chỉ ra action tiếp theo. "
                "Ví dụ: GET /users/42 nên trả thêm "
                "{'_links': {'update': 'PATCH /users/42', 'delete': 'DELETE /users/42'}}. "
                "Hầu hết API thực tế dừng ở Level 2, HATEOAS vẫn hiếm."
            )
        },
    ]

    # In danh sách endpoints
    print("\n─── API Endpoints được đánh giá ───────────────────────────────────")
    print(f"\n  {'Method':<8} {'Endpoint':<40} {'Mô tả'}")
    print(f"  {'─'*7} {'─'*39} {'─'*25}")
    for method, endpoint, desc in SAMPLE_API["endpoints"]:
        print(f"  {method:<8} {endpoint:<40} {desc}")

    # In đánh giá từng tiêu chí
    print("\n─── Đánh giá theo 6 nguyên tắc REST ──────────────────────────────")
    passed = sum(1 for c in criteria if "ĐẠT" in c["điểm"] and "CHƯA" not in c["điểm"])
    partial = sum(1 for c in criteria if "MỘT PHẦN" in c["điểm"])
    failed = sum(1 for c in criteria if "CHƯA ĐẠT" in c["điểm"])

    for c in criteria:
        print(f"\n  {c['điểm']} {c['nguyên_tắc']}")
        print(f"     {c['nhận_xét']}")

    # Tổng kết
    print("\n─── Tổng kết ──────────────────────────────────────────────────────")
    print(f"\n  ✅ Đạt:      {passed}/6 tiêu chí")
    print(f"  ⚠️  Một phần: {partial}/6 tiêu chí")
    print(f"  ❌ Chưa đạt: {failed}/6 tiêu chí")

    level = "Level 2 (HTTP Verbs + Resources)"
    print(f"\n  📊 Mức độ RESTful: {level}")
    print(f"     → API đạt chuẩn REST thực tế (Production-ready).")
    print(f"     → Cải thiện: thêm _links vào response để đạt Level 3 (HATEOAS).")

    # Lỗi phổ biến cần tránh
    print("\n─── Lỗi thường gặp khi dùng JWT ───────────────────────────────────")
    mistakes = [
        ("❌ Lưu JWT trong localStorage",
         "Dễ bị XSS đánh cắp → Nên dùng httpOnly cookie"),
        ("❌ Không set exp trong payload",
         "Token không bao giờ hết hạn → Rủi ro bảo mật nghiêm trọng"),
        ("❌ Đưa thông tin nhạy cảm vào payload",
         "Payload chỉ được base64 encode, ai cũng đọc được → Không lưu password"),
        ("❌ Dùng GET /auth/logout để logout",
         "JWT stateless, server không thể revoke → Dùng blacklist hoặc short exp"),
        ("❌ Secret key quá đơn giản ('secret', '123456')",
         "Dễ bị brute-force → Dùng key ngẫu nhiên ≥ 256-bit"),
    ]
    for mistake, fix in mistakes:
        print(f"\n  {mistake}")
        print(f"  → Khắc phục: {fix}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print_rest_principles()
    print_jwt_explained()

    scenario_0_jwt_login()
    scenario_0b_jwt_refresh()
    scenario_1_get_users()
    scenario_2_update_email()
    scenario_3_create_post()
    scenario_4_delete_comment()
    scenario_5_replace_profile()

    analyze_error_codes()
    compare_401_vs_403()
    evaluate_restfulness()
    summarize_http_methods()
    evaluate_jwt_api_restfulness()
