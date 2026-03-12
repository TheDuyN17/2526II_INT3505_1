from flask import Flask, jsonify, request

app = Flask(__name__)

books = [
    {"id": 1, "title": "The Hitchhiker's Guide to the Galaxy", "author": "Douglas Adams"},
    {"id": 2, "title": "Project Hail Mary", "author": "Andy Weir"},
    {"id": 3, "title": "Clean Code", "author": "Robert C. Martin"},
]

next_id = 4

# ============================================================================
# CASE STUDY: API POORLY DESIGNED (cac endpoint SAI - de phan tich loi)
# ============================================================================

@app.route('/getAllBooks', methods=['GET'])
def bad_get_all():
    return jsonify(books)

@app.route('/createBook', methods=['POST'])
def bad_create():
    data = request.get_json()
    return jsonify(data), 200

@app.route('/getBook', methods=['GET'])
def bad_get_one():
    book_id = request.args.get('id', type=int)
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"msg": "err"}), 200
    return jsonify(book)

@app.route('/updateBook/<int:book_id>', methods=['POST'])
def bad_update(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"code": -1}), 200
    data = request.get_json()
    book["title"] = data.get("Title", book["title"])
    return jsonify(book)

@app.route('/deleteBook', methods=['GET'])
def bad_delete():
    book_id = request.args.get('id', type=int)
    global books
    books = [b for b in books if b["id"] != book_id]
    return jsonify({"msg": "deleted"})

# ============================================================================
# GOOD API: Ap dung dung nguyen tac thiet ke (BAN SUA)
# ============================================================================

@app.route('/api/v1/books', methods=['GET'])
def get_books():
    result = books
    author = request.args.get('author')
    if author:
        result = [b for b in result if author.lower() in b["author"].lower()]
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    total = len(result)
    start = (page - 1) * limit
    result = result[start:start + limit]
    return jsonify({"data": result, "pagination": {"page": page, "limit": limit, "total": total}}), 200

@app.route('/api/v1/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": {"code": 404, "message": f"Book with id {book_id} not found"}}), 404
    return jsonify({"data": book}), 200

@app.route('/api/v1/books', methods=['POST'])
def create_book():
    global next_id
    data = request.get_json()
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({"error": {"code": 400, "message": "Missing required fields: title, author"}}), 400
    new_book = {"id": next_id, "title": data["title"], "author": data["author"]}
    next_id += 1
    books.append(new_book)
    response = jsonify({"data": new_book})
    response.status_code = 201
    response.headers["Location"] = f"/api/v1/books/{new_book['id']}"
    return response

@app.route('/api/v1/books/<int:book_id>', methods=['PATCH'])
def update_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": {"code": 404, "message": f"Book with id {book_id} not found"}}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": {"code": 400, "message": "Request body is required"}}), 400
    if "title" in data:
        book["title"] = data["title"]
    if "author" in data:
        book["author"] = data["author"]
    return jsonify({"data": book}), 200

@app.route('/api/v1/books/<int:book_id>', methods=['PUT'])
def replace_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": {"code": 404, "message": f"Book with id {book_id} not found"}}), 404
    data = request.get_json()
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({"error": {"code": 400, "message": "PUT requires all fields: title, author"}}), 400
    book["title"] = data["title"]
    book["author"] = data["author"]
    return jsonify({"data": book}), 200

@app.route('/api/v1/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": {"code": 404, "message": f"Book with id {book_id} not found"}}), 404
    books = [b for b in books if b["id"] != book_id]
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=5000)
