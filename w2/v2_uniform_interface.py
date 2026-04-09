"""
Version 2: + Uniform Interface
===============================
Thêm so với V1:
  ✅ Pagination (phân trang)
  ✅ Filtering (lọc theo role)
  ✅ Consistent error format (cấu trúc lỗi thống nhất)
  ✅ HATEOAS links (self-descriptive responses)
  ✅ Proper HTTP status codes
  ✅ PUT vs PATCH rõ ràng

Nguyên tắc Uniform Interface gồm 4 ràng buộc:
  1. Resource Identification → URI: /api/v1/users/1
  2. Resource Manipulation → HTTP Methods: GET, POST, PUT, PATCH, DELETE
  3. Self-descriptive Messages → Content-Type, status codes rõ ràng
  4. HATEOAS → Response chứa links tới các action tiếp theo

Chạy: python v2_uniform_interface.py
"""

from flask import Flask, jsonify, request
from datetime import datetime, timezone

app = Flask(__name__)

# ============================================================================
# DATABASE
# ============================================================================

users_db = [
    {"id": 1, "name": "Nguyễn Văn A", "email": "a@example.com", "role": "admin",
     "created_at": "2026-01-15T08:00:00Z"},
    {"id": 2, "name": "Trần Thị B", "email": "b@example.com", "role": "user",
     "created_at": "2026-02-01T10:30:00Z"},
    {"id": 3, "name": "Lê Văn C", "email": "c@example.com", "role": "user",
     "created_at": "2026-02-15T14:00:00Z"},
    {"id": 4, "name": "Phạm Thị D", "email": "d@example.com", "role": "admin",
     "created_at": "2026-03-01T09:00:00Z"},
    {"id": 5, "name": "Hoàng Văn E", "email": "e@example.com", "role": "user",
     "created_at": "2026-03-10T16:00:00Z"},
]

next_id = 6


# ============================================================================
# HELPER: Chuẩn hóa response format (Uniform Interface)
# ============================================================================

def success_response(data, status_code=200, pagination=None, links=None):
    """Response thành công có cấu trúc thống nhất."""
    response = {"data": data}
    if pagination:
        response["pagination"] = pagination
    if links:
        response["_links"] = links
    return jsonify(response), status_code


def error_response(status_code, message, details=None):
    """Response lỗi có cấu trúc thống nhất — giúp client xử lý dễ dàng."""
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
    """HATEOAS: Tạo links cho các action có thể thực hiện trên user."""
    return {
        "self": f"/api/v1/users/{user_id}",
        "update": f"/api/v1/users/{user_id}",
        "delete": f"/api/v1/users/{user_id}",
        "collection": "/api/v1/users"
    }


def user_with_links(user):
    """Gắn HATEOAS links vào user object."""
    return {**user, "_links": build_user_links(user["id"])}


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.route("/api/v1/users", methods=["GET"])
def get_users():
    """
    Tình huống 1: Lấy danh sách người dùng
    GET /api/v1/users?page=1&limit=2&role=admin

    MỚI ở V2 (Uniform Interface):
      - Pagination: ?page=1&limit=2
      - Filtering: ?role=admin
      - HATEOAS links trong response
      - Consistent response format
    """
    # --- Filtering ---
    filtered = users_db
    role = request.args.get("role")
    if role:
        filtered = [u for u in filtered if u["role"] == role]

    # --- Pagination ---
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    limit = min(limit, 100)  # Giới hạn tối đa 100

    total = len(filtered)
    total_pages = max(1, (total + limit - 1) // limit)
    start = (page - 1) * limit
    end = start + limit
    paginated = filtered[start:end]

    # --- HATEOAS links cho pagination ---
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
        pagination={
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total,
            "limit": limit
        },
        links=pagination_links
    )


@app.route("/api/v1/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    GET /api/v1/users/1
    
    MỚI: HATEOAS links cho biết client có thể update/delete user này
    """
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"User with id {user_id} not found")

    return success_response(user_with_links(user))


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    """
    POST /api/v1/users
    Body: {"name": "...", "email": "..."}

    MỚI: Validate kỹ hơn, trả 201 + Location header + HATEOAS links
    """
    global next_id
    data = request.get_json()

    # Validation chi tiết (Uniform Interface: self-descriptive errors)
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

    # Check email trùng → 409 Conflict
    if any(u["email"] == data["email"] for u in users_db):
        return error_response(409, f"Email {data['email']} already exists")

    new_user = {
        "id": next_id,
        "name": data["name"],
        "email": data["email"],
        "role": data.get("role", "user"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    next_id += 1
    users_db.append(new_user)

    response = success_response(user_with_links(new_user), status_code=201)
    # Thêm Location header (chuẩn REST cho 201)
    response[0].headers["Location"] = f"/api/v1/users/{new_user['id']}"
    return response


@app.route("/api/v1/users/<int:user_id>", methods=["PATCH"])
def patch_user(user_id):
    """
    Tình huống 2: Cập nhật MỘT PHẦN (partial update)
    PATCH /api/v1/users/1
    Body: {"email": "new@example.com"}

    → Chỉ cập nhật fields có trong request body
    → Các fields khác giữ nguyên
    """
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"User with id {user_id} not found")

    data = request.get_json()
    if not data:
        return error_response(400, "Request body is required")

    # Validate email nếu có
    if "email" in data and "@" not in data["email"]:
        return error_response(422, "Validation failed",
                              details=[{"field": "email", "message": "Invalid email format"}])

    # Partial update: chỉ cập nhật field được gửi
    allowed_fields = ["name", "email", "role"]
    for key in allowed_fields:
        if key in data:
            user[key] = data[key]

    user["updated_at"] = datetime.now(timezone.utc).isoformat()
    return success_response(user_with_links(user))


@app.route("/api/v1/users/<int:user_id>", methods=["PUT"])
def put_user(user_id):
    """
    Tình huống 5: Thay thế TOÀN BỘ resource (full replacement)
    PUT /api/v1/users/1
    Body: {"name": "...", "email": "...", "role": "..."}

    → PHẢI gửi đầy đủ tất cả fields
    → Thiếu field nào → lỗi 422
    → Khác PATCH: PATCH chỉ cần gửi field muốn sửa
    """
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"User with id {user_id} not found")

    data = request.get_json()
    if not data:
        return error_response(400, "Request body is required")

    # PUT yêu cầu ĐẦY ĐỦ fields
    errors = []
    if not data.get("name"):
        errors.append({"field": "name", "message": "Name is required for full replacement"})
    if not data.get("email"):
        errors.append({"field": "email", "message": "Email is required for full replacement"})
    if not data.get("role"):
        errors.append({"field": "role", "message": "Role is required for full replacement"})
    if errors:
        return error_response(422, "PUT requires all fields", details=errors)

    # Full replacement
    user["name"] = data["name"]
    user["email"] = data["email"]
    user["role"] = data["role"]
    user["updated_at"] = datetime.now(timezone.utc).isoformat()

    return success_response(user_with_links(user))


@app.route("/api/v1/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Tình huống 4: Xóa resource
    DELETE /api/v1/users/1
    → 204 No Content
    """
    global users_db
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"User with id {user_id} not found")

    users_db = [u for u in users_db if u["id"] != user_id]
    return "", 204


# ============================================================================
# ERROR DEMO — Phân tích mã lỗi HTTP
# ============================================================================

@app.route("/api/v1/error-demo/<int:code>", methods=["GET"])
def error_demo(code):
    """Demo mã lỗi với format thống nhất."""
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
    print("=" * 60)
    print("V2: + UNIFORM INTERFACE")
    print("=" * 60)
    print()
    print("Thêm so với V1:")
    print("  ✅ Pagination:  GET /api/v1/users?page=1&limit=2")
    print("  ✅ Filtering:   GET /api/v1/users?role=admin")
    print("  ✅ HATEOAS:     Response chứa _links")
    print("  ✅ Error format: Cấu trúc lỗi thống nhất")
    print("  ✅ PUT vs PATCH: PUT cần đủ fields, PATCH chỉ cần 1")
    print("  ✅ 201 + Location header khi POST")
    print("  ✅ 409 Conflict khi email trùng")
    print("  ✅ 422 khi validation fail")
    print()
    print("Hạn chế:")
    print("  ❌ Chưa Stateless (chưa có authentication)")
    print("  ❌ Chưa Cacheable")
    print("=" * 60)

    app.run(debug=True, port=5000)
