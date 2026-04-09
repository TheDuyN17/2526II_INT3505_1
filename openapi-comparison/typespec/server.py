"""
server.py — TypeSpec Doc Server
=================================
TypeSpec là ngôn ngữ của Microsoft, compiler của nó là Node.js.
Workflow thực tế:
  1. Viết spec bằng TypeSpec (.tsp)
  2. Compile ra OpenAPI YAML bằng `tsp compile`
  3. Serve OpenAPI YAML đó bằng Swagger UI (giống Lecture 4)

Server này hỗ trợ CẢ HAI mode:
  - Nếu đã có file openapi.yaml (đã compile): serve trực tiếp
  - Nếu chưa có: hiển thị hướng dẫn compile + serve file .tsp dưới dạng source

Cài đặt:
    pip install flask flask-swagger-ui

Chạy:
    python server.py

Mở trình duyệt:
    http://localhost:8003/docs
"""

import os
import json
from flask import Flask, send_file, redirect, render_template_string, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# --- Dữ liệu giả lập ---
books = [
    {"id": 1, "title": "Nhà Giả Kim", "author": "Paulo Coelho", "genre": "fiction", "price": 85000, "available": True},
    {"id": 2, "title": "Đắc Nhân Tâm", "author": "Dale Carnegie", "genre": "non-fiction", "price": 95000, "available": True}
]

members = [
    {"id": 1, "name": "Nguyễn Văn A", "email": "nguyenvana@email.com", "joined_date": "2024-01-01"}
]

BASE_DIR       = os.path.dirname(__file__)
TSP_FILE       = os.path.join(BASE_DIR, "library_api.tsp")
OPENAPI_FILE   = os.path.join(BASE_DIR, "tsp-output", "@typespec", "openapi3", "openapi.yaml")
FALLBACK_YAML  = os.path.join(BASE_DIR, "openapi_fallback.yaml")

SWAGGER_URL = "/docs"
API_URL     = "/openapi.yaml"

# ─── Swagger UI blueprint ────────────────────────────────────────────────────

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Library Management API (TypeSpec)"},
)
app.register_blueprint(swaggerui_blueprint)

# ─── Helper ──────────────────────────────────────────────────────────────────

def get_openapi_file() -> str | None:
    """Trả về đường dẫn file OpenAPI nếu tồn tại."""
    if os.path.exists(OPENAPI_FILE):
        return OPENAPI_FILE
    if os.path.exists(FALLBACK_YAML):
        return FALLBACK_YAML
    return None

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect("/docs")

@app.route("/openapi.yaml")
def serve_openapi():
    """Serve file OpenAPI YAML đã được compile từ TypeSpec."""
    yaml_path = get_openapi_file()
    if yaml_path:
        return send_file(yaml_path, mimetype="text/yaml")

    # Chưa compile → trả về thông báo lỗi dạng YAML hợp lệ
    fallback = """openapi: "3.0.0"
info:
  title: "⚠️ Chưa compile TypeSpec"
  version: "0.0.0"
  description: |
    File OpenAPI chưa được tạo.
    Vui lòng chạy lệnh sau để compile:

    ```
    npm install -g @typespec/compiler
    tsp compile library_api.tsp --emit @typespec/openapi3
    ```

    Sau đó restart server này.
paths: {}
"""
    from flask import Response
    return Response(fallback, mimetype="text/yaml")

@app.route("/source")
def view_source():
    """Xem nội dung file TypeSpec gốc."""
    with open(TSP_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    from flask import Response
    return Response(content, mimetype="text/plain; charset=utf-8")

@app.route("/status")
def status():
    """Kiểm tra trạng thái compile."""
    yaml_path = get_openapi_file()
    return jsonify({
        "tsp_file":       os.path.exists(TSP_FILE),
        "openapi_file":   yaml_path is not None,
        "openapi_path":   yaml_path or "not found",
        "compile_command": "tsp compile library_api.tsp --emit @typespec/openapi3",
    })

# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.route("/api/v1/books", methods=["GET"])
def list_books():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    search = request.args.get("search", "").lower()
    
    filtered = [b for b in books if search in str(b["title"]).lower() or search in str(b["author"]).lower()]
    start = (page - 1) * limit
    end = start + limit
    
    return jsonify({
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "data": filtered[start:end]
    }), 200

@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book: return jsonify({"error": "NOT_FOUND", "message": "Không tìm thấy sách"}), 404
    return jsonify({"data": book}), 200

@app.route("/api/v1/books", methods=["POST"])
def create_book():
    data = request.json
    new_id = max([b["id"] for b in books] + [0]) + 1
    new_book = {**data, "id": new_id, "created_at": datetime.datetime.now().isoformat() + "Z"}
    books.append(new_book)
    return jsonify({"data": new_book}), 201

@app.route("/api/v1/members", methods=["GET"])
def list_members():
    return jsonify({"total": len(members), "data": members}), 200

@app.route("/api/v1/members", methods=["POST"])
def create_member():
    data = request.json
    new_id = max([m["id"] for m in members] + [0]) + 1
    new_member = {**data, "id": new_id, "joined_date": datetime.date.today().isoformat()}
    members.append(new_member)
    return jsonify({"data": new_member}), 201

# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8003))
    yaml_path = get_openapi_file()

    print(f"\n{'='*55}")
    print(f"  📚  TypeSpec Doc Server")
    print(f"  🌐  http://localhost:{port}/docs")
    print(f"  📄  http://localhost:{port}/source  (file .tsp gốc)")
    print(f"  🔍  http://localhost:{port}/status  (trạng thái compile)")
    print(f"{'='*55}")

    if yaml_path:
        print(f"  ✅  OpenAPI file found: {yaml_path}")
    else:
        print(f"  ⚠️   OpenAPI chưa được compile!")
        print(f"  👉  Chạy lệnh sau để compile:")
        print(f"      npm install -g @typespec/compiler")
        print(f"      tsp compile library_api.tsp --emit @typespec/openapi3")
    print()

    app.run(host="0.0.0.0", port=port, debug=False)
