from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock Database
users_db = {
    1: {"id": 1, "name": "Alice", "role": "admin"},
    2: {"id": 2, "name": "Bob", "role": "user"}
}
current_id = 2

@app.route('/users', methods=['GET'])
def get_users():
    """Read: Lấy danh sách users"""
    return jsonify(list(users_db.values())), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Read: Lấy thông tin 1 user"""
    user = users_db.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

@app.route('/users', methods=['POST'])
def create_user():
    """Create: Tạo user mới"""
    global current_id
    data = request.json
    current_id += 1
    new_user = {
        "id": current_id,
        "name": data.get("name"),
        "role": data.get("role", "user")
    }
    users_db[current_id] = new_user
    return jsonify(new_user), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update: Cập nhật thông tin user"""
    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    users_db[user_id]["name"] = data.get("name", users_db[user_id]["name"])
    users_db[user_id]["role"] = data.get("role", users_db[user_id]["role"])
    return jsonify(users_db[user_id]), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete: Xóa user"""
    if user_id in users_db:
        del users_db[user_id]
        return '', 204
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(port=5001, debug=True)
