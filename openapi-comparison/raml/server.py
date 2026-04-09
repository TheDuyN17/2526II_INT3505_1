"""
server.py — RAML Doc Server
============================
Đọc file .raml và render thành trang HTML tài liệu API.

Thư viện dùng:
  - Flask         : web server
  - ramlfications : Python RAML parser (tạo bởi Spotify)
  - PyYAML        : fallback đọc RAML (RAML là superset của YAML)

Cài đặt:
    pip install -r requirements.txt

Chạy:
    python server.py

Mở trình duyệt:
    http://localhost:8002/docs
"""

import os
import yaml
from flask import Flask, render_template_string, Response, jsonify, request
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
RAML_FILE = os.path.join(os.path.dirname(__file__), "library_api.raml")

# --- Dữ liệu giả lập ---
books = [
    {"id": 1, "title": "Nhà Giả Kim", "author": "Paulo Coelho", "genre": "fiction", "price": 85000, "available": True},
    {"id": 2, "title": "Đắc Nhân Tâm", "author": "Dale Carnegie", "genre": "non-fiction", "price": 95000, "available": True}
]

members = [
    {"id": 1, "name": "Nguyễn Văn A", "email": "nguyenvana@email.com", "joined_date": "2024-01-01"}
]

# ─── Parse RAML bằng PyYAML (RAML là superset của YAML) ─────────────────────

def parse_raml(filepath: str) -> dict:
    """Đọc file .raml và trả về dict cấu trúc."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    # Bỏ dòng directive đầu tiên (#%RAML 1.0) để PyYAML có thể parse
    lines = raw.split("\n")
    clean_lines = [l for l in lines if not l.startswith("#%RAML")]
    clean_yaml = "\n".join(clean_lines)

    data = yaml.safe_load(clean_yaml) or {}

    # Trích xuất endpoints từ keys bắt đầu bằng /
    endpoints = []
    for key, value in data.items():
        if key.startswith("/") and isinstance(value, dict):
            methods = []
            sub_resources = []

            for method in ["get", "post", "put", "delete", "patch"]:
                if method in value:
                    m_data = value[method] or {}
                    responses = list((m_data.get("responses") or {}).keys())
                    methods.append({
                        "method": method.upper(),
                        "description": m_data.get("description", ""),
                        "responses": responses,
                    })

            # Sub-resources như /{id}
            for sub_key, sub_val in value.items():
                if sub_key.startswith("/") and isinstance(sub_val, dict):
                    sub_methods = []
                    for method in ["get", "post", "put", "delete", "patch"]:
                        if method in sub_val:
                            m_data = sub_val[method] or {}
                            sub_methods.append({
                                "method": method.upper(),
                                "description": m_data.get("description", ""),
                                "responses": list((m_data.get("responses") or {}).keys()),
                            })
                    if sub_methods:
                        sub_resources.append({
                            "path": key + sub_key,
                            "methods": sub_methods,
                        })

            if methods or sub_resources:
                endpoints.append({
                    "path": key,
                    "description": value.get("description", ""),
                    "methods": methods,
                    "sub_resources": sub_resources,
                })

    # Trích types
    types = list((data.get("types") or {}).keys())
    traits = list((data.get("traits") or {}).keys())

    return {
        "title":       data.get("title", "API"),
        "description": data.get("description", ""),
        "version":     data.get("version", ""),
        "base_uri":    data.get("baseUri", ""),
        "media_type":  data.get("mediaType", "application/json"),
        "endpoints":   endpoints,
        "types":       types,
        "traits":      traits,
        "raw":         data,
    }

# ─── HTML Template ────────────────────────────────────────────────────────────

TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{{ api.title }} — RAML Docs</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { margin: 0; font-family: 'Segoe UI', sans-serif; background: #f7f3ff; color: #2d3748; }

    header {
      background: linear-gradient(135deg, #553c9a, #44337a);
      color: #fff; padding: 20px 32px;
      display: flex; align-items: center; justify-content: space-between;
      box-shadow: 0 2px 10px rgba(0,0,0,.3);
    }
    header h1 { margin: 0; font-size: 1.3rem; }
    header h1 span { color: #d6bcfa; }
    .badge {
      background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.3);
      border-radius: 6px; padding: 6px 14px; font-size: .8rem;
    }

    .container { max-width: 960px; margin: 0 auto; padding: 32px 16px; }

    /* Info cards */
    .info-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px; margin-bottom: 32px;
    }
    .info-card {
      background: #fff; border-radius: 10px; padding: 16px 20px;
      box-shadow: 0 1px 4px rgba(0,0,0,.08);
    }
    .info-card .label { font-size: .72rem; text-transform: uppercase; color: #805ad5; margin-bottom: 4px; }
    .info-card .value { font-weight: 600; color: #44337a; word-break: break-all; }

    /* Tags row */
    .tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 28px; }
    .tag {
      padding: 4px 12px; border-radius: 20px; font-size: .8rem; font-weight: 600;
    }
    .tag-type  { background: #e9d8fd; color: #553c9a; }
    .tag-trait { background: #feebc8; color: #c05621; }

    /* Endpoints */
    .endpoint {
      background: #fff; border-radius: 10px; margin-bottom: 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,.08); overflow: hidden;
    }
    .endpoint-header {
      background: #faf5ff; padding: 14px 20px;
      border-bottom: 1px solid #e9d8fd;
      display: flex; align-items: center; gap: 12px;
    }
    .endpoint-path { font-family: monospace; font-weight: 700; color: #553c9a; font-size: 1rem; }
    .endpoint-desc { color: #718096; font-size: .85rem; }

    .method-row {
      padding: 12px 20px; display: flex; align-items: flex-start; gap: 14px;
      border-bottom: 1px solid #f7fafc;
    }
    .method-row:last-child { border-bottom: none; }

    .method {
      padding: 3px 10px; border-radius: 4px; font-size: .75rem;
      font-weight: 700; min-width: 70px; text-align: center; color: #fff;
      flex-shrink: 0;
    }
    .GET    { background: #38a169; }
    .POST   { background: #553c9a; }
    .PUT    { background: #dd6b20; }
    .DELETE { background: #e53e3e; }
    .PATCH  { background: #2b6cb0; }

    .method-info { flex: 1; }
    .method-desc { color: #4a5568; font-size: .88rem; margin-bottom: 6px; }
    .response-codes { display: flex; gap: 6px; flex-wrap: wrap; }
    .rc {
      padding: 2px 8px; border-radius: 4px; font-size: .75rem; font-weight: 600;
    }
    .rc-2 { background: #c6f6d5; color: #276749; }
    .rc-4 { background: #fed7d7; color: #9b2c2c; }
    .rc-5 { background: #feebc8; color: #c05621; }

    /* Sub-resource indent */
    .sub-resource { margin-left: 20px; margin-top: 8px; }
    .sub-resource .endpoint-header { background: #fdf2ff; }
    .sub-resource .endpoint-path { color: #805ad5; }
  </style>
</head>
<body>

<header>
  <div>
    <h1>📚 <span>{{ api.title }}</span></h1>
    <small style="opacity:.7">RAML 1.0 Format · Rendered by Flask + PyYAML</small>
  </div>
  <div class="badge">{{ api.version }} · {{ api.media_type }}</div>
</header>

<div class="container">

  <!-- Info -->
  <div class="info-grid">
    <div class="info-card">
      <div class="label">Base URI</div>
      <div class="value">{{ api.base_uri }}</div>
    </div>
    <div class="info-card">
      <div class="label">Version</div>
      <div class="value">{{ api.version or "—" }}</div>
    </div>
    <div class="info-card">
      <div class="label">Types định nghĩa</div>
      <div class="value">{{ api.types | length }}</div>
    </div>
    <div class="info-card">
      <div class="label">Traits tái sử dụng</div>
      <div class="value">{{ api.traits | length }}</div>
    </div>
  </div>

  <!-- Types & Traits -->
  {% if api.types or api.traits %}
  <div class="tags">
    {% for t in api.types %}
    <span class="tag tag-type">type: {{ t }}</span>
    {% endfor %}
    {% for t in api.traits %}
    <span class="tag tag-trait">trait: {{ t }}</span>
    {% endfor %}
  </div>
  {% endif %}

  <!-- Endpoints -->
  {% for ep in api.endpoints %}
  <div class="endpoint">
    <div class="endpoint-header">
      <span class="endpoint-path">{{ ep.path }}</span>
      {% if ep.description %}<span class="endpoint-desc">— {{ ep.description }}</span>{% endif %}
    </div>
    {% for m in ep.methods %}
    <div class="method-row">
      <span class="method {{ m.method }}">{{ m.method }}</span>
      <div class="method-info">
        {% if m.description %}<div class="method-desc">{{ m.description }}</div>{% endif %}
        <div class="response-codes">
          {% for code in m.responses %}
          <span class="rc {% if code|string|first == '2' %}rc-2{% elif code|string|first == '4' %}rc-4{% else %}rc-5{% endif %}">
            {{ code }}
          </span>
          {% endfor %}
        </div>
      </div>
    </div>
    {% endfor %}

    {% for sub in ep.sub_resources %}
    <div class="sub-resource">
      <div class="endpoint">
        <div class="endpoint-header">
          <span class="endpoint-path">{{ sub.path }}</span>
        </div>
        {% for m in sub.methods %}
        <div class="method-row">
          <span class="method {{ m.method }}">{{ m.method }}</span>
          <div class="method-info">
            {% if m.description %}<div class="method-desc">{{ m.description }}</div>{% endif %}
            <div class="response-codes">
              {% for code in m.responses %}
              <span class="rc {% if code|string|first == '2' %}rc-2{% elif code|string|first == '4' %}rc-4{% else %}rc-5{% endif %}">
                {{ code }}
              </span>
              {% endfor %}
            </div>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
    {% endfor %}
  </div>
  {% endfor %}

</div>
</body>
</html>
"""

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    from flask import redirect
    return redirect("/docs")

@app.route("/docs")
def docs():
    api = parse_raml(RAML_FILE)
    return render_template_string(TEMPLATE, api=api)

@app.route("/raml")
def raw_raml():
    with open(RAML_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    return Response(content, mimetype="text/plain; charset=utf-8")

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
    port = int(os.environ.get("PORT", 8002))
    print(f"\n{'='*50}")
    print(f"  📚  RAML Doc Server")
    print(f"  🌐  http://localhost:{port}/docs")
    print(f"  📄  http://localhost:{port}/raml  (file gốc .raml)")
    print(f"{'='*50}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
