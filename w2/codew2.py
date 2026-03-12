from flask import Flask, request, jsonify

app = Flask(__name__)

# Fake database - danh sách dict đơn giản
users = [
    {"id": "1", "name": "Nguyen The Duy", "email": "theduynguyen27@gmail.com"}
]

next_id = 2


@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users), 200


@app.route("/users", methods=["POST"])
def create_user():
    global next_id
    data = request.get_json()
    user = {
        "id": str(next_id),
        "name": data["name"],
        "email": data["email"]
    }
    next_id += 1
    users.append(user)
    return jsonify(user), 201


if __name__ == "__main__":
    app.run(port=5000)
