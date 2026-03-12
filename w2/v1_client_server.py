"""
Version 1: Client-Server Architecture
======================================
Nguyên tắc: Tách biệt Client và Server
- Server: Flask API xử lý dữ liệu
- Client: Có thể là bất kỳ app nào gọi API
- Client không biết server lưu trữ thế nào
- Server không biết client hiển thị ra sao

Chạy: python v1_client_server.py
Test: curl http://localhost:5000/api/v1/users
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

# ============================================================================
# SERVER SIDE — Quản lý dữ liệu
# ============================================================================

# Database giả lập (server tự quản lý, client không cần biết)
users_db = [
    {"id": 1, "name": "Nguyễn Văn A", "email": "a@example.com", "role": "admin"},
    {"id": 2, "name": "Trần Thị B", "email": "b@example.com", "role": "user"},
    {"id": 3, "name": "Lê Văn C", "email": "c@example.com", "role": "user"},
    {"id": 4, "name": "Phạm Thị D", "email": "d@example.com", "role": "admin"},
    {"id": 5, "name": "Hoàng Văn E", "email": "e@example.com", "role": "user"},
]

next_id = 6


# --- GET: Lấy danh sách users ---
@app.route("/api/v1/users", methods=["GET"])
def get_users():
    """
    Tình huống 1: Lấy danh sách người dùng
    GET /api/v1/users
    
    → Chỉ đọc dữ liệu, không thay đổi server
    """
    return jsonify({
        "data": users_db,
        "total": len(users_db)
    }), 200


# --- GET: Lấy 1 user theo ID ---
@app.route("/api/v1/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Tình huống 1b: Lấy thông tin 1 người dùng
    GET /api/v1/users/1
    
    → 404 nếu không tìm thấy
    """
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200


# --- POST: Tạo user mới ---
@app.route("/api/v1/users", methods=["POST"])
def create_user():
    """
    Tình huống 3: Tạo resource mới
    POST /api/v1/users
    Body: {"name": "...", "email": "...", "role": "..."}
    
    → Server tự sinh ID, trả về 201 Created
    """
    global next_id
    data = request.get_json()

    if not data or not data.get("name") or not data.get("email"):
        return jsonify({"error": "Missing required fields: name, email"}), 400

    new_user = {
        "id": next_id,
        "name": data["name"],
        "email": data["email"],
        "role": data.get("role", "user")
    }
    next_id += 1
    users_db.append(new_user)

    return jsonify(new_user), 201


# --- PATCH: Cập nhật email ---
@app.route("/api/v1/users/<int:user_id>", methods=["PATCH"])
def update_user(user_id):
    """
    Tình huống 2: Cập nhật một phần thông tin
    PATCH /api/v1/users/1
    Body: {"email": "new@example.com"}
    
    → Chỉ cập nhật field được gửi, không ảnh hưởng field khác
    → Khác PUT: PUT thay thế toàn bộ resource
    """
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Chỉ cập nhật các field có trong request
    for key in ["name", "email", "role"]:
        if key in data:
            user[key] = data[key]

    return jsonify(user), 200


# --- DELETE: Xóa user ---
@app.route("/api/v1/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Tình huống 4: Xóa resource
    DELETE /api/v1/users/1
    
    → 204 No Content nếu xóa thành công
    → 404 nếu không tìm thấy
    """
    global users_db
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    users_db = [u for u in users_db if u["id"] != user_id]
    return "", 204


# ============================================================================
# HTTP ERROR CODES — Phân tích mã lỗi
# ============================================================================

@app.route("/api/v1/error-demo/<int:code>", methods=["GET"])
def error_demo(code):
    """
    Demo các mã lỗi HTTP để phân tích.
    GET /api/v1/error-demo/404
    """
    errors = {
        400: {"error": "Bad Request", "message": "Request sai cú pháp hoặc thiếu tham số"},
        401: {"error": "Unauthorized", "message": "Chưa xác thực - thiếu hoặc sai token"},
        403: {"error": "Forbidden", "message": "Đã xác thực nhưng không có quyền"},
        404: {"error": "Not Found", "message": "Resource không tồn tại"},
        405: {"error": "Method Not Allowed", "message": "HTTP method không được hỗ trợ"},
        409: {"error": "Conflict", "message": "Xung đột dữ liệu (VD: email đã tồn tại)"},
        422: {"error": "Unprocessable Entity", "message": "Cú pháp đúng nhưng dữ liệu không hợp lệ"},
        429: {"error": "Too Many Requests", "message": "Vượt quá giới hạn request"},
        500: {"error": "Internal Server Error", "message": "Lỗi không xác định phía server"},
        502: {"error": "Bad Gateway", "message": "Server trung gian nhận response lỗi"},
        503: {"error": "Service Unavailable", "message": "Server tạm thời không khả dụng"},
        504: {"error": "Gateway Timeout", "message": "Server trung gian timeout"},
    }

    if code in errors:
        return jsonify(errors[code]), code
    return jsonify({"error": f"Unknown error code: {code}"}), 400


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("V1: CLIENT-SERVER ARCHITECTURE")
    print("=" * 60)
    print()
    print("Nguyên tắc: Client và Server tách biệt hoàn toàn")
    print("  - Server quản lý dữ liệu (users_db)")
    print("  - Client gọi API qua HTTP")
    print("  - Hai bên giao tiếp qua JSON")
    print()
    print("Endpoints:")
    print("  GET    /api/v1/users          → Danh sách users")
    print("  GET    /api/v1/users/<id>     → Chi tiết 1 user")
    print("  POST   /api/v1/users          → Tạo user mới")
    print("  PATCH  /api/v1/users/<id>     → Cập nhật email")
    print("  DELETE /api/v1/users/<id>     → Xóa user")
    print("  GET    /api/v1/error-demo/<code> → Demo mã lỗi HTTP")
    print()
    print("Hạn chế ở V1:")
    print("  ❌ Chưa có Uniform Interface (chưa chuẩn REST)")
    print("  ❌ Chưa Stateless (chưa có authentication)")
    print("  ❌ Chưa Cacheable")
    print("=" * 60)

    app.run(debug=True, port=5000)
