"""
Version 4: + Cacheable (Full REST API)
=======================================
Thêm so với V3:
  ✅ Cache-Control headers — client biết cache bao lâu
  ✅ ETag — fingerprint của data, tránh gửi lại data không đổi
  ✅ 304 Not Modified — data chưa đổi, không cần gửi body
  ✅ Rate Limiting — 429 Too Many Requests
  ✅ Request ID — tracking mỗi request

Nguyên tắc Cacheable:
  - Response PHẢI cho biết có thể cache được hay không
  - GET requests → nên cache (Cache-Control: max-age=60)
  - POST/PUT/PATCH/DELETE → không cache (Cache-Control: no-store)
  - ETag: hash của data → client gửi If-None-Match → 304 nếu không đổi
  - Lợi ích: Giảm tải server, tăng tốc cho client

Tổng kết 4 nguyên tắc đã tích hợp:
  V1: ✅ Client-Server — tách biệt client/server
  V2: ✅ Uniform Interface — chuẩn REST, HATEOAS, consistent format
  V3: ✅ Stateless — JWT, server không lưu session
  V4: ✅ Cacheable — ETag, Cache-Control, 304, Rate Limiting

Cài đặt: pip install flask pyjwt
Chạy: python v4_cacheable.py
"""

from flask import Flask, jsonify, request, g, make_response
from datetime import datetime, timezone, timedelta
from functools import wraps
import jwt
import json
import hashlib
import time
import uuid

app = Flask(__name__)

SECRET_KEY = "your-secret-key-change-in-production"

# ============================================================================
# DATABASE
# ============================================================================

users_db = [
    {"id": 1, "name": "Nguyễn Văn A", "email": "a@example.com", "role": "admin",
     "password": "admin123", "created_at": "2026-01-15T08:00:00Z"},
    {"id": 2, "name": "Trần Thị B", "email": "b@example.com", "role": "user",
     "password": "user123", "created_at": "2026-02-01T10:30:00Z"},
    {"id": 3, "name": "Lê Văn C", "email": "c@example.com", "role": "user",
     "password": "user456", "created_at": "2026-02-15T14:00:00Z"},
    {"id": 4, "name": "Phạm Thị D", "email": "d@example.com", "role": "admin",
     "password": "admin456", "created_at": "2026-03-01T09:00:00Z"},
    {"id": 5, "name": "Hoàng Văn E", "email": "e@example.com", "role": "user",
     "password": "user789", "created_at": "2026-03-10T16:00:00Z"},
]

next_id = 6

# Rate limiting storage (trong production dùng Redis)
rate_limit_store = {}  # {ip: {"count": N, "reset_at": timestamp}}
RATE_LIMIT = 30        # 30 requests
RATE_WINDOW = 60       # per 60 seconds


# ============================================================================
# HELPERS
# ============================================================================

def success_response(data, status_code=200, pagination=None, links=None):
    response = {"data": data}
    if pagination:
        response["pagination"] = pagination
    if links:
        response["_links"] = links
    return jsonify(response), status_code


def error_response(status_code, message, details=None):
    response = {
        "error": {
            "code": status_code,
            "message": message,
            "request_id": g.get("request_id", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
    if details:
        response["error"]["details"] = details
    return jsonify(response), status_code


def build_user_links(user_id):
    return {
        "self": f"/api/v1/users/{user_id}",
        "update": f"/api/v1/users/{user_id}",
        "delete": f"/api/v1/users/{user_id}",
        "collection": "/api/v1/users"
    }


def user_with_links(user):
    safe_user = {k: v for k, v in user.items() if k != "password"}
    return {**safe_user, "_links": build_user_links(user["id"])}


def generate_etag(data):
    """
    Tạo ETag — fingerprint của data.
    Nếu data không đổi → ETag giống → trả 304 Not Modified.
    """
    data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return '"' + hashlib.md5(data_str.encode()).hexdigest() + '"'


# ============================================================================
# JWT AUTHENTICATION (from V3)
# ============================================================================

def generate_token(user):
    payload = {
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return error_response(401, "Missing Authorization header")

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return error_response(401, "Invalid Authorization format. Use: Bearer <token>")

        try:
            payload = jwt.decode(parts[1], SECRET_KEY, algorithms=["HS256"])
            g.current_user = {
                "user_id": payload["user_id"],
                "email": payload["email"],
                "role": payload["role"]
            }
        except jwt.ExpiredSignatureError:
            return error_response(401, "Token expired. Please login again.")
        except jwt.InvalidTokenError:
            return error_response(401, "Invalid token.")

        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.current_user["role"] != "admin":
            return error_response(403, "Admin access required",
                                  details={"required_role": "admin",
                                           "your_role": g.current_user["role"]})
        return f(*args, **kwargs)
    return decorated


# ============================================================================
# MIDDLEWARE — Rate Limiting + Request ID + Cache Headers
# ============================================================================

@app.before_request
def before_request_handler():
    """
    Middleware chạy TRƯỚC mỗi request:
    1. Gán Request ID — tracking unique cho mỗi request
    2. Rate Limiting — chặn nếu quá nhiều request → 429
    """
    # 1. Request ID
    g.request_id = str(uuid.uuid4())[:8]

    # 2. Rate Limiting (429 Too Many Requests)
    client_ip = request.remote_addr
    now = time.time()

    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = {"count": 0, "reset_at": now + RATE_WINDOW}

    bucket = rate_limit_store[client_ip]

    # Reset nếu đã qua window
    if now > bucket["reset_at"]:
        bucket["count"] = 0
        bucket["reset_at"] = now + RATE_WINDOW

    bucket["count"] += 1

    if bucket["count"] > RATE_LIMIT:
        retry_after = int(bucket["reset_at"] - now)
        resp = make_response(jsonify({
            "error": {
                "code": 429,
                "message": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                "request_id": g.request_id,
                "retry_after": retry_after,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }), 429)
        resp.headers["Retry-After"] = str(retry_after)
        resp.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        resp.headers["X-RateLimit-Remaining"] = "0"
        resp.headers["X-RateLimit-Reset"] = str(int(bucket["reset_at"]))
        return resp


@app.after_request
def after_request_handler(response):
    """
    Middleware chạy SAU mỗi request:
    - Thêm Rate Limit headers vào mọi response
    - Thêm Request ID header
    """
    client_ip = request.remote_addr
    bucket = rate_limit_store.get(client_ip, {"count": 0, "reset_at": 0})
    remaining = max(0, RATE_LIMIT - bucket["count"])

    response.headers["X-Request-ID"] = g.get("request_id", "unknown")
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(bucket.get("reset_at", 0)))

    return response


# ============================================================================
# CACHE HELPERS
# ============================================================================

def cacheable_response(data, status_code=200, max_age=60, **kwargs):
    """
    Response với Cache-Control + ETag cho GET requests.

    Cache-Control: max-age=60
      → Client cache response trong 60 giây
      → Trong 60s tiếp theo, client dùng cache mà không gọi server

    ETag: "abc123"
      → Fingerprint của data
      → Client gửi If-None-Match: "abc123" trong request tiếp
      → Nếu data không đổi → server trả 304 Not Modified (không body)
      → Tiết kiệm bandwidth
    """
    response_data = {"data": data}
    if "pagination" in kwargs:
        response_data["pagination"] = kwargs["pagination"]
    if "links" in kwargs:
        response_data["_links"] = kwargs["links"]

    etag = generate_etag(response_data)

    # Check If-None-Match → 304 Not Modified
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match == etag:
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = f"public, max-age={max_age}"
        return resp

    resp = make_response(jsonify(response_data), status_code)
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = f"public, max-age={max_age}"
    resp.headers["Vary"] = "Authorization, Accept"  # Cache khác nhau theo user
    return resp


def no_cache_response(data, status_code=200):
    """
    Response KHÔNG được cache — dùng cho POST/PUT/PATCH/DELETE.
    Cache-Control: no-store → Client không được lưu response.
    """
    resp = make_response(jsonify({"data": data}), status_code)
    resp.headers["Cache-Control"] = "no-store"
    return resp


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    """POST /api/v1/auth/login — Đăng nhập, nhận JWT token"""
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return error_response(400, "Email and password are required")

    user = next((u for u in users_db
                 if u["email"] == data["email"] and u["password"] == data["password"]), None)
    if not user:
        return error_response(401, "Invalid email or password")

    token = generate_token(user)

    return no_cache_response({
        "token": token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "user": {"id": user["id"], "name": user["name"],
                 "email": user["email"], "role": user["role"]},
        "_links": {"profile": f"/api/v1/users/{user['id']}", "users": "/api/v1/users"}
    })


@app.route("/api/v1/auth/me", methods=["GET"])
@require_auth
def get_me():
    """GET /api/v1/auth/me — Profile từ token (cache 30s)"""
    user = next((u for u in users_db if u["id"] == g.current_user["user_id"]), None)
    if not user:
        return error_response(404, "User not found")
    return cacheable_response(user_with_links(user), max_age=30)


# ============================================================================
# USER ENDPOINTS (Cacheable)
# ============================================================================

@app.route("/api/v1/users", methods=["GET"])
@require_auth
def get_users():
    """
    GET /api/v1/users?page=1&limit=2&role=admin

    CACHEABLE:
      - Cache-Control: max-age=60 → cache 1 phút
      - ETag: hash data → 304 nếu không đổi
      - Vary: Authorization → cache riêng cho từng user
    """
    filtered = users_db
    role = request.args.get("role")
    if role:
        filtered = [u for u in filtered if u["role"] == role]

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    limit = min(limit, 100)

    total = len(filtered)
    total_pages = max(1, (total + limit - 1) // limit)
    start = (page - 1) * limit
    paginated = filtered[start:start + limit]

    pagination_links = {
        "self": f"/api/v1/users?page={page}&limit={limit}",
        "first": f"/api/v1/users?page=1&limit={limit}",
        "last": f"/api/v1/users?page={total_pages}&limit={limit}",
    }
    if page > 1:
        pagination_links["prev"] = f"/api/v1/users?page={page-1}&limit={limit}"
    if page < total_pages:
        pagination_links["next"] = f"/api/v1/users?page={page+1}&limit={limit}"

    return cacheable_response(
        data=[user_with_links(u) for u in paginated],
        max_age=60,
        pagination={"current_page": page, "total_pages": total_pages,
                    "total_items": total, "limit": limit},
        links=pagination_links
    )


@app.route("/api/v1/users/<int:user_id>", methods=["GET"])
@require_auth
def get_user(user_id):
    """GET /api/v1/users/1 — Cacheable 60s, ETag support"""
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"User with id {user_id} not found")
    return cacheable_response(user_with_links(user), max_age=60)


@app.route("/api/v1/users", methods=["POST"])
@require_auth
@require_admin
def create_user():
    """POST /api/v1/users — KHÔNG cache (no-store)"""
    global next_id
    data = request.get_json()

    if not data:
        return error_response(400, "Request body is required")

    errors = []
    if not data.get("name"):
        errors.append({"field": "name", "message": "Name is required"})
    if not data.get("email"):
        errors.append({"field": "email", "message": "Email is required"})
    elif "@" not in data["email"]:
        errors.append({"field": "email", "message": "Invalid email format"})
    if errors:
        return error_response(422, "Validation failed", details=errors)

    if any(u["email"] == data["email"] for u in users_db):
        return error_response(409, f"Email {data['email']} already exists")

    new_user = {
        "id": next_id,
        "name": data["name"],
        "email": data["email"],
        "role": data.get("role", "user"),
        "password": data.get("password", "default123"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    next_id += 1
    users_db.append(new_user)

    resp = no_cache_response(user_with_links(new_user), status_code=201)
    resp.headers["Location"] = f"/api/v1/users/{new_user['id']}"
    return resp


@app.route("/api/v1/users/<int:user_id>", methods=["PATCH"])
@require_auth
def patch_user(user_id):
    """PATCH /api/v1/users/1 — Partial update, KHÔNG cache"""
    if g.current_user["role"] != "admin" and g.current_user["user_id"] != user_id:
        return error_response(403, "You can only update your own profile")

    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"User with id {user_id} not found")

    data = request.get_json()
    if not data:
        return error_response(400, "Request body is required")

    if "email" in data and "@" not in data["email"]:
        return error_response(422, "Validation failed",
                              details=[{"field": "email", "message": "Invalid email format"}])

    allowed_fields = ["name", "email"]
    if g.current_user["role"] == "admin":
        allowed_fields.append("role")

    for key in allowed_fields:
        if key in data:
            user[key] = data[key]

    user["updated_at"] = datetime.now(timezone.utc).isoformat()
    return no_cache_response(user_with_links(user))


@app.route("/api/v1/users/<int:user_id>", methods=["PUT"])
@require_auth
@require_admin
def put_user(user_id):
    """PUT /api/v1/users/1 — Full replacement, KHÔNG cache"""
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"User with id {user_id} not found")

    data = request.get_json()
    if not data:
        return error_response(400, "Request body is required")

    errors = []
    for field in ["name", "email", "role"]:
        if not data.get(field):
            errors.append({"field": field, "message": f"{field} is required"})
    if errors:
        return error_response(422, "PUT requires all fields", details=errors)

    user["name"] = data["name"]
    user["email"] = data["email"]
    user["role"] = data["role"]
    user["updated_at"] = datetime.now(timezone.utc).isoformat()

    return no_cache_response(user_with_links(user))


@app.route("/api/v1/users/<int:user_id>", methods=["DELETE"])
@require_auth
@require_admin
def delete_user(user_id):
    """DELETE /api/v1/users/1 — Không trả body"""
    global users_db
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"User with id {user_id} not found")

    users_db = [u for u in users_db if u["id"] != user_id]

    resp = make_response("", 204)
    resp.headers["Cache-Control"] = "no-store"
    return resp


# ============================================================================
# ERROR DEMO
# ============================================================================

@app.route("/api/v1/error-demo/<int:code>", methods=["GET"])
def error_demo(code):
    """Demo mã lỗi HTTP — không cần auth"""
    error_map = {
        400: "Bad Request — sai cú pháp, thiếu tham số",
        401: "Unauthorized — chưa xác thực (thiếu/sai token)",
        403: "Forbidden — đã xác thực nhưng không đủ quyền",
        404: "Not Found — resource không tồn tại",
        405: "Method Not Allowed — method không hỗ trợ",
        409: "Conflict — xung đột dữ liệu (email trùng)",
        422: "Unprocessable Entity — dữ liệu không hợp lệ",
        429: "Too Many Requests — vượt rate limit",
        500: "Internal Server Error — lỗi server",
        502: "Bad Gateway — upstream server lỗi",
        503: "Service Unavailable — server bảo trì/quá tải",
        504: "Gateway Timeout — upstream timeout",
    }
    if code in error_map:
        return error_response(code, error_map[code])
    return error_response(400, f"Unknown error code: {code}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 65)
    print("V4: FULL REST API — Client-Server + Uniform + Stateless + Cache")
    print("=" * 65)
    print()
    print("Tiến trình tích hợp REST qua 4 version:")
    print("  V1: ✅ Client-Server — Flask API, client/server tách biệt")
    print("  V2: ✅ Uniform Interface — pagination, HATEOAS, error format")
    print("  V3: ✅ Stateless — JWT auth, server không lưu session")
    print("  V4: ✅ Cacheable — ETag, Cache-Control, 304, Rate Limit")
    print()
    print("Tính năng mới ở V4:")
    print("  ✅ Cache-Control: max-age=60 (GET), no-store (POST/PUT/DELETE)")
    print("  ✅ ETag + If-None-Match → 304 Not Modified")
    print("  ✅ Rate Limiting: 30 req/60s → 429 Too Many Requests")
    print("  ✅ X-Request-ID: tracking unique mỗi request")
    print("  ✅ Retry-After header khi bị rate limit")
    print("  ✅ X-RateLimit-* headers")
    print()
    print("Test flow:")
    print("  1. Login:  POST /api/v1/auth/login")
    print('     Body:   {"email":"a@example.com","password":"admin123"}')
    print("  2. Get:    GET /api/v1/users")
    print("     Header: Authorization: Bearer <token>")
    print("  3. Cache:  GET /api/v1/users")
    print('     Header: If-None-Match: "<etag from step 2>"')
    print("     → 304 Not Modified (no body!)")
    print("  4. Spam:   Gọi > 30 lần trong 60s → 429")
    print("=" * 65)

    app.run(debug=True, port=5000)
