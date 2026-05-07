from flask import Blueprint, request, jsonify, make_response
import uuid
import time

v2_api = Blueprint('v2_api', __name__)

VALID_PAYMENT_METHODS = {'CREDIT_CARD', 'DEBIT_CARD', 'E_WALLET', 'BANK_TRANSFER'}
VALID_CURRENCIES = {'USD', 'EUR', 'VND', 'GBP'}
IDEMPOTENCY_TTL = 86400  # 24 hours in seconds

# In production, replace with Redis or a persistent store that supports TTL.
_idempotency_cache: dict[str, dict] = {}


def _validate_payment(data: dict) -> list[str]:
    errors = []
    amount = data.get('amount')
    payment_method = data.get('payment_method')
    currency = data.get('currency', 'USD')

    if amount is None:
        errors.append("'amount' is required")
    elif not isinstance(amount, (int, float)) or amount <= 0:
        errors.append("'amount' must be a positive number")

    if not data.get('user_id'):
        errors.append("'user_id' is required")

    if not payment_method:
        errors.append("'payment_method' is required")
    elif payment_method not in VALID_PAYMENT_METHODS:
        errors.append(f"'payment_method' must be one of: {sorted(VALID_PAYMENT_METHODS)}")

    if currency not in VALID_CURRENCIES:
        errors.append(f"'currency' must be one of: {sorted(VALID_CURRENCIES)}")

    return errors


def _build_response_data(data: dict, idempotency_key: str | None) -> dict:
    return {
        "data": {
            "transaction_id": str(uuid.uuid4()),
            "status": "COMPLETED",
            "amount": data['amount'],
            "currency": data.get('currency', 'USD'),
            "payment_method": data['payment_method'],
            "user_id": data['user_id'],
            "timestamp": int(time.time()),
        },
        "meta": {
            "api_version": "v2",
            "idempotency_key": idempotency_key,
        },
    }


@v2_api.route('/payments', methods=['POST'])
def process_payment():
    idempotency_key = request.headers.get('Idempotency-Key')

    # Return cached result if idempotency key was seen recently
    if idempotency_key and idempotency_key in _idempotency_cache:
        entry = _idempotency_cache[idempotency_key]
        if time.time() - entry['cached_at'] < IDEMPOTENCY_TTL:
            resp = make_response(jsonify(entry['response']), 200)
            resp.headers['X-Idempotency-Cache'] = 'HIT'
            return resp
        del _idempotency_cache[idempotency_key]

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Validation Failed", "details": ["Request body must be valid JSON"]}), 400

    errors = _validate_payment(data)
    if errors:
        return jsonify({"error": "Validation Failed", "details": errors}), 400

    response_data = _build_response_data(data, idempotency_key)

    if idempotency_key:
        _idempotency_cache[idempotency_key] = {
            'response': response_data,
            'cached_at': time.time(),
        }

    resp = make_response(jsonify(response_data), 201)
    if idempotency_key:
        resp.headers['X-Idempotency-Cache'] = 'MISS'

    return resp


@v2_api.route('/payments/<transaction_id>', methods=['GET'])
def get_payment(transaction_id):
    """Simulated payment status lookup by transaction ID."""
    return jsonify({
        "data": {
            "transaction_id": transaction_id,
            "status": "COMPLETED",
            "note": "This is a simulated status response.",
        },
        "meta": {"api_version": "v2"},
    }), 200
