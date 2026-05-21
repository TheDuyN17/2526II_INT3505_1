import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path

from flask import g, request
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from werkzeug.exceptions import HTTPException


LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        extra_fields = getattr(record, "extra_fields", None)
        if extra_fields:
            payload.update(extra_fields)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def build_logger(name, file_name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = JsonFormatter()

    if os.getenv("LOG_TO_FILE", "false").lower() == "true":
        file_handler = logging.FileHandler(LOG_DIR / file_name)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


app_logger = build_logger("lecture_10.app", "app.log")
audit_logger = build_logger("lecture_10.audit", "audit.log")


class MetricsStore:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.http_requests = Counter(
            "flask_http_requests_total",
            "Total HTTP requests.",
            ["method", "path", "status"],
            registry=self.registry,
        )
        self.http_request_duration = Histogram(
            "flask_http_request_duration_seconds",
            "HTTP request duration in seconds.",
            ["method", "path", "status"],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
            registry=self.registry,
        )
        self.security_events = Counter(
            "security_events_total",
            "Total blocked or audited security events.",
            ["type"],
            registry=self.registry,
        )
        self.circuit_breaker_open = Gauge(
            "circuit_breaker_open",
            "Circuit breaker state, 1 is open and 0 is closed.",
            registry=self.registry,
        )

    def record_request(self, method, path, status_code, duration_seconds):
        labels = (method, path, str(status_code))
        self.http_requests.labels(*labels).inc()
        self.http_request_duration.labels(*labels).observe(duration_seconds)

    def record_security_event(self, event_type):
        self.security_events.labels(event_type).inc()

    def set_circuit_breaker_open(self, is_open):
        self.circuit_breaker_open.set(1 if is_open else 0)

    def render_prometheus(self):
        return generate_latest(self.registry)


metrics = MetricsStore()


def get_trace_id():
    traceparent = request.headers.get("traceparent", "")
    parts = traceparent.split("-")
    if len(parts) >= 2 and len(parts[1]) == 32:
        return parts[1]

    try:
        from opentelemetry import trace

        span_context = trace.get_current_span().get_span_context()
        if span_context.is_valid:
            return format(span_context.trace_id, "032x")
    except Exception:
        pass

    return request.headers.get("X-Request-Id") or uuid.uuid4().hex


def setup_tracing(app):
    if os.getenv("OTEL_SDK_DISABLED", "false").lower() == "true":
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        app_logger.warning("opentelemetry_not_installed")
        return

    if getattr(app, "_otel_tracing_configured", False):
        return

    service_name = os.getenv("OTEL_SERVICE_NAME", "lecture-10-api")
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FlaskInstrumentor().instrument_app(app)
    app._otel_tracing_configured = True


def setup_observability(app):
    setup_tracing(app)

    @app.before_request
    def start_request_trace():
        g.started_at = time.perf_counter()
        g.trace_id = get_trace_id()

    @app.after_request
    def record_request_metrics(response):
        duration = time.perf_counter() - g.get("started_at", time.perf_counter())
        route = request.url_rule.rule if request.url_rule else request.path

        metrics.record_request(request.method, route, response.status_code, duration)
        response.headers["X-Request-Id"] = g.get("trace_id", "")

        app_logger.info(
            "request_completed",
            extra={
                "extra_fields": {
                    "trace_id": g.get("trace_id"),
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "remote_addr": request.remote_addr,
                    "user_agent": request.headers.get("User-Agent", ""),
                }
            },
        )

        return response

    @app.errorhandler(Exception)
    def log_unhandled_exception(error):
        if isinstance(error, HTTPException):
            return {"error": error.name, "message": error.description, "trace_id": g.get("trace_id")}, error.code

        app_logger.exception(
            "unhandled_exception",
            extra={
                "extra_fields": {
                    "trace_id": g.get("trace_id"),
                    "method": request.method,
                    "path": request.path,
                }
            },
        )
        return {"error": "Internal Server Error", "trace_id": g.get("trace_id")}, 500
