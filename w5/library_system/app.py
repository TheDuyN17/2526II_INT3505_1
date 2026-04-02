"""
Library Management System - Flask REST API
Quản lý thư viện sách với 3 kiểu phân trang: page-based, offset-limit, cursor-based
"""

from flask import Flask, request, jsonify, render_template, url_for, abort
from datetime import datetime
import copy

from pagination import (
    PageBasedPagination,
    OffsetLimitPagination,
    CursorBasedPagination,
    detect_pagination_type,
)

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # Support Vietnamese characters

# ─────────────────────────────────────────────
# IN-MEMORY DATABASE (25 sách tiếng Việt)
# ─────────────────────────────────────────────

BOOKS = [
    {
        "id": 1,
        "title": "Dế Mèn Phiêu Lưu Ký",
        "author": "Tô Hoài",
        "genre": "Thiếu nhi",
        "year": 1941,
        "pages": 196,
        "available": True,
        "rating": 4.8,
        "isbn": "978-604-1-01234-1",
    },
    {
        "id": 2,
        "title": "Số Đỏ",
        "author": "Vũ Trọng Phụng",
        "genre": "Tiểu thuyết",
        "year": 1936,
        "pages": 312,
        "available": True,
        "rating": 4.7,
        "isbn": "978-604-1-01234-2",
    },
    {
        "id": 3,
        "title": "Chí Phèo",
        "author": "Nam Cao",
        "genre": "Truyện ngắn",
        "year": 1941,
        "pages": 48,
        "available": False,
        "rating": 4.9,
        "isbn": "978-604-1-01234-3",
    },
    {
        "id": 4,
        "title": "Tắt Đèn",
        "author": "Ngô Tất Tố",
        "genre": "Tiểu thuyết",
        "year": 1939,
        "pages": 236,
        "available": True,
        "rating": 4.6,
        "isbn": "978-604-1-01234-4",
    },
    {
        "id": 5,
        "title": "Truyện Kiều",
        "author": "Nguyễn Du",
        "genre": "Thơ",
        "year": 1820,
        "pages": 320,
        "available": True,
        "rating": 4.9,
        "isbn": "978-604-1-01234-5",
    },
    {
        "id": 6,
        "title": "Lão Hạc",
        "author": "Nam Cao",
        "genre": "Truyện ngắn",
        "year": 1943,
        "pages": 32,
        "available": True,
        "rating": 4.7,
        "isbn": "978-604-1-01234-6",
    },
    {
        "id": 7,
        "title": "Đất Rừng Phương Nam",
        "author": "Đoàn Giỏi",
        "genre": "Thiếu nhi",
        "year": 1957,
        "pages": 268,
        "available": False,
        "rating": 4.8,
        "isbn": "978-604-1-01234-7",
    },
    {
        "id": 8,
        "title": "Nỗi Buồn Chiến Tranh",
        "author": "Bảo Ninh",
        "genre": "Tiểu thuyết",
        "year": 1990,
        "pages": 368,
        "available": True,
        "rating": 4.8,
        "isbn": "978-604-1-01234-8",
    },
    {
        "id": 9,
        "title": "Mắt Biếc",
        "author": "Nguyễn Nhật Ánh",
        "genre": "Tiểu thuyết",
        "year": 1990,
        "pages": 262,
        "available": True,
        "rating": 4.6,
        "isbn": "978-604-1-01234-9",
    },
    {
        "id": 10,
        "title": "Tôi Thấy Hoa Vàng Trên Cỏ Xanh",
        "author": "Nguyễn Nhật Ánh",
        "genre": "Thiếu nhi",
        "year": 2010,
        "pages": 332,
        "available": True,
        "rating": 4.7,
        "isbn": "978-604-1-01234-10",
    },
    {
        "id": 11,
        "title": "Cho Tôi Xin Một Vé Đi Tuổi Thơ",
        "author": "Nguyễn Nhật Ánh",
        "genre": "Thiếu nhi",
        "year": 2008,
        "pages": 178,
        "available": False,
        "rating": 4.5,
        "isbn": "978-604-1-01234-11",
    },
    {
        "id": 12,
        "title": "Đắc Nhân Tâm",
        "author": "Dale Carnegie",
        "genre": "Kỹ năng sống",
        "year": 1936,
        "pages": 320,
        "available": True,
        "rating": 4.6,
        "isbn": "978-604-1-01234-12",
    },
    {
        "id": 13,
        "title": "Nhà Giả Kim",
        "author": "Paulo Coelho",
        "genre": "Tiểu thuyết",
        "year": 1988,
        "pages": 228,
        "available": True,
        "rating": 4.7,
        "isbn": "978-604-1-01234-13",
    },
    {
        "id": 14,
        "title": "Người Đua Diều",
        "author": "Khaled Hosseini",
        "genre": "Tiểu thuyết",
        "year": 2003,
        "pages": 372,
        "available": False,
        "rating": 4.8,
        "isbn": "978-604-1-01234-14",
    },
    {
        "id": 15,
        "title": "Cà Phê Cùng Tony",
        "author": "Tony Buổi Sáng",
        "genre": "Kỹ năng sống",
        "year": 2013,
        "pages": 248,
        "available": True,
        "rating": 4.3,
        "isbn": "978-604-1-01234-15",
    },
    {
        "id": 16,
        "title": "Bắt Trẻ Đồng Xanh",
        "author": "J.D. Salinger",
        "genre": "Tiểu thuyết",
        "year": 1951,
        "pages": 277,
        "available": True,
        "rating": 4.4,
        "isbn": "978-604-1-01234-16",
    },
    {
        "id": 17,
        "title": "Chiến Tranh Và Hòa Bình",
        "author": "Leo Tolstoy",
        "genre": "Tiểu thuyết",
        "year": 1869,
        "pages": 1392,
        "available": False,
        "rating": 4.9,
        "isbn": "978-604-1-01234-17",
    },
    {
        "id": 18,
        "title": "Harry Potter Và Hòn Đá Phù Thủy",
        "author": "J.K. Rowling",
        "genre": "Phiêu lưu",
        "year": 1997,
        "pages": 320,
        "available": True,
        "rating": 4.8,
        "isbn": "978-604-1-01234-18",
    },
    {
        "id": 19,
        "title": "Tư Duy Phản Biện",
        "author": "Richard Paul",
        "genre": "Kỹ năng sống",
        "year": 2019,
        "pages": 420,
        "available": True,
        "rating": 4.4,
        "isbn": "978-604-1-01234-19",
    },
    {
        "id": 20,
        "title": "Sapiens: Lược Sử Loài Người",
        "author": "Yuval Noah Harari",
        "genre": "Lịch sử",
        "year": 2011,
        "pages": 512,
        "available": True,
        "rating": 4.7,
        "isbn": "978-604-1-01234-20",
    },
    {
        "id": 21,
        "title": "Homo Deus: Lược Sử Tương Lai",
        "author": "Yuval Noah Harari",
        "genre": "Lịch sử",
        "year": 2015,
        "pages": 464,
        "available": False,
        "rating": 4.5,
        "isbn": "978-604-1-01234-21",
    },
    {
        "id": 22,
        "title": "Atomic Habits",
        "author": "James Clear",
        "genre": "Kỹ năng sống",
        "year": 2018,
        "pages": 320,
        "available": True,
        "rating": 4.8,
        "isbn": "978-604-1-01234-22",
    },
    {
        "id": 23,
        "title": "Tuổi Trẻ Đáng Giá Bao Nhiêu",
        "author": "Rosie Nguyễn",
        "genre": "Kỹ năng sống",
        "year": 2016,
        "pages": 200,
        "available": True,
        "rating": 4.2,
        "isbn": "978-604-1-01234-23",
    },
    {
        "id": 24,
        "title": "Đừng Bao Giờ Đi Ăn Một Mình",
        "author": "Keith Ferrazzi",
        "genre": "Kỹ năng sống",
        "year": 2005,
        "pages": 368,
        "available": True,
        "rating": 4.3,
        "isbn": "978-604-1-01234-24",
    },
    {
        "id": 25,
        "title": "Rừng Na Uy",
        "author": "Haruki Murakami",
        "genre": "Tiểu thuyết",
        "year": 1987,
        "pages": 296,
        "available": False,
        "rating": 4.6,
        "isbn": "978-604-1-01234-25",
    },
]

_next_id = 26  # auto-increment counter


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_book_or_404(book_id: int) -> dict:
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        abort(404, description=f"Không tìm thấy sách với id={book_id}")
    return book


def book_links(book_id: int) -> dict:
    """HATEOAS links cho một cuốn sách"""
    return {
        "self": url_for("get_book", book_id=book_id, _external=True),
        "update": url_for("update_book", book_id=book_id, _external=True),
        "delete": url_for("delete_book", book_id=book_id, _external=True),
        "collection": url_for("list_books", _external=True),
    }


def book_to_response(book: dict) -> dict:
    return {**book, "_links": book_links(book["id"])}


def apply_filters(books: list, args: dict) -> list:
    """Filter books by query params"""
    result = books

    q = args.get("q", "").strip().lower()
    if q:
        result = [
            b for b in result
            if q in b["title"].lower() or q in b["author"].lower()
        ]

    genre = args.get("genre", "").strip()
    if genre:
        result = [b for b in result if b["genre"].lower() == genre.lower()]

    author = args.get("author", "").strip()
    if author:
        result = [b for b in result if author.lower() in b["author"].lower()]

    available = args.get("available", "").strip().lower()
    if available in ("true", "1"):
        result = [b for b in result if b["available"]]
    elif available in ("false", "0"):
        result = [b for b in result if not b["available"]]

    year_from = args.get("year_from")
    year_to = args.get("year_to")
    if year_from:
        result = [b for b in result if b["year"] >= int(year_from)]
    if year_to:
        result = [b for b in result if b["year"] <= int(year_to)]

    return result


def apply_sort(books: list, sort_by: str, order: str) -> list:
    """Sort books"""
    valid_fields = {"id", "title", "author", "year", "pages", "rating"}
    if sort_by not in valid_fields:
        sort_by = "id"
    reverse = order.lower() == "desc"
    return sorted(books, key=lambda b: b.get(sort_by, 0), reverse=reverse)


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── GET /api/books ────────────────────────────
@app.route("/api/books", methods=["GET"])
def list_books():
    args = request.args

    # 1. Filter
    filtered = apply_filters(BOOKS, args)

    # 2. Sort
    sort_by = args.get("sort_by", "id")
    order = args.get("order", "asc")
    sorted_books = apply_sort(filtered, sort_by, order)

    # 3. Detect pagination type and paginate
    pagination_type = detect_pagination_type(args)

    # Extra params to pass to URL builder (filter/sort params)
    extra = {}
    for key in ("q", "genre", "author", "available", "year_from", "year_to", "sort_by", "order"):
        if args.get(key):
            extra[key] = args.get(key)

    if pagination_type == "cursor":
        limit = int(args.get("limit", 5))
        cursor = args.get("cursor")

        # Apply cursor filter
        if cursor:
            cursor_id = CursorBasedPagination.decode_cursor(cursor)
            if cursor_id is not None:
                sorted_books = [b for b in sorted_books if b["id"] > int(cursor_id)]

        # Fetch limit+1 to detect has_next
        fetched = sorted_books[:limit + 1]

        pager = CursorBasedPagination(
            items=fetched,
            limit=limit,
            endpoint="list_books",
            **extra,
        )
        items = pager.visible_items

    elif pagination_type == "offset":
        offset = int(args.get("offset", 0))
        limit = int(args.get("limit", 5))
        pager = OffsetLimitPagination(
            total=len(sorted_books),
            offset=offset,
            limit=limit,
            endpoint="list_books",
            **extra,
        )
        items = sorted_books[pager.offset: pager.offset + pager.limit]

    else:  # page-based (default)
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 5))
        pager = PageBasedPagination(
            total=len(sorted_books),
            page=page,
            per_page=per_page,
            endpoint="list_books",
            **extra,
        )
        items = sorted_books[pager.offset: pager.offset + pager.per_page]

    return jsonify({
        "data": [book_to_response(b) for b in items],
        "meta": pager.get_meta(),
        "_links": pager.get_links(),
    })


# ── GET /api/books/<id> ────────────────────────
@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = get_book_or_404(book_id)
    return jsonify(book_to_response(book))


# ── POST /api/books ────────────────────────────
@app.route("/api/books", methods=["POST"])
def create_book():
    global _next_id
    data = request.get_json()
    if not data:
        abort(400, description="Request body phải là JSON")

    required = ["title", "author", "genre", "year", "pages"]
    missing = [f for f in required if f not in data]
    if missing:
        abort(400, description=f"Thiếu các trường bắt buộc: {', '.join(missing)}")

    new_book = {
        "id": _next_id,
        "title": data["title"],
        "author": data["author"],
        "genre": data["genre"],
        "year": int(data["year"]),
        "pages": int(data["pages"]),
        "available": bool(data.get("available", True)),
        "rating": float(data.get("rating", 0.0)),
        "isbn": data.get("isbn", f"978-604-0-{_next_id:05d}-0"),
    }
    BOOKS.append(new_book)
    _next_id += 1

    response = jsonify(book_to_response(new_book))
    response.status_code = 201
    response.headers["Location"] = url_for("get_book", book_id=new_book["id"], _external=True)
    return response


# ── PUT /api/books/<id> ────────────────────────
@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = get_book_or_404(book_id)
    data = request.get_json()
    if not data:
        abort(400, description="Request body phải là JSON")

    updatable = ["title", "author", "genre", "year", "pages", "available", "rating", "isbn"]
    for field in updatable:
        if field in data:
            book[field] = data[field]

    return jsonify(book_to_response(book))


# ── DELETE /api/books/<id> ─────────────────────
@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = get_book_or_404(book_id)
    BOOKS.remove(book)
    return jsonify({
        "message": f"Đã xóa sách '{book['title']}' (id={book_id})",
        "_links": {"collection": url_for("list_books", _external=True)},
    })


# ── GET /api/books/genres ──────────────────────
@app.route("/api/books/genres", methods=["GET"])
def list_genres():
    genres = sorted(set(b["genre"] for b in BOOKS))
    return jsonify({
        "genres": genres,
        "total": len(genres),
        "_links": {
            "self": url_for("list_genres", _external=True),
            "books": url_for("list_books", _external=True),
        },
    })


# ── GET /api/books/stats ───────────────────────
@app.route("/api/books/stats", methods=["GET"])
def book_stats():
    total = len(BOOKS)
    available = sum(1 for b in BOOKS if b["available"])
    avg_rating = round(sum(b["rating"] for b in BOOKS) / total, 2) if total else 0
    by_genre = {}
    for b in BOOKS:
        by_genre[b["genre"]] = by_genre.get(b["genre"], 0) + 1

    return jsonify({
        "total_books": total,
        "available": available,
        "borrowed": total - available,
        "average_rating": avg_rating,
        "books_by_genre": by_genre,
        "_links": {
            "self": url_for("book_stats", _external=True),
            "books": url_for("list_books", _external=True),
        },
    })


# ── GET /api/pagination-info ───────────────────
@app.route("/api/pagination-info", methods=["GET"])
def pagination_info():
    return jsonify({
        "strategies": [
            {
                "name": "page-based",
                "params": ["page", "per_page"],
                "example": "/api/books?page=2&per_page=5",
                "sql": "LIMIT per_page OFFSET (page-1)*per_page",
                "use_case": "UI với số trang cụ thể",
            },
            {
                "name": "offset-limit",
                "params": ["offset", "limit"],
                "example": "/api/books?offset=10&limit=5",
                "sql": "LIMIT limit OFFSET offset",
                "use_case": "Data export, analytics",
            },
            {
                "name": "cursor-based",
                "params": ["cursor", "limit"],
                "example": "/api/books?cursor=<encoded>&limit=5",
                "sql": "WHERE id > cursor_id ORDER BY id LIMIT limit+1",
                "use_case": "Infinite scroll, real-time feed",
            },
        ],
        "_links": {
            "self": url_for("pagination_info", _external=True),
            "books": url_for("list_books", _external=True),
        },
    })


# ─────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad Request", "message": str(e.description)}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found", "message": str(e.description)}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method Not Allowed", "message": str(e.description)}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("=" * 60)
    print("  Library Management System - Flask REST API")
    print("  Running at: http://127.0.0.1:5000")
    print("  Demo UI  : http://127.0.0.1:5000/")
    print("  API root : http://127.0.0.1:5000/api/books")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)
