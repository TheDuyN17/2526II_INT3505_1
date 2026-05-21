# Week 10: Service Operation - Security & Monitoring

Demo Flask API minh hoạ hai nhóm kiến thức chính trong vận hành production:

- **Observability**: structured JSON logs, audit logs, Prometheus metrics, distributed tracing (OpenTelemetry), request/trace ID.
- **Production security**: security headers, WAF cơ bản, rate limiting theo endpoint, API key authorization, audit logs, circuit breaker.

## Kiến trúc

```
app.py           - Flask app, routes, circuit breaker
observability.py - Structured logging (JSON), Prometheus metrics, OpenTelemetry tracing
security.py      - WAF, rate limit (global + per-endpoint), API key auth, audit log, security headers
```

## Chạy API local

```bash
cd w10
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

API chạy ở `http://127.0.0.1:5010`

## Tính năng

### 1. Structured Logging (tương đương Winston trong Node.js)

Python sử dụng `logging` module với `JsonFormatter` tự triển khai — output JSON có cùng cấu trúc như Winston:

```json
{"timestamp": "2024-01-01T10:00:00", "level": "INFO", "logger": "lecture_10.app", "message": "request_completed", "trace_id": "...", "method": "GET", "path": "/api/v1/products", "status_code": 200, "duration_ms": 2.5}
```

Hai logger riêng biệt:
- `app_logger` → `logs/app.log` (request log)
- `audit_logger` → `logs/audit.log` (security event log)

Bật ghi file log:

```bash
LOG_TO_FILE=true python app.py
```

### 2. Prometheus Metrics

Endpoint `/metrics` export theo format Prometheus:

```
flask_http_requests_total{method, path, status}       - Counter
flask_http_request_duration_seconds{method, path, status} - Histogram
security_events_total{type}                            - Counter (auth, rate_limit, waf_block)
circuit_breaker_open                                   - Gauge (0/1)
```

Chạy Prometheus bằng Docker để scrape API:

```bash
docker run --rm --name w10-prometheus \
  --add-host=host.docker.internal:host-gateway \
  -p 9090:9090 \
  -v "$PWD/prometheus.yml:/etc/prometheus/prometheus.yml:ro" \
  prom/prometheus
```

Mở Prometheus UI: `http://127.0.0.1:9090`

PromQL demo:

```promql
flask_http_requests_total
rate(flask_http_requests_total[1m])
histogram_quantile(0.95, rate(flask_http_request_duration_seconds_bucket[5m]))
security_events_total
circuit_breaker_open
```

### 3. Distributed Tracing (OpenTelemetry)

Mỗi request được gán `trace_id` (lấy từ header `traceparent` hoặc `X-Request-Id`), trả về qua header `X-Request-Id`.

```bash
curl -H "X-Request-Id: my-trace-001" http://127.0.0.1:5010/api/v1/products
```

### 4. Rate Limiting theo endpoint

Hai lớp rate limiting độc lập:

| Lớp | Giới hạn | Mục đích |
|-----|----------|----------|
| Global (WAF) | 100 req/phút | Chống DDoS |
| `GET /api/v1/products` | 30 req/phút | Giới hạn read |
| `POST /api/v1/orders` | 5 req/phút | Giới hạn write |

Demo rate limit của endpoint products (vượt 30 req/phút):

```bash
for i in {1..35}; do curl -i http://127.0.0.1:5010/api/v1/products; done
```

Demo rate limit của endpoint orders (vượt 5 req/phút):

```bash
for i in {1..7}; do
  curl -i -X POST http://127.0.0.1:5010/api/v1/orders \
    -H "Content-Type: application/json" \
    -H "X-Api-Key: demo-service-key" \
    -d '{"product_id": 1, "quantity": 1}'
done
```

Khi bị chặn, response trả về:

```json
HTTP/1.1 429 Too Many Requests
Retry-After: 42

{"error": "Too Many Requests", "retry_after_seconds": 42}
```

### 5. WAF cơ bản

Chặn các pattern nguy hiểm trong URL và body:
- XSS: `<script>`, `javascript:`
- SQL Injection: `union select`, `drop table`, `or 1=1`
- Path Traversal: `../`, `..\`
- Payload quá lớn: > 16 KB

Demo WAF chặn XSS:

```bash
curl "http://127.0.0.1:5010/api/v1/products?q=%3Cscript%3Ealert(1)%3C/script%3E"
```

### 6. API Key Authorization

| Key | Role | Quyền truy cập |
|-----|------|----------------|
| `demo-admin-key` | admin | `/api/v1/admin/audit-events` |
| `demo-service-key` | service | `POST /api/v1/orders` |

Demo thành công:

```bash
curl -X POST http://127.0.0.1:5010/api/v1/orders \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: demo-service-key" \
  -d '{"product_id": 1, "quantity": 2}'
```

Demo thiếu API key (401):

```bash
curl -X POST http://127.0.0.1:5010/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

Demo sai role (403):

```bash
curl -X POST http://127.0.0.1:5010/api/v1/orders \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: demo-admin-key" \
  -d '{"product_id": 1, "quantity": 2}'
```

### 7. Circuit Breaker

`CircuitBreaker` bảo vệ khi gọi inventory service:

- Trạng thái **Closed** (bình thường): forward request đến service
- Sau 3 lần fail liên tiếp → chuyển sang **Open**, trả về lỗi ngay không gọi service
- Sau 10 giây → **Half-Open**, thử lại

Demo ép circuit breaker mở:

```bash
for i in {1..4}; do
  curl -X POST "http://127.0.0.1:5010/api/v1/orders?fail_inventory=true" \
    -H "Content-Type: application/json" \
    -H "X-Api-Key: demo-service-key" \
    -d '{"product_id": 1, "quantity": 1}'
done
```

Kiểm tra trạng thái qua Prometheus:

```promql
circuit_breaker_open
```

### 8. Security Headers

Mọi response đều có:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 9. Audit Log

Mọi security event được ghi ra `logs/audit.log` dạng JSON:

```json
{"timestamp": "...", "level": "INFO", "logger": "lecture_10.audit", "message": "security_event", "trace_id": "...", "event_type": "rate_limit", "status": "blocked", "path": "/api/v1/products", "client": "127.0.0.1", "details": {"endpoint": "/api/v1/products", "retry_after_seconds": 42}}
```

Các event type: `auth`, `rate_limit`, `waf_block`.

## Deploy Kubernetes local (kind)

Cài tool:

```bash
cd w10
./scripts/install-k8s-tools.sh
export PATH="$PWD/bin:$PATH"
```

Tạo cluster, build image, deploy:

```bash
./scripts/bootstrap-kind.sh
```

URL sau khi deploy:

```
API:        http://127.0.0.1:8080
Prometheus: http://127.0.0.1:19090
Grafana:    http://127.0.0.1:3000  (admin/admin)
```

Xóa cluster:

```bash
./scripts/delete-kind.sh
```

Luồng observability trên Kubernetes:

```
API stdout JSON logs  →  Promtail  →  Loki   →  Grafana
API /metrics          →  Prometheus            →  Grafana
API OTLP traces       →  OTel Collector  →  Tempo  →  Grafana
```

Grafana Loki query:

```logql
{app="lecture-10-api"}
```

## Bảng kiến thức

| Yêu cầu | File | Vị trí |
|---------|------|--------|
| Structured logging (Winston equivalent) | `observability.py` | `JsonFormatter`, `build_logger()`, `app_logger` |
| Prometheus metrics | `observability.py`, `prometheus.yml` | `MetricsStore`, endpoint `/metrics` |
| Distributed tracing | `observability.py` | `get_trace_id()`, `setup_tracing()` |
| Rate limit theo endpoint | `security.py`, `app.py` | `rate_limit()` decorator, `@rate_limit(limit=30)` |
| WAF cơ bản | `security.py` | `SUSPICIOUS_PATTERNS`, `waf_and_rate_limit()` |
| API key authorization | `security.py`, `app.py` | `require_api_key()`, `POST /api/v1/orders` |
| Audit log | `security.py` | `audit()`, `audit_logger` |
| Security headers | `security.py` | `add_security_headers()` |
| Circuit breaker | `app.py` | `CircuitBreaker`, `call_inventory_service()` |
| Deploy Docker/K8s | `Dockerfile`, `k8s/` | gunicorn, kind manifests |
