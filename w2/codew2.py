import logging
import uuid
from flask import Flask, request, jsonify

# v4: UUID tự sinh, logging, tìm kiếm theo name/email, phân trang
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


class User:
    def __init__(self, uid, name, email):
        self.uid = uid
        self.name = name
        self.email = email

    def to_json(self):
        return {"id": self.uid, "name": self.name, "email": self.email}


users = [
    User(str(uuid.uuid4()), "Nguyen The Duy", "theduynguyen27@gmail.com"),
]


def find_user(uid):
    for i, u in enumerate(users):
        if u.uid == uid:
            return u, i
    return None, None


def validate_user_data(data, required_fields):
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
        # --- Tìm kiếm theo name hoặc email ---
        query = request.args.get("q", "").strip().lower()
        filtered = users
        if query:
            filtered = [
                u for u in users
                if query in u.name.lower() or query in u.email.lower()
            ]

        # --- Phân trang ---
        try:
            page = max(1, int(request.args.get("page", 1)))
            per_page = max(1, min(100, int(request.args.get("per_page", 10))))
        except ValueError:
            return jsonify({"error": "page and per_page must be integers"}), 400

        total = len(filtered)
        start = (page - 1) * per_page
        paged = filtered[start: start + per_page]

        logger.info("GET /users  query=%r  page=%d  total=%d", query, page, total)

        return jsonify({
            "data": [u.to_json() for u in paged],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": max(1, -(-total // per_page)),  # ceil division
            }
        }), 200

    # POST
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    errors = validate_user_data(data, ["name", "email"])
    if errors:
        return jsonify({"errors": errors}), 422

    if email_exists(data["email"]):
        return jsonify({"error": "Email already in use"}), 409

    # UUID tự động sinh — không cần client truyền id
    user = User(str(uuid.uuid4()), data["name"].strip(), data["email"].strip())
    users.append(user)
    logger.info("POST /users  created id=%s", user.uid)
    return jsonify(user.to_json()), 201


@app.route("/users/<uid>", methods=["GET", "PUT", "PATCH", "DELETE"])
def handle_user_by_id(uid):
    user, index = find_user(uid)

    if user is None:
        logger.warning("User not found: id=%s", uid)
        return jsonify({"error": "User not found"}), 404

    if request.method == "GET":
        return jsonify(user.to_json()), 200

    if request.method == "DELETE":
        users.pop(index)
        logger.info("DELETE /users/%s", uid)
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
        logger.info("PUT /users/%s", uid)
        return jsonify(users[index].to_json()), 200

    # PATCH
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
    logger.info("PATCH /users/%s", uid)
    return jsonify(user.to_json()), 200


if __name__ == "__main__":
    PORT = 5000
    logger.info("Server running at http://localhost:%d", PORT)
    app.run(port=PORT, debug=False)
