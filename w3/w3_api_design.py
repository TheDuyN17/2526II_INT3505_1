"""
Buổi 3: Nguyên tắc Thiết kế API
=================================
Sinh viên: TheDuyN17
Repo: btvn/w3

Kiến thức cần đạt:
- Best practices: consistency, clarity, extensibility
- Naming conventions: plural nouns, lowercase, hyphens, versioning

Kỹ năng cần làm được:
- Áp dụng quy tắc đặt tên endpoint
- Đánh giá chất lượng thiết kế API mẫu

Thực hành:
- Case study: Phát hiện lỗi trong một API poorly designed
- Peer review: Đánh giá thiết kế API của nhóm bạn

Chạy: python w3_api_design.py
"""

import json

# ============================================================================
# PHẦN 1: CASE STUDY — PHÁT HIỆN LỖI TRONG API POORLY DESIGNED
# ============================================================================

# Đây là một API "thật" được thiết kế RẤT TỆ
# Nhiệm vụ: Tìm ra TẤT CẢ các lỗi thiết kế

BAD_API = {
    "tên": "ShopAPI v0 — API Quản lý cửa hàng (POORLY DESIGNED)",
    "base_url": "http://shop-server.com",
    "endpoints": [
        {
            "id": 1,
            "endpoint": "GET /getAllProducts",
            "mô_tả": "Lấy tất cả sản phẩm",
            "lỗi": [
                "❌ Dùng động từ trong URL: 'getAll' → nên dùng danh từ",
                "❌ camelCase → nên dùng lowercase + hyphens hoặc chỉ lowercase",
                "❌ Không có versioning → thiếu /api/v1/",
                "❌ Không có pagination → trả hết data sẽ quá tải",
            ],
            "sửa_lại": "GET /api/v1/products?page=1&limit=20"
        },
        {
            "id": 2,
            "endpoint": "POST /createNewProduct",
            "body": '{"product_Name": "Áo", "Price": 100000, "cat": "fashion"}',
            "mô_tả": "Tạo sản phẩm mới",
            "lỗi": [
                "❌ Dùng động từ 'create' → POST đã ngầm hiểu là tạo mới",
                "❌ camelCase trong URL",
                "❌ Body fields không nhất quán: product_Name (PascalCase), Price (PascalCase), cat (viết tắt)",
                "❌ Nên dùng snake_case hoặc camelCase thống nhất cho body fields",
                "❌ 'cat' → không rõ nghĩa, nên viết đầy đủ: 'category'",
                "❌ Không có versioning",
            ],
            "sửa_lại": "POST /api/v1/products",
            "body_sửa": '{"name": "Áo", "price": 100000, "category": "fashion"}'
        },
        {
            "id": 3,
            "endpoint": "GET /product/info?id=5",
            "mô_tả": "Lấy thông tin 1 sản phẩm",
            "lỗi": [
                "❌ Dùng số ít 'product' → nên dùng số nhiều 'products' (nhất quán)",
                "❌ Dùng query param cho ID → nên dùng path param: /products/5",
                "❌ '/info' thừa → GET đã ngầm hiểu là lấy info",
                "❌ Không nhất quán với endpoint 1: 'getAllProducts' vs 'product/info'",
            ],
            "sửa_lại": "GET /api/v1/products/5"
        },
        {
            "id": 4,
            "endpoint": "POST /updateProduct/5",
            "body": '{"Price": 150000}',
            "mô_tả": "Cập nhật giá sản phẩm",
            "lỗi": [
                "❌ Dùng POST để update → nên dùng PATCH (partial) hoặc PUT (full)",
                "❌ Dùng động từ 'update' trong URL",
                "❌ 'Price' viết hoa → không nhất quán",
                "❌ Không rõ partial hay full update",
            ],
            "sửa_lại": "PATCH /api/v1/products/5",
            "body_sửa": '{"price": 150000}'
        },
        {
            "id": 5,
            "endpoint": "GET /deleteProduct?id=5",
            "mô_tả": "Xóa sản phẩm",
            "lỗi": [
                "❌ Dùng GET để xóa → CỰC KỲ NGUY HIỂM (crawler có thể xóa hết data!)",
                "❌ GET phải idempotent và safe, không được thay đổi state",
                "❌ Dùng động từ 'delete' trong URL",
                "❌ Dùng query param cho ID",
                "❌ Nên dùng DELETE method",
            ],
            "sửa_lại": "DELETE /api/v1/products/5"
        },
        {
            "id": 6,
            "endpoint": "GET /getOrdersByUser?userId=10&startDate=2026-01-01&endDate=2026-03-01",
            "mô_tả": "Lấy đơn hàng của user theo khoảng thời gian",
            "lỗi": [
                "❌ Dùng động từ 'get' → thừa vì đã dùng GET method",
                "❌ camelCase: 'ByUser', 'userId', 'startDate', 'endDate'",
                "❌ Không dùng nested resource → nên: /users/10/orders",
                "❌ Query params nên dùng snake_case hoặc kebab-case",
            ],
            "sửa_lại": "GET /api/v1/users/10/orders?start_date=2026-01-01&end_date=2026-03-01"
        },
        {
            "id": 7,
            "endpoint": "POST /api/order/add-to-cart",
            "body": '{"prod_id": 5, "qty": 2}',
            "mô_tả": "Thêm sản phẩm vào giỏ hàng",
            "lỗi": [
                "❌ Số ít 'order' → nên 'orders' hoặc tách riêng resource 'cart'",
                "❌ 'add-to-cart' là hành động → RESTful dùng danh từ, method thể hiện hành động",
                "❌ 'prod_id' viết tắt → 'product_id'",
                "❌ 'qty' viết tắt → 'quantity'",
                "❌ Thiếu versioning /v1/",
            ],
            "sửa_lại": "POST /api/v1/cart/items",
            "body_sửa": '{"product_id": 5, "quantity": 2}'
        },
        {
            "id": 8,
            "endpoint": "GET /api/v1/Products/5/Reviews",
            "mô_tả": "Lấy reviews của sản phẩm",
            "lỗi": [
                "❌ PascalCase: 'Products', 'Reviews' → URL phải lowercase",
                "❌ Có versioning nhưng inconsistent với các endpoint khác (endpoint khác không có)",
            ],
            "sửa_lại": "GET /api/v1/products/5/reviews"
        },
        {
            "id": 9,
            "endpoint": "POST /api/v2/products",
            "response_lỗi": '''{
  "code": -1,
  "msg": "err",
  "data": null
}''',
            "mô_tả": "Tạo sản phẩm thất bại (response format)",
            "lỗi": [
                "❌ Error code '-1' → không ai hiểu, nên dùng HTTP status codes (400, 422...)",
                "❌ 'msg: err' → không mô tả lỗi gì, client không biết sửa thế nào",
                "❌ Trả HTTP 200 cho lỗi → nên trả đúng status code (400/422)",
                "❌ Nhảy từ v1 sang v2 không rõ lý do, thiếu backward compatibility",
            ],
            "sửa_lại_response": '''{
  "error": {
    "code": 422,
    "message": "Validation failed",
    "details": [
      {"field": "name", "message": "Name is required"},
      {"field": "price", "message": "Price must be positive"}
    ]
  }
}'''
        },
        {
            "id": 10,
            "endpoint": "GET /api/v1/search-products-by-category-and-price-range",
            "mô_tả": "Tìm sản phẩm theo category và giá",
            "lỗi": [
                "❌ URL quá dài, nhồi nhét hành động vào path",
                "❌ Nên dùng query params cho bộ lọc",
                "❌ Resource chính là 'products', filter bằng params",
            ],
            "sửa_lại": "GET /api/v1/products?category=fashion&min_price=100000&max_price=500000"
        }
    ]
}


def case_study_bad_api():
    """Phần 1: Phân tích API poorly designed."""
    print("=" * 70)
    print("CASE STUDY: PHÁT HIỆN LỖI TRONG API POORLY DESIGNED")
    print("=" * 70)
    print(f"\nAPI: {BAD_API['tên']}")
    print(f"Base URL: {BAD_API['base_url']}")

    total_errors = 0

    for ep in BAD_API["endpoints"]:
        print(f"\n{'─' * 65}")
        print(f"  #{ep['id']} {ep['mô_tả']}")
        print(f"  ❌ SAI:  {ep['endpoint']}")
        if "body" in ep:
            print(f"     Body: {ep['body']}")
        if "response_lỗi" in ep:
            print(f"     Response: {ep['response_lỗi']}")

        print(f"\n  Các lỗi phát hiện:")
        for lỗi in ep["lỗi"]:
            print(f"    {lỗi}")
            total_errors += 1

        print(f"\n  ✅ SỬA:  {ep['sửa_lại']}")
        if "body_sửa" in ep:
            print(f"     Body: {ep['body_sửa']}")
        if "sửa_lại_response" in ep:
            print(f"     Response: {ep['sửa_lại_response']}")

    print(f"\n{'=' * 70}")
    print(f"TỔNG KẾT: Phát hiện {total_errors} lỗi thiết kế trong 10 endpoints")
    print(f"{'=' * 70}")


# ============================================================================
# PHẦN 2: BẢNG QUY TẮC THIẾT KẾ API (BEST PRACTICES)
# ============================================================================

API_DESIGN_RULES = {
    "1. Naming Conventions": {
        "rules": [
            "Dùng danh từ SỐ NHIỀU: /users, /products, /orders (không phải /user, /product)",
            "Dùng LOWERCASE: /products (không phải /Products)",
            "Dùng HYPHENS cho multi-word: /order-items (không phải /orderItems hay /order_items)",
            "KHÔNG dùng động từ: /users (không phải /getUsers, /createUser)",
            "Viết tắt phải rõ nghĩa: tránh /prod, /cat, /qty → dùng /products, /categories, quantity",
        ],
        "ví_dụ_đúng": [
            "GET    /api/v1/users",
            "POST   /api/v1/users",
            "GET    /api/v1/users/42",
            "GET    /api/v1/users/42/orders",
            "GET    /api/v1/order-items",
        ],
        "ví_dụ_sai": [
            "GET    /api/v1/getUsers         ← động từ 'get' thừa",
            "POST   /api/v1/createUser       ← động từ 'create' thừa",
            "GET    /api/v1/User/42          ← số ít + PascalCase",
            "GET    /api/v1/user_orders/42   ← snake_case trong URL",
            "DELETE /api/v1/removeProduct/5  ← động từ 'remove' thừa",
        ]
    },
    "2. Versioning": {
        "rules": [
            "Luôn có version trong URL: /api/v1/, /api/v2/",
            "Giúp backward compatibility khi API thay đổi",
            "Client cũ dùng v1, client mới dùng v2 → không ai bị break",
        ],
        "ví_dụ_đúng": [
            "GET /api/v1/users",
            "GET /api/v2/users  ← version mới, có thể response format khác",
        ],
        "ví_dụ_sai": [
            "GET /users          ← không có version",
            "GET /api/users      ← thiếu version number",
        ]
    },
    "3. HTTP Methods (Consistency)": {
        "rules": [
            "GET    → Đọc (không thay đổi data)",
            "POST   → Tạo mới",
            "PUT    → Thay thế toàn bộ (cần đủ fields)",
            "PATCH  → Cập nhật một phần (chỉ cần fields muốn sửa)",
            "DELETE → Xóa",
            "KHÔNG BAO GIỜ dùng GET để xóa/sửa data!",
        ],
        "ví_dụ_đúng": [
            "DELETE /api/v1/users/5     ← xóa user",
            "PATCH  /api/v1/users/5     ← sửa email",
        ],
        "ví_dụ_sai": [
            "GET    /deleteUser?id=5    ← GET để xóa = NGUY HIỂM",
            "POST   /updateUser/5       ← POST để update = sai method",
        ]
    },
    "4. Response Format (Clarity)": {
        "rules": [
            "Dùng đúng HTTP status codes (200, 201, 400, 404, 500...)",
            "Error response phải có message rõ ràng, chỉ rõ field nào sai",
            "Cấu trúc response nhất quán cho mọi endpoint",
            "Không trả HTTP 200 cho lỗi rồi đặt error code trong body",
        ],
        "ví_dụ_đúng": [
            '200 OK → {"data": {...}}',
            '201 Created → {"data": {...}} + Location header',
            '400 Bad Request → {"error": {"code": 400, "message": "Missing name"}}',
            '404 Not Found → {"error": {"code": 404, "message": "User 99 not found"}}',
        ],
        "ví_dụ_sai": [
            '200 OK → {"code": -1, "msg": "err"}  ← HTTP 200 nhưng thực ra lỗi',
            '500 → "Something went wrong"          ← không đủ thông tin debug',
        ]
    },
    "5. Query Parameters (Extensibility)": {
        "rules": [
            "Dùng query params cho filtering, sorting, pagination",
            "Dễ mở rộng: thêm filter mới không cần thay đổi URL structure",
            "Tên param dùng snake_case: ?start_date=, ?min_price=",
        ],
        "ví_dụ_đúng": [
            "GET /api/v1/products?category=fashion&sort=price&order=asc",
            "GET /api/v1/products?min_price=100000&max_price=500000",
            "GET /api/v1/products?page=2&limit=20",
        ],
        "ví_dụ_sai": [
            "GET /api/v1/search-products-by-category-and-price  ← nhồi vào URL",
            "GET /api/v1/products/fashion/cheap                 ← filter trong path",
        ]
    },
    "6. Nested Resources": {
        "rules": [
            "Thể hiện quan hệ parent-child qua URL",
            "Tối đa 2-3 cấp, không quá sâu",
            "Resource con phụ thuộc resource cha",
        ],
        "ví_dụ_đúng": [
            "GET /api/v1/users/42/orders           ← orders của user 42",
            "GET /api/v1/products/5/reviews         ← reviews của product 5",
            "POST /api/v1/orders/100/items          ← thêm item vào order 100",
        ],
        "ví_dụ_sai": [
            "GET /api/v1/users/42/orders/100/items/5/details  ← quá sâu (4 cấp)",
            "GET /api/v1/getOrdersByUser?userId=42             ← không dùng nested",
        ]
    }
}


def print_design_rules():
    """In ra bảng quy tắc thiết kế API."""
    print("\n\n" + "=" * 70)
    print("BẢNG QUY TẮC THIẾT KẾ API — BEST PRACTICES")
    print("=" * 70)

    for rule_name, details in API_DESIGN_RULES.items():
        print(f"\n{'─' * 65}")
        print(f"📌 {rule_name}")
        print()
        for rule in details["rules"]:
            print(f"    • {rule}")

        print(f"\n    ✅ Đúng:")
        for ex in details["ví_dụ_đúng"]:
            print(f"       {ex}")

        print(f"\n    ❌ Sai:")
        for ex in details["ví_dụ_sai"]:
            print(f"       {ex}")


# ============================================================================
# PHẦN 3: PEER REVIEW — ĐÁNH GIÁ THIẾT KẾ API CỦA NHÓM BẠN
# ============================================================================

# Giả lập 2 API của "nhóm bạn" để peer review

TEAM_APIS = [
    {
        "team": "Nhóm A — API Quản lý Thư viện",
        "endpoints": [
            {"endpoint": "GET /api/v1/books", "đánh_giá": "✅", "nhận_xét": "Đúng chuẩn: danh từ số nhiều, có versioning"},
            {"endpoint": "GET /api/v1/books/15", "đánh_giá": "✅", "nhận_xét": "Path param cho ID — chính xác"},
            {"endpoint": "POST /api/v1/books", "đánh_giá": "✅", "nhận_xét": "POST để tạo mới — đúng"},
            {"endpoint": "PUT /api/v1/books/15", "đánh_giá": "⚠️", "nhận_xét": "PUT nhưng body chỉ có 1 field → nên dùng PATCH cho partial update"},
            {"endpoint": "GET /api/v1/books/15/borrowHistory", "đánh_giá": "⚠️", "nhận_xét": "camelCase 'borrowHistory' → nên là 'borrow-history' hoặc tách resource: /books/15/borrows"},
            {"endpoint": "POST /api/v1/borrowBook", "đánh_giá": "❌", "nhận_xét": "Động từ 'borrow' trong URL + số ít 'Book' → nên: POST /api/v1/borrows hoặc POST /api/v1/books/15/borrows"},
            {"endpoint": "DELETE /api/v1/books/15", "đánh_giá": "✅", "nhận_xét": "DELETE đúng chuẩn"},
        ],
        "điểm_tổng": "5/7 endpoints đạt chuẩn",
        "góp_ý_chung": [
            "Nhìn chung API thiết kế khá tốt, có versioning từ đầu",
            "Cần thống nhất naming: tránh camelCase trong URL",
            "Nên tách 'borrow' thành resource riêng thay vì dùng động từ",
            "Thiếu pagination cho GET /books",
        ]
    },
    {
        "team": "Nhóm B — API Quản lý Nhà hàng",
        "endpoints": [
            {"endpoint": "GET /menu/getAll", "đánh_giá": "❌", "nhận_xét": "Thiếu versioning, động từ 'getAll' thừa, số ít 'menu'"},
            {"endpoint": "POST /menu/addItem", "đánh_giá": "❌", "nhận_xét": "Động từ 'add' thừa, số ít, thiếu version → POST /api/v1/menu-items"},
            {"endpoint": "GET /api/v1/tables", "đánh_giá": "✅", "nhận_xét": "Đúng chuẩn"},
            {"endpoint": "POST /api/v1/reservations", "đánh_giá": "✅", "nhận_xét": "Đúng chuẩn, resource rõ ràng"},
            {"endpoint": "GET /getOrderByTable?table=5", "đánh_giá": "❌", "nhận_xét": "Động từ, thiếu version, dùng query cho table → GET /api/v1/tables/5/orders"},
            {"endpoint": "POST /api/v1/orders", "đánh_giá": "✅", "nhận_xét": "Đúng chuẩn"},
            {"endpoint": "PATCH /api/v1/orders/20", "đánh_giá": "✅", "nhận_xét": "PATCH cho partial update — tốt"},
        ],
        "điểm_tổng": "4/7 endpoints đạt chuẩn",
        "góp_ý_chung": [
            "Có sự không nhất quán: một số endpoint có versioning, một số không",
            "Các endpoint về menu cần refactor lại hoàn toàn",
            "Phần orders và reservations thiết kế tốt — nên áp dụng style này cho menu",
            "Nên thống nhất convention trước khi code: tránh mix style",
        ]
    }
]


def peer_review():
    """Phần 3: Peer review API của nhóm bạn."""
    print("\n\n" + "=" * 70)
    print("PEER REVIEW: ĐÁNH GIÁ THIẾT KẾ API CỦA NHÓM BẠN")
    print("=" * 70)

    for team in TEAM_APIS:
        print(f"\n{'━' * 65}")
        print(f"📋 {team['team']}")
        print(f"{'━' * 65}")

        print(f"\n  {'Đánh giá':<10} {'Endpoint':<45} ")
        print(f"  {'─'*9} {'─'*44}")

        for ep in team["endpoints"]:
            print(f"  {ep['đánh_giá']:<10} {ep['endpoint']:<45}")
            print(f"  {'':10} → {ep['nhận_xét']}")

        print(f"\n  📊 Kết quả: {team['điểm_tổng']}")
        print(f"\n  💬 Góp ý chung:")
        for gop_y in team["góp_ý_chung"]:
            print(f"     • {gop_y}")


# ============================================================================
# PHẦN 4: CHECKLIST ĐÁNH GIÁ API (có thể tái sử dụng)
# ============================================================================

REVIEW_CHECKLIST = [
    {"tiêu_chí": "Versioning", "câu_hỏi": "API có version trong URL? (/api/v1/)", "trọng_số": "Cao"},
    {"tiêu_chí": "Plural nouns", "câu_hỏi": "Resource dùng danh từ số nhiều? (/users, /products)", "trọng_số": "Cao"},
    {"tiêu_chí": "Lowercase URL", "câu_hỏi": "URL toàn bộ lowercase?", "trọng_số": "Cao"},
    {"tiêu_chí": "No verbs in URL", "câu_hỏi": "Không có động từ trong URL path?", "trọng_số": "Cao"},
    {"tiêu_chí": "Correct HTTP methods", "câu_hỏi": "Dùng đúng GET/POST/PUT/PATCH/DELETE?", "trọng_số": "Cao"},
    {"tiêu_chí": "Proper status codes", "câu_hỏi": "Trả đúng HTTP status code (200, 201, 400, 404...)?", "trọng_số": "Cao"},
    {"tiêu_chí": "Consistent naming", "câu_hỏi": "Body fields dùng cùng 1 convention (snake_case)?", "trọng_số": "Trung bình"},
    {"tiêu_chí": "Pagination", "câu_hỏi": "GET danh sách có hỗ trợ pagination?", "trọng_số": "Trung bình"},
    {"tiêu_chí": "Filtering via params", "câu_hỏi": "Filter/sort qua query params (không nhồi vào URL)?", "trọng_số": "Trung bình"},
    {"tiêu_chí": "Nested resources", "câu_hỏi": "Quan hệ parent-child thể hiện qua URL? (max 2-3 cấp)", "trọng_số": "Trung bình"},
    {"tiêu_chí": "Error format", "câu_hỏi": "Error response có message rõ ràng, format nhất quán?", "trọng_số": "Trung bình"},
    {"tiêu_chí": "No abbreviations", "câu_hỏi": "Không viết tắt khó hiểu? (prod → product, qty → quantity)", "trọng_số": "Thấp"},
    {"tiêu_chí": "HATEOAS links", "câu_hỏi": "Response có _links cho navigation?", "trọng_số": "Thấp"},
    {"tiêu_chí": "Extensibility", "câu_hỏi": "Dễ thêm tính năng mới mà không break client cũ?", "trọng_số": "Trung bình"},
]


def print_review_checklist():
    """In checklist đánh giá API."""
    print("\n\n" + "=" * 70)
    print("CHECKLIST ĐÁNH GIÁ CHẤT LƯỢNG API")
    print("(Dùng để peer review bất kỳ API nào)")
    print("=" * 70)

    print(f"\n  {'#':<4} {'Tiêu chí':<25} {'Trọng số':<12} {'Câu hỏi kiểm tra'}")
    print(f"  {'─'*3} {'─'*24} {'─'*11} {'─'*40}")

    for i, item in enumerate(REVIEW_CHECKLIST, 1):
        print(f"  {i:<4} {item['tiêu_chí']:<25} {item['trọng_số']:<12} {item['câu_hỏi']}")

    print(f"\n  📌 Cách chấm: Đạt (✅) / Cần sửa (⚠️) / Sai (❌)")
    print(f"  📌 API tốt: ≥ 10/14 tiêu chí đạt ✅")
    print(f"  📌 API chấp nhận được: 7-9/14 đạt ✅")
    print(f"  📌 API cần refactor: < 7/14 đạt ✅")


# ============================================================================
# PHẦN 5: TỔNG KẾT — BEFORE vs AFTER
# ============================================================================

def summary_before_after():
    """Tổng kết: So sánh API trước và sau khi áp dụng best practices."""
    print("\n\n" + "=" * 70)
    print("TỔNG KẾT: BEFORE vs AFTER")
    print("=" * 70)

    comparisons = [
        ("GET /getAllProducts",                     "GET /api/v1/products?page=1&limit=20"),
        ("POST /createNewProduct",                  "POST /api/v1/products"),
        ("GET /product/info?id=5",                  "GET /api/v1/products/5"),
        ("POST /updateProduct/5",                   "PATCH /api/v1/products/5"),
        ("GET /deleteProduct?id=5",                 "DELETE /api/v1/products/5"),
        ("GET /getOrdersByUser?userId=10",          "GET /api/v1/users/10/orders"),
        ("POST /api/order/add-to-cart",             "POST /api/v1/cart/items"),
        ("GET /api/v1/Products/5/Reviews",          "GET /api/v1/products/5/reviews"),
        ("200 {code:-1, msg:'err'}",                "422 {error:{message:'Validation failed'}}"),
        ("GET /search-products-by-category-and-price", "GET /api/v1/products?category=fashion&min_price=100000"),
    ]

    print(f"\n  {'❌ BEFORE (Poorly Designed)':<50} {'✅ AFTER (RESTful)'}")
    print(f"  {'─'*49} {'─'*49}")

    for before, after in comparisons:
        print(f"  {before:<50} {after}")

    print(f"\n  📌 Nguyên tắc cốt lõi:")
    print(f"     1. Consistency — nhất quán trong naming, format, versioning")
    print(f"     2. Clarity — rõ ràng, dễ hiểu, không viết tắt")
    print(f"     3. Extensibility — dễ mở rộng mà không break client cũ")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║   BUỔI 3: NGUYÊN TẮC THIẾT KẾ API                                 ║")
    print("║   Sinh viên: TheDuyN17                                             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    # Phần 1: Case study — API poorly designed
    case_study_bad_api()

    # Phần 2: Bảng quy tắc thiết kế
    print_design_rules()

    # Phần 3: Peer review
    peer_review()

    # Phần 4: Checklist đánh giá
    print_review_checklist()

    # Phần 5: Tổng kết
    summary_before_after()

    print("\n\n" + "=" * 70)
    print("✅ KẾT THÚC BÀI TẬP BUỔI 3")
    print("=" * 70)
