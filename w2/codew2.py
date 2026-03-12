from flask import Flask, request, jsonify

app = Flask(__name__)


# v2: Tách User thành class riêng, thêm đủ CRUD (GET by id, PUT, DELETE)
class User:
    def __init__(self, uid, name, email):
        self.uid = uid
        self.name = name
        self.email = email

    def to_json(self):
        return {"id": self.uid, "name": self.name, "email": self.email}


users = [
    User("1", "Nguyen The Duy", "theduynguyen27@gmail.com"),
]

next_id = 2


def find_user(uid):
    for i, u in enumerate(users):
        if u.uid == uid:
            return u, i
    return None, None


# GET /users  — lấy tất cả
# POST /users — tạo mới
@app.route("/users", methods=["GET", "POST"])
def handle_users():
    if request.method == "GET":
        return jsonify([u.to_json() for u in users]), 200

    global next_id
    data = request.get_json()
    user = User(str(next_id), data["name"], data["email"])
    next_id += 1
    users.append(user)
    return jsonify(user.to_json()), 201


# GET /users/<id>  — lấy một user
# PUT /users/<id>  — thay toàn bộ
# DELETE /users/<id> — xoá
@app.route("/users/<uid>", methods=["GET", "PUT", "DELETE"])
def handle_user_by_id(uid):
    user, index = find_user(uid)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    if request.method == "GET":
        return jsonify(user.to_json()), 200

    if request.method == "DELETE":
        users.pop(index)
        return "", 204

    # PUT
    data = request.get_json()
    users[index] = User(uid, data["name"], data["email"])
    return jsonify(users[index].to_json()), 200


if __name__ == "__main__":
    PORT = 5000
    print(f"Server running at http://localhost:{PORT}")
    app.run(port=PORT)
