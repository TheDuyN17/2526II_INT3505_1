import hashlib
import hmac
import json
import time
import uuid

import requests

WEBHOOK_URL = "http://localhost:5004/webhook/notifications"
WEBHOOK_SECRET = "my-super-secret-key"


def sign_payload(body: bytes) -> str:
    mac = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256)
    return "sha256=" + mac.hexdigest()


def send_event(event: dict):
    body = json.dumps(event).encode()
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": sign_payload(body),
        "X-Event-Id": event["event_id"],
    }
    try:
        response = requests.post(WEBHOOK_URL, data=body, headers=headers, timeout=5)
        print(f"[PUBLISHER] {event['event_type']} → receiver trả về {response.status_code}")
    except Exception as e:
        print(f"[PUBLISHER] Lỗi khi gửi webhook: {e}")


def simulate_payment_system():
    print("=== Hệ thống thanh toán đang xử lý... ===\n")

    time.sleep(1)
    send_event({
        "event_id": f"evt_{uuid.uuid4().hex[:8]}",
        "event_type": "payment.succeeded",
        "data": {"order_id": "ORD-999", "amount": 1500000, "currency": "VND"},
    })

    time.sleep(2)
    send_event({
        "event_id": f"evt_{uuid.uuid4().hex[:8]}",
        "event_type": "payment.failed",
        "data": {"order_id": "ORD-777", "reason": "Insufficient funds"},
    })


if __name__ == "__main__":
    simulate_payment_system()
