import random
import time

from flask import Flask, Response, jsonify, request

from observability import CONTENT_TYPE_LATEST, metrics, setup_observability
from security import rate_limit, require_api_key, setup_security


PRODUCTS = [
    {"id": 1, "name": "Clean Architecture", "stock": 12, "price": 39.9},
    {"id": 2, "name": "API Security Handbook", "stock": 6, "price": 29.5},
    {"id": 3, "name": "Observability Starter Kit", "stock": 3, "price": 49.0},
]


class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=10):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.opened_at = None

    def is_open(self):
        if self.opened_at is None:
            return False
        if time.time() - self.opened_at >= self.recovery_timeout:
            self.failure_count = 0
            self.opened_at = None
            metrics.set_circuit_breaker_open(False)
            return False
        return True

    def record_success(self):
        self.failure_count = 0
        self.opened_at = None
        metrics.set_circuit_breaker_open(False)

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.opened_at = time.time()
            metrics.set_circuit_breaker_open(True)


inventory_breaker = CircuitBreaker()


def create_app():
    app = Flask(__name__)
    setup_observability(app)
    setup_security(app)

    @app.route("/")
    def index():
        return jsonify(
            {
                "message": "Lecture 10 - Service Operation: Security & Monitoring",
                "endpoints": {
                    "products": "/api/v1/products",
                    "create_order": "POST /api/v1/orders",
                    "admin_audit": "/api/v1/admin/audit-events",
                    "health": "/health",
                    "metrics": "/metrics",
                },
                "demo_api_keys": {
                    "admin": "demo-admin-key",
                    "service": "demo-service-key",
                },
            }
        )

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "lecture-10-api"})

    @app.route("/metrics")
    def metrics_endpoint():
        return Response(metrics.render_prometheus(), content_type=CONTENT_TYPE_LATEST)

    @app.route("/api/v1/products")
    @rate_limit(limit=30, window_seconds=60)
    def get_products():
        query = request.args.get("q", "").lower()
        data = PRODUCTS
        if query:
            data = [item for item in PRODUCTS if query in item["name"].lower()]
        return jsonify({"data": data})

    @app.route("/api/v1/orders", methods=["POST"])
    @rate_limit(limit=5, window_seconds=60)
    @require_api_key(required_role="service")
    def create_order():
        payload = request.get_json(silent=True) or {}
        product_id = int(payload.get("product_id", 0))
        quantity = int(payload.get("quantity", 1))

        product = next((item for item in PRODUCTS if item["id"] == product_id), None)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        inventory_status = call_inventory_service(product_id)
        if inventory_status.get("status") != "available":
            return jsonify({"error": "Inventory temporarily unavailable"}), 503

        if quantity > product["stock"]:
            return jsonify({"error": "Not enough stock"}), 409

        return jsonify(
            {
                "message": "Order created",
                "order": {
                    "product_id": product_id,
                    "quantity": quantity,
                    "total": round(product["price"] * quantity, 2),
                },
            }
        ), 201

    @app.route("/api/v1/admin/audit-events")
    @require_api_key(required_role="admin")
    def audit_events():
        return jsonify(
            {
                "message": "Audit events are written as JSON lines",
                "file": "Lecture_10/logs/audit.log",
                "examples": ["auth", "rate_limit", "waf_block"],
            }
        )

    return app


def call_inventory_service(product_id):
    if inventory_breaker.is_open():
        return {"status": "circuit_open", "product_id": product_id}

    try:
        if request.args.get("fail_inventory") == "true" or random.random() < 0.05:
            raise TimeoutError("inventory service timeout")
        inventory_breaker.record_success()
        return {"status": "available", "product_id": product_id}
    except TimeoutError:
        inventory_breaker.record_failure()
        return {"status": "unavailable", "product_id": product_id}


if __name__ == "__main__":
    app = create_app()
    print("Lecture 10 API is running on http://127.0.0.1:5010")
    app.run(host="0.0.0.0", port=5010, debug=True)
