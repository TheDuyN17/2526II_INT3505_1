from flask import Blueprint, request, jsonify, make_response
import uuid

v1_api = Blueprint('v1_api', __name__)

VALID_CURRENCIES = {'USD', 'EUR', 'VND', 'GBP'}

# Shared deprecation headers per RFC 8594
_DEPRECATION_HEADERS = {
    'Deprecation': 'Thu, 07 May 2026 00:00:00 GMT',
    'Sunset': 'Thu, 31 Dec 2026 23:59:59 GMT',
    'Link': '</api/v2/payments>; rel="successor-version"',
    'Warning': '299 - "This API version is deprecated and will be removed on 2026-12-31. Please migrate to /api/v2/payments"',
}

def _apply_deprecation_headers(response):
    for key, value in _DEPRECATION_HEADERS.items():
        response.headers[key] = value
    return response


@v1_api.route('/payments', methods=['POST'])
def process_payment():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    amount = data.get('amount')
    currency = data.get('currency', 'USD')

    if amount is None:
        return jsonify({"error": "Missing required field: 'amount'"}), 400
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Field 'amount' must be a positive number"}), 400
    if currency not in VALID_CURRENCIES:
        return jsonify({"error": f"Invalid currency. Supported values: {sorted(VALID_CURRENCIES)}"}), 400

    response_data = {
        "status": "success",
        "message": f"Successfully processed payment of {amount} {currency}",
        "transaction_id": str(uuid.uuid4()),
    }

    response = make_response(jsonify(response_data), 200)
    return _apply_deprecation_headers(response)


@v1_api.route('/payments/<transaction_id>', methods=['GET'])
def get_payment(transaction_id):
    """Simulated status lookup — limited functionality compared to v2."""
    response_data = {
        "status": "success",
        "transaction_id": transaction_id,
        "note": "Status lookup is limited in v1. Migrate to v2 for full transaction details.",
    }
    response = make_response(jsonify(response_data), 200)
    return _apply_deprecation_headers(response)
