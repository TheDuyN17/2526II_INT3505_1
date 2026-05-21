# Mẫu thiết kế Webhook & Event-driven

## Mô tả

Trong kiến trúc truyền thống, nếu hệ thống A muốn biết hệ thống B đã xử lý xong chưa, nó phải liên tục "hỏi" (Polling), ví dụ: cứ 5 giây gọi `GET /status` một lần. Cách này tốn tài nguyên và không real-time.

**Webhook (Event-driven)** giải quyết bằng cơ chế "Đừng gọi tôi, tôi sẽ gọi bạn":
- Receiver cung cấp một URL công khai và chờ sự kiện
- Publisher khi xử lý xong sẽ tự động POST dữ liệu sự kiện tới URL đó

## Bảo mật Webhook: HMAC Signature

Vấn đề: ai cũng có thể POST giả mạo đến URL của Receiver. Stripe, GitHub đều giải quyết bằng **HMAC-SHA256 signature**:

1. Publisher và Receiver chia sẻ một `WEBHOOK_SECRET`
2. Publisher tính `HMAC-SHA256(secret, body)` và gửi kèm header `X-Webhook-Signature: sha256=<hex>`
3. Receiver tính lại chữ ký và so sánh — nếu không khớp → từ chối (401)

```
[Publisher] → POST /webhook/notifications
              Header: X-Webhook-Signature: sha256=abc123...
              Body:   {"event_type": "payment.succeeded", ...}

[Receiver]  → verify_signature(body, header) → ✓ → xử lý sự kiện
```

## Chạy thử

**Bước 1: Cài đặt**

```bash
pip install -r requirements.txt   # ở thư mục w11-12
```

**Bước 2: Mở Terminal 1 — bật Receiver**

```bash
cd w11-12/webhook
python receiver.py
```

**Bước 3: Mở Terminal 2 — kích hoạt Publisher**

```bash
cd w11-12/webhook
python publisher.py
```

Bạn sẽ thấy Publisher ký và gửi event, Receiver xác thực chữ ký và xử lý.

**Demo chữ ký không hợp lệ:**

```bash
curl -X POST http://localhost:5004/webhook/notifications \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: sha256=invalid" \
  -d '{"event_type": "payment.succeeded"}'
# → 401 Invalid signature
```
