from flask import Flask, request, jsonify

app = Flask(__name__)


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


# v3: Thêm validate input — kiểm tra field bắt buộc, kiểm tra email trùng
def validate_user_data(data, required_fields):
    """Trả về danh sách lỗi nếu có."""
    errors = []
    for field in required_fields:
        if not data.get(field, "").strip():
            errors.append(f"'{field}' is required and cannot be empty")
    return errors


def email_exists(email, exclude_uid=None):
    return any(u.email == email and u.uid != exclude_uid for u in users)


@app.route("/users", methods=["GET", "POST"])
def handle_users():
    if request.method == "GET":
        return jsonify([u.to_json() for u in users]), 200

    # POST
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    errors = validate_user_data(data, ["name", "email"])
    if errors:
        return jsonify({"errors": errors}), 422

    if email_exists(data["email"]):
        return jsonify({"error": "Email already in use"}), 409

    global next_id
    user = User(str(next_id), data["name"].strip(), data["email"].strip())
    next_id += 1
    users.append(user)
    return jsonify(user.to_json()), 201


@app.route("/users/<uid>", methods=["GET", "PUT", "PATCH", "DELETE"])
def handle_user_by_id(uid):
    user, index = find_user(uid)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    if request.method == "GET":
        return jsonify(user.to_json()), 200

    if request.method == "DELETE":
        users.pop(index)
        return "", 204

    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    if request.method == "PUT":
        errors = validate_user_data(data, ["name", "email"])
        if errors:
            return jsonify({"errors": errors}), 422
        if email_exists(data["email"], exclude_uid=uid):
            return jsonify({"error": "Email already in use"}), 409
        users[index] = User(uid, data["name"].strip(), data["email"].strip())
        return jsonify(users[index].to_json()), 200

    # PATCH — chỉ cập nhật field được gửi lên
    if "email" in data:
        if not data["email"].strip():
            return jsonify({"error": "'email' cannot be empty"}), 422
        if email_exists(data["email"], exclude_uid=uid):
            return jsonify({"error": "Email already in use"}), 409
        user.email = data["email"].strip()
    if "name" in data:
        if not data["name"].strip():
            return jsonify({"error": "'name' cannot be empty"}), 422
        user.name = data["name"].strip()
    return jsonify(user.to_json()), 200


if __name__ == "__main__":
    PORT = 5000
    print(f"Server running at http://localhost:{PORT}")
    app.run(port=PORT)
