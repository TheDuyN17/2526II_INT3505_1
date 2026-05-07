from flask import Flask, jsonify
from v1 import v1_api
from v2 import v2_api

app = Flask(__name__)

app.register_blueprint(v1_api, url_prefix='/api/v1')
app.register_blueprint(v2_api, url_prefix='/api/v2')


@app.route('/')
def index():
    return jsonify({
        "service": "Payment API",
        "status": "operational",
        "versions": {
            "v1": {
                "status": "deprecated",
                "endpoint": "/api/v1/payments",
                "sunset": "2026-12-31",
            },
            "v2": {
                "status": "active",
                "endpoint": "/api/v2/payments",
            },
        },
        "migration_guide": "See DEPRECATION_NOTICE.md for upgrade instructions",
    })


@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found", "message": str(e)}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method Not Allowed", "message": str(e)}), 405


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
