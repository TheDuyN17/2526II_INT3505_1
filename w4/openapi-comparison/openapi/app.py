from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "year": 2008, "genre": "Technology", "available": True},
    {"id": 2, "title": "Đắc nhân tâm", "author": "Dale Carnegie", "year": 1936, "genre": "Self-help", "available": True},
    {"id": 3, "title": "Nhà giả kim", "author": "Paulo Coelho", "year": 1988, "genre": "Fiction", "available": False},
]

next_id = 4

@app.route('/api/books', methods=['GET'])
def get_books():
    result = books.copy()
    search = request.args.get('search', '')
    genre = request.args.get('genre', '')
    if search:
        s = search.lower()
        result = [b for b in result if s in b['title'].lower() or s in b['author'].lower()]
    if genre:
        result = [b for b in result if b.get('genre', '').lower() == genre.lower()]
    return jsonify(result)

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
        "genre": data.get('genre'),
        "available": True
    }
    next_id += 1
    books.append(new_book)
    return jsonify(new_book), 201

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"message": "Resource not found"}), 404
    return jsonify(book)

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

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"message": "Resource not found"}), 404
    books.remove(book)
    return jsonify({"message": "Xóa thành công"})

if __name__ == '__main__':
    app.run(port=3000, debug=True)