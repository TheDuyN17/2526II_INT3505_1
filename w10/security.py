import re
import os
import time
from collections import defaultdict, deque
from functools import wraps
from urllib.parse import unquote_plus

from flask import g, jsonify, request

from observability import audit_logger, metrics


API_KEYS = {
    os.getenv("DEMO_ADMIN_KEY", "demo-admin-key"): "admin",
    os.getenv("DEMO_SERVICE_KEY", "demo-service-key"): "service",
}

SUSPICIOUS_PATTERNS = [
    re.compile(r"(<script|</script>|javascript:)", re.IGNORECASE),
    re.compile(r"(union\s+select|drop\s+table|or\s+1\s*=\s*1)", re.IGNORECASE),
    re.compile(r"(\.\./|\.\.\\)"),
]


class FixedWindowRateLimiter:
    def __init__(self, limit, window_seconds):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)

    def check(self, key):
        now = time.time()
        bucket = self.requests[key]

        while bucket and bucket[0] <= now - self.window_seconds:
            bucket.popleft()

        if len(bucket) >= self.limit:
            return False, max(1, int(self.window_seconds - (now - bucket[0])))

        bucket.append(now)
        return True, 0


rate_limiter = FixedWindowRateLimiter(limit=100, window_seconds=60)


def client_key():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.remote_addr
    return request.headers.get("X-Api-Key") or ip or "anonymous"


def audit(event_type, status, details=None):
    payload = {
        "trace_id": g.get("trace_id"),
        "event_type": event_type,
        "status": status,
        "path": request.path,
        "method": request.method,
        "client": client_key(),
        "details": details or {},
    }
    audit_logger.info("security_event", extra={"extra_fields": payload})
    metrics.record_security_event(event_type)


def rate_limit(limit=10, window_seconds=60):
    limiter = FixedWindowRateLimiter(limit=limit, window_seconds=window_seconds)

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            allowed, retry_after = limiter.check(client_key())
            if not allowed:
                audit("rate_limit", "blocked", {
                    "endpoint": request.path,
                    "retry_after_seconds": retry_after,
                })
                response = jsonify({"error": "Too Many Requests", "retry_after_seconds": retry_after})
                response.status_code = 429
                response.headers["Retry-After"] = str(retry_after)
                return response
            return f(*args, **kwargs)

        return wrapper

    return decorator


def setup_security(app):
    @app.before_request
    def waf_and_rate_limit():
        if request.endpoint in {"metrics_endpoint", "health"}:
            return None

        raw_query = request.query_string.decode("utf-8", errors="ignore")
        raw_target = "%s?%s" % (request.path, raw_query)
        body = request.get_data(as_text=True) if request.content_length else ""
        combined = "%s %s" % (raw_target, body[:2000])
        decoded_combined = unquote_plus(combined)

        if request.content_length and request.content_length > 16 * 1024:
            audit("waf_block", "blocked", {"reason": "payload_too_large"})
            return jsonify({"error": "Payload too large", "trace_id": g.get("trace_id")}), 413

        for pattern in SUSPICIOUS_PATTERNS:
            if pattern.search(decoded_combined):
                audit("waf_block", "blocked", {"pattern": pattern.pattern})
                return jsonify({"error": "Request blocked by WAF", "trace_id": g.get("trace_id")}), 403

        allowed, retry_after = rate_limiter.check(client_key())
        if not allowed:
            audit("rate_limit", "blocked", {"retry_after_seconds": retry_after})
            response = jsonify({"error": "Too Many Requests", "retry_after_seconds": retry_after})
            response.status_code = 429
            response.headers["Retry-After"] = str(retry_after)
            return response

        return None

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


def require_api_key(required_role=None):
    def decorator(handler):
        @wraps(handler)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get("X-Api-Key", "")
            role = API_KEYS.get(api_key)

            if not role:
                audit("auth", "denied", {"reason": "missing_or_invalid_key"})
                return jsonify({"error": "Unauthorized", "message": "Missing or invalid X-Api-Key"}), 401

            if required_role and role != required_role:
                audit("auth", "denied", {"reason": "insufficient_role", "role": role})
                return jsonify({"error": "Forbidden", "message": "Insufficient role"}), 403

            g.role = role
            audit("auth", "allowed", {"role": role})
            return handler(*args, **kwargs)

        return wrapper

    return decorator
