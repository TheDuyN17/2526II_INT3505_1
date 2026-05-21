from flask import Flask, jsonify

app = Flask(__name__)

VALID_TRANSITIONS = {
    "PENDING": {"pay": "PAID", "cancel": "CANCELLED"},
    "PAID": {"ship": "SHIPPED", "refund": "REFUNDED"},
}

orders = {
    "ORD123": {"id": "ORD123", "status": "PENDING", "amount": 100},
    "ORD124": {"id": "ORD124", "status": "PAID", "amount": 200},
    "ORD125": {"id": "ORD125", "status": "SHIPPED", "amount": 300},
}


def generate_links(order):
    order_id = order["id"]
    status = order["status"]
    base = "http://localhost:5003"

    links = [{"rel": "self", "href": f"{base}/orders/{order_id}", "method": "GET"}]
    for action in VALID_TRANSITIONS.get(status, {}):
        links.append({
            "rel": action,
            "href": f"{base}/orders/{order_id}/{action}",
            "method": "POST",
        })
    return links


@app.route("/orders/<order_id>")
def get_order(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify({"order": order, "_links": generate_links(order)})


@app.route("/orders/<order_id>/<action>", methods=["POST"])
def process_action(order_id, action):
    order = orders.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    transitions = VALID_TRANSITIONS.get(order["status"], {})
    if action not in transitions:
        return jsonify({
            "error": f"Action '{action}' không hợp lệ ở trạng thái '{order['status']}'",
            "allowed_actions": list(transitions.keys()),
        }), 422

    order["status"] = transitions[action]
    return jsonify({"order": order, "_links": generate_links(order)})


if __name__ == "__main__":
    app.run(port=5003, debug=True)
