import hashlib
import hmac
import logging

from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WEBHOOK_SECRET = "my-super-secret-key"


def verify_signature(payload: bytes, signature_header: str) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


@app.route("/webhook/notifications", methods=["POST"])
def handle_webhook():
    raw_body = request.get_data()
    signature = request.headers.get("X-Webhook-Signature", "")

    if not verify_signature(raw_body, signature):
        logger.warning("[RECEIVER] Webhook bị từ chối: chữ ký không hợp lệ")
        return jsonify({"error": "Invalid signature"}), 401

    event = request.get_json(force=True)
    if not event:
        return jsonify({"error": "Invalid payload"}), 400

    event_type = event.get("event_type")
    event_id = event.get("event_id", "unknown")

    if event_type == "payment.succeeded":
        order_id = event["data"]["order_id"]
        amount = event["data"]["amount"]
        logger.info(
            f"[RECEIVER] {event_id}: Thanh toán thành công đơn {order_id} "
            f"- {amount:,} VND → Gửi email xác nhận"
        )

    elif event_type == "payment.failed":
        order_id = event["data"]["order_id"]
        reason = event["data"]["reason"]
        logger.warning(
            f"[RECEIVER] {event_id}: Thanh toán thất bại đơn {order_id} "
            f"({reason}) → Gửi thông báo retry"
        )

    else:
        logger.info(f"[RECEIVER] {event_id}: Sự kiện không xác định: {event_type}")

    return jsonify({"status": "received", "event_id": event_id}), 200


if __name__ == "__main__":
    print("Webhook Receiver đang chạy tại cổng 5004 và chờ sự kiện...")
    app.run(port=5004, debug=False)
