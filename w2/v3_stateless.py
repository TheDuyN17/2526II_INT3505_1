"""
Version 3: + Stateless (JWT Authentication)
=============================================
Thêm so với V2:
  ✅ JWT Authentication — mỗi request tự chứa đủ thông tin xác thực
  ✅ Server KHÔNG lưu session — không biết ai đang login
  ✅ Token chứa user_id + role → server decode là biết ngay
  ✅ 401 Unauthorized khi thiếu/sai token
  ✅ 403 Forbidden khi không đủ quyền (role)
  ✅ Middleware auth kiểm tra tự động

Nguyên tắc Stateless:
  - Mỗi request PHẢI chứa đủ thông tin để server xử lý
  - Server KHÔNG lưu trạng thái giữa các request
  - Token JWT chứa: user_id, role, exp → server decode là xong
  - Lợi ích: Dễ scale — bất kỳ server nào cũng xử lý được

Cài đặt: pip install flask pyjwt
Chạy: python v3_stateless.py
"""

from flask import Flask, jsonify, request, g
from datetime import datetime, timezone, timedelta
from functools import wraps
import jwt
import json

app = Flask(__name__)

# Secret key để sign JWT (trong thực tế lưu ở env variable)
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
    # Không trả password về client
    safe_user = {k: v for k, v in user.items() if k != "password"}
    return {**safe_user, "_links": build_user_links(user["id"])}


# ============================================================================
# JWT AUTHENTICATION — Stateless
# ============================================================================

def generate_token(user):
    """
    Tạo JWT token chứa đầy đủ thông tin xác thực.
    
    STATELESS: Token tự chứa mọi thứ server cần:
      - user_id: biết ai đang request
      - role: biết có quyền gì
      - exp: biết token còn hạn không
    → Server KHÔNG cần tra database hay session
    """
    payload = {
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def require_auth(f):
    """
    Middleware: Kiểm tra JWT token trong mỗi request.
    
    STATELESS: Server không nhớ ai đã login.
    Mỗi request phải tự gửi token → server decode → xong.
    Không có token → 401 Unauthorized.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return error_response(401, "Missing Authorization header. Use: Bearer <token>")

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return error_response(401, "Invalid Authorization format. Use: Bearer <token>")

        try:
            payload = jwt.decode(parts[1], SECRET_KEY, algorithms=["HS256"])
            # Lưu user info vào request context (g) — chỉ tồn tại trong request này
            g.current_user = {
                "user_id": payload["user_id"],
                "email": payload["email"],
                "role": payload["role"]
            }
        except jwt.ExpiredSignatureError:
            return error_response(401, "Token has expired. Please login again.")
        except jwt.InvalidTokenError:
            return error_response(401, "Invalid token.")

        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """
    Middleware: Kiểm tra quyền admin.
    Đã xác thực (401 passed) nhưng không phải admin → 403 Forbidden.
    
    SO SÁNH 401 vs 403:
      401: Chưa xác thực (thiếu/sai token) → "Bạn là ai?"
      403: Đã xác thực nhưng không đủ quyền → "Tôi biết bạn, nhưng bạn không có quyền"
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.current_user["role"] != "admin":
            return error_response(403,
                "Admin access required. Your role: " + g.current_user["role"],
                details={
                    "required_role": "admin",
                    "your_role": g.current_user["role"]
                })
        return f(*args, **kwargs)
    return decorated


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    """
    Đăng nhập → nhận JWT token.
    POST /api/v1/auth/login
    Body: {"email": "a@example.com", "password": "admin123"}
    
    → Token được trả về cho client tự lưu
    → Server KHÔNG lưu session (stateless)
    """
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return error_response(400, "Email and password are required")

    user = next((u for u in users_db
                 if u["email"] == data["email"] and u["password"] == data["password"]), None)

    if not user:
        return error_response(401, "Invalid email or password")

    token = generate_token(user)

    return jsonify({
        "data": {
            "token": token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        },
        "_links": {
            "profile": f"/api/v1/users/{user['id']}",
            "users": "/api/v1/users"
        }
    }), 200


@app.route("/api/v1/auth/me", methods=["GET"])
@require_auth
def get_me():
    """
    Xem thông tin user hiện tại từ token.
    GET /api/v1/auth/me
    Authorization: Bearer <token>
    
    STATELESS: Server decode token → biết ngay user là ai, không cần session.
    """
    user = next((u for u in users_db if u["id"] == g.current_user["user_id"]), None)
    if not user:
        return error_response(404, "User not found")
    return success_response(user_with_links(user))


# ============================================================================
# USER ENDPOINTS (giờ có authentication)
# ============================================================================

@app.route("/api/v1/users", methods=["GET"])
@require_auth
def get_users():
    """GET /api/v1/users?page=1&limit=2&role=admin — Cần token"""
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

    return success_response(
        data=[user_with_links(u) for u in paginated],
        pagination={"current_page": page, "total_pages": total_pages,
                    "total_items": total, "limit": limit},
        links=pagination_links
    )


@app.route("/api/v1/users/<int:user_id>", methods=["GET"])
@require_auth
def get_user(user_id):
    """GET /api/v1/users/1 — Cần token"""
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"User with id {user_id} not found")
    return success_response(user_with_links(user))


@app.route("/api/v1/users", methods=["POST"])
@require_auth
@require_admin  # Chỉ admin mới được tạo user → 403 nếu không phải admin
def create_user():
    """POST /api/v1/users — Chỉ admin (token + role=admin)"""
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

    response = success_response(user_with_links(new_user), status_code=201)
    response[0].headers["Location"] = f"/api/v1/users/{new_user['id']}"
    return response


@app.route("/api/v1/users/<int:user_id>", methods=["PATCH"])
@require_auth
def patch_user(user_id):
    """PATCH /api/v1/users/1 — User chỉ sửa được chính mình, admin sửa được tất cả"""
    # Kiểm tra quyền: user thường chỉ sửa chính mình
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

    # User thường không được tự đổi role
    allowed_fields = ["name", "email"]
    if g.current_user["role"] == "admin":
        allowed_fields.append("role")

    for key in allowed_fields:
        if key in data:
            user[key] = data[key]

    user["updated_at"] = datetime.now(timezone.utc).isoformat()
    return success_response(user_with_links(user))


@app.route("/api/v1/users/<int:user_id>", methods=["PUT"])
@require_auth
@require_admin
def put_user(user_id):
    """PUT /api/v1/users/1 — Chỉ admin, cần đầy đủ fields"""
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"User with id {user_id} not found")

    data = request.get_json()
    if not data:
        return error_response(400, "Request body is required")

    errors = []
    for field in ["name", "email", "role"]:
        if not data.get(field):
            errors.append({"field": field, "message": f"{field} is required for full replacement"})
    if errors:
        return error_response(422, "PUT requires all fields", details=errors)

    user["name"] = data["name"]
    user["email"] = data["email"]
    user["role"] = data["role"]
    user["updated_at"] = datetime.now(timezone.utc).isoformat()

    return success_response(user_with_links(user))


@app.route("/api/v1/users/<int:user_id>", methods=["DELETE"])
@require_auth
@require_admin  # Chỉ admin mới được xóa
def delete_user(user_id):
    """DELETE /api/v1/users/1 — Chỉ admin"""
    global users_db
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"User with id {user_id} not found")

    users_db = [u for u in users_db if u["id"] != user_id]
    return "", 204


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("V3: + STATELESS (JWT Authentication)")
    print("=" * 60)
    print()
    print("Thêm so với V2:")
    print("  ✅ JWT Authentication — token tự chứa user info")
    print("  ✅ Stateless — server không lưu session")
    print("  ✅ 401 Unauthorized — thiếu/sai token")
    print("  ✅ 403 Forbidden — không đủ quyền (role)")
    print("  ✅ Admin-only routes: POST, PUT, DELETE users")
    print("  ✅ User chỉ sửa profile của chính mình")
    print()
    print("Test flow:")
    print("  1. POST /api/v1/auth/login")
    print('     Body: {"email":"a@example.com","password":"admin123"}')
    print("  2. Copy token từ response")
    print("  3. GET /api/v1/users")
    print("     Header: Authorization: Bearer <token>")
    print()
    print("Hạn chế:")
    print("  ❌ Chưa Cacheable")
    print("=" * 60)

    app.run(debug=True, port=5000)
