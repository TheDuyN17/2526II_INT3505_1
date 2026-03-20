from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Dữ liệu mẫu
books = [
    {"id": 1, "title": "Lập trình API với Node.js", "author": "Nguyen Van A", "year": 2024, "genre": "Technology"},
    {"id": 2, "title": "Python cơ bản", "author": "Tran Van B", "year": 2023, "genre": "Technology"},
    {"id": 3, "title": "Đắc nhân tâm", "author": "Dale Carnegie", "year": 1936, "genre": "Self-help"},
    {"id": 4, "title": "Nhà giả kim", "author": "Paulo Coelho", "year": 1988, "genre": "Fiction"},
    {"id": 5, "title": "Clean Code", "author": "Robert C. Martin", "year": 2008, "genre": "Technology"},
]

next_id = 6

# GET /api/books - Lấy danh sách, tìm kiếm, lọc, sắp xếp
@app.route('/api/books', methods=['GET'])
def get_books():
    result = books.copy()

    # Tìm kiếm theo tên hoặc tác giả
    search = request.args.get('search', '', type=str)
    if search:
        search_lower = search.lower()
        result = [b for b in result if search_lower in b['title'].lower() or search_lower in b['author'].lower()]

    # Lọc theo thể loại
    genre = request.args.get('genre', '', type=str)
    if genre:
        result = [b for b in result if b.get('genre', '').lower() == genre.lower()]

    # Sắp xếp
    sort_by = request.args.get('sort_by', '', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)
    if sort_by in ['title', 'author', 'year']:
        reverse = sort_order.lower() == 'desc'
        result = sorted(result, key=lambda b: b.get(sort_by, ''), reverse=reverse)

    # Phân trang
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    start = (page - 1) * limit
    end = start + limit

    return jsonify({
        "total": len(result),
        "page": page,
        "limit": limit,
        "data": result[start:end]
    })

# POST /api/books - Thêm sách mới
@app.route('/api/books', methods=['POST'])
def create_book():
    global next_id
    data = request.get_json()

    if not data or not data.get('title') or not data.get('author'):
        return jsonify({"message": "title và author là bắt buộc"}), 400

    new_book = {
        "id": next_id,
        "title": data['title'],
        "author": data['author'],
        "year": data.get('year'),
        "genre": data.get('genre')
    }
    next_id += 1
    books.append(new_book)
    return jsonify(new_book), 201

# GET /api/books/<id> - Lấy sách theo ID
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"message": "Resource not found"}), 404
    return jsonify(book)

# PUT /api/books/<id> - Cập nhật sách
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"message": "Resource not found"}), 404

    data = request.get_json()
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({"message": "title và author là bắt buộc"}), 400

    book['title'] = data['title']
    book['author'] = data['author']
    book['year'] = data.get('year', book['year'])
    book['genre'] = data.get('genre', book['genre'])
    return jsonify(book)

# DELETE /api/books/<id> - Xóa sách
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"message": "Resource not found"}), 404
    books.remove(book)
    return jsonify({"message": "Xóa thành công"})

# GET /api/books/stats - Thống kê
@app.route('/api/books/stats', methods=['GET'])
def get_stats():
    genres = {}
    for book in books:
        g = book.get('genre', 'Unknown')
        genres[g] = genres.get(g, 0) + 1

    return jsonify({
        "total_books": len(books),
        "by_genre": genres,
        "genres_list": list(genres.keys())
    })

# GET /api/genres - Lấy danh sách thể loại
@app.route('/api/genres', methods=['GET'])
def get_genres():
    genres = list(set(b.get('genre', 'Unknown') for b in books))
    return jsonify(genres)

if __name__ == '__main__':
    app.run(port=3000, debug=True)