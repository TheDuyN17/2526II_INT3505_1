from __future__ import annotations

from flask import Flask, jsonify, render_template_string

try:
    from flasgger import Swagger
except ImportError:
    Swagger = None

try:
    from .openapi import OPENAPI_SPEC
except ImportError:
    from openapi import OPENAPI_SPEC


BUSINESS_MODEL_CANVAS = {
    "customer_segments": [
        "Student developers building learning and tutoring integrations",
        "Education platforms that need tutor search, booking, and payment APIs",
        "Internal product teams that need stable API contracts for frontend apps",
    ],
    "value_propositions": [
        "A documented education API with sandbox data and clear examples",
        "Faster integration through predictable REST endpoints and OpenAPI docs",
        "Operational visibility through usage, error, and developer KPIs",
    ],
    "channels": [
        "Developer portal",
        "Swagger/OpenAPI documentation",
        "GitHub examples and quickstart guides",
    ],
    "customer_relationships": [
        "Self-service onboarding",
        "Sandbox support for testing before production access",
        "Changelog and deprecation notices for lifecycle management",
    ],
    "revenue_streams": [
        "Freemium tier for learning and prototypes",
        "Pay-per-call for production traffic",
        "Team plan with higher quota, analytics export, and priority support",
    ],
    "key_resources": [
        "API gateway and backend services",
        "OpenAPI specification and developer documentation",
        "Analytics pipeline for usage and error tracking",
    ],
    "key_activities": [
        "Publish docs, SDK examples, and sandbox credentials",
        "Track developer activation, call volume, latency, and error rate",
        "Manage pricing tiers, quotas, versioning, and deprecation policy",
    ],
    "key_partners": [
        "Payment provider",
        "Cloud hosting and monitoring provider",
        "University and education content partners",
    ],
    "cost_structure": [
        "Cloud compute, database, logging, and monitoring",
        "Developer support and documentation maintenance",
        "Security review and compliance work",
    ],
}


LAUNCH_STRATEGY = {
    "phase_1": {
        "name": "Private beta",
        "actions": [
            "Invite a small group of developers",
            "Provide sandbox API keys and fake data",
            "Collect feedback on docs, examples, and error messages",
        ],
    },
    "phase_2": {
        "name": "Public developer portal",
        "actions": [
            "Publish quickstart, endpoint docs, and pricing",
            "Add changelog, status page, and support contact",
            "Measure sign-up to first successful API call conversion",
        ],
    },
    "phase_3": {
        "name": "Monetization and lifecycle",
        "actions": [
            "Enable freemium and pay-per-call plans",
            "Add quota alerts and analytics dashboard",
            "Document versioning, migration, and deprecation policy",
        ],
    },
}


PRICING_PLANS = [
    {
        "name": "Free",
        "price": "$0",
        "quota": "1,000 calls/month",
        "best_for": "Learning, demos, and prototypes",
        "features": ["Sandbox access", "Public docs", "Community support"],
    },
    {
        "name": "Growth",
        "price": "$19/month + $0.002/call over quota",
        "quota": "50,000 calls/month",
        "best_for": "Small production integrations",
        "features": ["Production API key", "Email support", "Usage analytics"],
    },
    {
        "name": "Scale",
        "price": "Custom",
        "quota": "Custom quota",
        "best_for": "Teams with high traffic or SLA needs",
        "features": ["SLA", "Analytics export", "Priority support"],
    },
]


KPI_SNAPSHOT = {
    "registered_developers": 128,
    "active_developers_30d": 42,
    "call_volume_30d": 184250,
    "error_rate_30d": 0.012,
    "p95_latency_ms": 180,
    "first_call_conversion_rate": 0.64,
}


PORTAL_TEMPLATE = """
<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Edu API Developer Portal</title>
    <style>
      :root {
        color-scheme: light;
        --ink: #18212f;
        --muted: #5e6878;
        --line: #d9dee7;
        --panel: #ffffff;
        --accent: #147a73;
        --accent-dark: #0d5550;
        --soft: #eef7f5;
        --warn: #8a5a00;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--ink);
        background: #f6f8fb;
        line-height: 1.5;
      }
      header {
        border-bottom: 1px solid var(--line);
        background: #fff;
        position: sticky;
        top: 0;
        z-index: 10;
      }
      nav {
        max-width: 1120px;
        margin: 0 auto;
        padding: 14px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
      }
      .brand {
        font-weight: 750;
        font-size: 18px;
      }
      .nav-links {
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
      }
      .nav-links a {
        color: var(--muted);
        text-decoration: none;
        font-size: 14px;
      }
      main { max-width: 1120px; margin: 0 auto; padding: 34px 20px 56px; }
      .hero {
        display: grid;
        grid-template-columns: minmax(0, 1.35fr) minmax(280px, .65fr);
        gap: 28px;
        align-items: start;
        padding: 24px 0 34px;
      }
      h1 {
        font-size: clamp(32px, 5vw, 58px);
        line-height: 1.03;
        margin: 0 0 18px;
        letter-spacing: 0;
      }
      h2 { margin: 0 0 14px; font-size: 24px; letter-spacing: 0; }
      h3 { margin: 0 0 8px; font-size: 17px; letter-spacing: 0; }
      p { margin: 0 0 14px; color: var(--muted); }
      .actions { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 22px; }
      .button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 42px;
        padding: 0 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 650;
        border: 1px solid var(--accent);
      }
      .primary { background: var(--accent); color: white; }
      .secondary { color: var(--accent-dark); background: white; }
      .metrics {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
      }
      .metric, .card, .canvas-cell, pre {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
      }
      .metric { padding: 14px; min-height: 94px; }
      .metric strong { display: block; font-size: 26px; color: var(--accent-dark); }
      .metric span { color: var(--muted); font-size: 13px; }
      section { padding: 30px 0; border-top: 1px solid var(--line); }
      .grid-3 {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
      }
      .card { padding: 18px; }
      .card ul, .canvas-cell ul { margin: 10px 0 0; padding-left: 18px; color: var(--muted); }
      .canvas {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
      }
      .canvas-cell { padding: 14px; min-height: 180px; }
      .sandbox {
        display: grid;
        grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr);
        gap: 18px;
      }
      code, pre {
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
        font-size: 13px;
      }
      pre {
        margin: 0;
        padding: 16px;
        overflow: auto;
        color: #d7e8e5;
        background: #102522;
      }
      .tag {
        display: inline-block;
        padding: 3px 8px;
        border: 1px solid #acd5d0;
        border-radius: 999px;
        color: var(--accent-dark);
        background: var(--soft);
        font-size: 12px;
        font-weight: 650;
        margin-bottom: 10px;
      }
      @media (max-width: 800px) {
        .hero, .sandbox { grid-template-columns: 1fr; }
        .grid-3, .canvas { grid-template-columns: 1fr; }
        .metrics { grid-template-columns: 1fr; }
        nav { align-items: flex-start; flex-direction: column; }
      }
    </style>
  </head>
  <body>
    <header>
      <nav>
        <div class="brand">Edu API Developer Portal</div>
        <div class="nav-links">
          <a href="#quickstart">Quickstart</a>
          <a href="#pricing">Pricing</a>
          <a href="#analytics">Analytics</a>
          <a href="#canvas">Business model</a>
          <a href="/apidocs/">Swagger</a>
        </div>
      </nav>
    </header>
    <main>
      <div class="hero">
        <div>
          <span class="tag">API as a Product</span>
          <h1>Build education integrations with a clear sandbox, pricing, and product metrics.</h1>
          <p>
            Portal này mô phỏng cách đóng gói API thành sản phẩm: developer experience,
            launch strategy, monetization model, analytics và KPI vận hành.
          </p>
          <div class="actions">
            <a class="button primary" href="/api/sandbox">Open sandbox JSON</a>
            <a class="button secondary" href="/apidocs/">Swagger docs</a>
            <a class="button secondary" href="/api/business-model">Business canvas API</a>
          </div>
        </div>
        <div class="metrics" id="analytics">
          <div class="metric"><strong>{{ metrics.registered_developers }}</strong><span>registered developers</span></div>
          <div class="metric"><strong>{{ metrics.active_developers_30d }}</strong><span>active developers in 30 days</span></div>
          <div class="metric"><strong>{{ metrics.call_volume_30d }}</strong><span>calls in 30 days</span></div>
          <div class="metric"><strong>{{ "%.2f"|format(metrics.error_rate_30d * 100) }}%</strong><span>30-day error rate</span></div>
        </div>
      </div>

      <section id="quickstart">
        <h2>Launch Strategy</h2>
        <div class="grid-3">
          {% for phase in launch.values() %}
          <article class="card">
            <h3>{{ phase.name }}</h3>
            <ul>
              {% for action in phase.actions %}<li>{{ action }}</li>{% endfor %}
            </ul>
          </article>
          {% endfor %}
        </div>
      </section>

      <section class="sandbox">
        <div>
          <h2>Sandbox Experience</h2>
          <p>
            Developer mới cần nhìn thấy base URL, API key mẫu, endpoint chính và response
            dự kiến trước khi đăng ký production key.
          </p>
          <p><strong>Base URL:</strong> <code>http://127.0.0.1:5014/api</code></p>
          <p><strong>Sandbox key:</strong> <code>edu_sandbox_demo_key</code></p>
        </div>
        <pre><code>curl http://127.0.0.1:5014/api/sandbox \
  -H "Authorization: Bearer edu_sandbox_demo_key"</code></pre>
      </section>

      <section id="pricing">
        <h2>Monetization Model</h2>
        <div class="grid-3">
          {% for plan in pricing %}
          <article class="card">
            <h3>{{ plan.name }}</h3>
            <p><strong>{{ plan.price }}</strong></p>
            <p>{{ plan.quota }}</p>
            <p>{{ plan.best_for }}</p>
            <ul>{% for feature in plan.features %}<li>{{ feature }}</li>{% endfor %}</ul>
          </article>
          {% endfor %}
        </div>
      </section>

      <section id="canvas">
        <h2>Business Model Canvas</h2>
        <div class="canvas">
          {% for key, values in canvas.items() %}
          <article class="canvas-cell">
            <h3>{{ key.replace("_", " ").title() }}</h3>
            <ul>{% for item in values %}<li>{{ item }}</li>{% endfor %}</ul>
          </article>
          {% endfor %}
        </div>
      </section>
    </main>
  </body>
</html>
"""


def register_swagger(app: Flask) -> None:
    if Swagger is not None:
        Swagger(app, template=OPENAPI_SPEC)
        return

    @app.get("/apispec_1.json")
    def openapi_json():
        return jsonify(OPENAPI_SPEC), 200

    @app.get("/apidocs/")
    def swagger_fallback():
        return render_template_string(
            """
            <!doctype html>
            <html lang="vi">
              <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Week13 Swagger Docs</title>
                <style>
                  body {
                    margin: 0;
                    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    color: #18212f;
                    background: #f6f8fb;
                  }
                  main { max-width: 880px; margin: 0 auto; padding: 48px 20px; }
                  h1 { margin: 0 0 12px; font-size: 36px; letter-spacing: 0; }
                  p { color: #5e6878; line-height: 1.55; }
                  a { color: #0d5550; font-weight: 700; }
                  pre {
                    margin-top: 22px;
                    padding: 16px;
                    overflow: auto;
                    border-radius: 8px;
                    color: #d7e8e5;
                    background: #102522;
                  }
                </style>
              </head>
              <body>
                <main>
                  <h1>Week13 Swagger Docs</h1>
                  <p>
                    OpenAPI spec is available at <a href="/apispec_1.json">/apispec_1.json</a>.
                    Install dependencies from <code>requirements.txt</code> to enable the full Swagger UI.
                  </p>
                  <pre><code>python3 -m pip install -r requirements.txt</code></pre>
                </main>
              </body>
            </html>
            """
        ), 200


def create_app() -> Flask:
    app = Flask(__name__)
    register_swagger(app)

    @app.get("/")
    def home():
        return jsonify(
            {
                "message": "Week13 API as a Product is running",
                "developer_portal": "/portal",
                "swagger_docs": "/apidocs/",
                "openapi_json": "/apispec_1.json",
                "business_model_canvas": "/api/business-model",
                "kpis": "/api/metrics",
                "pricing": "/api/pricing",
                "sandbox": "/api/sandbox",
            }
        ), 200

    @app.get("/portal")
    def portal():
        return render_template_string(
            PORTAL_TEMPLATE,
            canvas=BUSINESS_MODEL_CANVAS,
            launch=LAUNCH_STRATEGY,
            pricing=PRICING_PLANS,
            metrics=KPI_SNAPSHOT,
        ), 200

    @app.get("/api/business-model")
    def business_model():
        return jsonify({"canvas": BUSINESS_MODEL_CANVAS}), 200

    @app.get("/api/launch-strategy")
    def launch_strategy():
        return jsonify({"strategy": LAUNCH_STRATEGY}), 200

    @app.get("/api/pricing")
    def pricing():
        return jsonify({"plans": PRICING_PLANS}), 200

    @app.get("/api/metrics")
    def metrics():
        return jsonify({"kpis": KPI_SNAPSHOT}), 200

    @app.get("/api/sandbox")
    def sandbox():
        return jsonify(
            {
                "environment": "sandbox",
                "base_url": "http://127.0.0.1:5014/api",
                "api_key": "edu_sandbox_demo_key",
                "sample_endpoints": [
                    {"method": "GET", "path": "/api/metrics", "purpose": "Read KPI snapshot"},
                    {"method": "GET", "path": "/api/pricing", "purpose": "Read pricing plans"},
                    {
                        "method": "GET",
                        "path": "/api/business-model",
                        "purpose": "Read business model canvas",
                    },
                ],
            }
        ), 200

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Route not found"}), 404

    return app
