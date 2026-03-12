from flask import Flask, request, jsonify

app = Flask(__name__)


# Model User
class User:
    def __init__(self, uid, name, email):
        self.uid = uid
        self.name = name
        self.email = email

    def to_json(self):
        return {
            "id": self.uid,
            "name": self.name,
            "email": self.email
        }


# Fake database
users = [
    User("1", "Nguyen The Duy", "theduynguyen27@gmail.com"),
]


# Helper: tìm user theo id
def find_user(uid):
    for i in range(len(users)):
        if users[i].uid == uid:
            return users[i], i
    return None, None


# GET + POST /users
@app.route("/users", methods=["GET", "POST"])
def handle_users():

    if request.method == "GET":
        result = list(map(lambda u: u.to_json(), users))
        return jsonify(result), 200

    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid data"}), 400

    user = User(data["id"], data["name"], data["email"])
    users.append(user)

    return jsonify(user.to_json()), 201


# PUT PATCH DELETE /users/<id>
@app.route("/users/<uid>", methods=["PUT", "PATCH", "DELETE"])
def handle_user_by_id(uid):

    user, index = find_user(uid)

    if user is None:
        return "", 404

    if request.method == "DELETE":
        users.pop(index)
        return "", 204

    data = request.get_json()

    if data is None:
        return "", 400

    if request.method == "PUT":
        updated = User(uid, data["name"], data["email"])
        users[index] = updated
        return jsonify(updated.to_json()), 200

    if request.method == "PATCH":
        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)
        return jsonify(user.to_json()), 200


if __name__ == "__main__":
    PORT = 5000
    print(f"Server running at http://localhost:{PORT}")
    app.run(port=PORT)