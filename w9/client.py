import requests
import time

BASE_URL = "http://localhost:5000"


def _print_section(title: str):
    print(f"\n{'=' * 55}")
    print(f"  {title}")
    print('=' * 55)


def _print_response(response: requests.Response):
    print(f"  Status : {response.status_code}")
    try:
        print(f"  Body   : {response.json()}")
    except Exception:
        print(f"  Body   : {response.text}")


def test_v1_payment_success():
    _print_section("v1 POST /payments — Success (Deprecated)")
    resp = requests.post(f"{BASE_URL}/api/v1/payments", json={"amount": 100.50, "currency": "USD"})
    _print_response(resp)
    if 'Deprecation' in resp.headers:
        print(f"\n  [DEPRECATION WARNING] {resp.headers.get('Warning')}")
        print(f"  Sunset : {resp.headers.get('Sunset')}")
        print(f"  Link   : {resp.headers.get('Link')}")


def test_v1_payment_invalid():
    _print_section("v1 POST /payments — Validation Error (missing amount)")
    resp = requests.post(f"{BASE_URL}/api/v1/payments", json={"currency": "USD"})
    _print_response(resp)


def test_v1_get_payment():
    _print_section("v1 GET /payments/<id> — Status Lookup")
    fake_id = "txn_v1_abc123"
    resp = requests.get(f"{BASE_URL}/api/v1/payments/{fake_id}")
    _print_response(resp)


def test_v2_payment_success():
    _print_section("v2 POST /payments — Success")
    payload = {
        "amount": 250.00,
        "currency": "USD",
        "user_id": "usr_987654321",
        "payment_method": "CREDIT_CARD",
    }
    resp = requests.post(f"{BASE_URL}/api/v2/payments", json=payload)
    _print_response(resp)
    return resp.json().get("data", {}).get("transaction_id")


def test_v2_payment_invalid():
    _print_section("v2 POST /payments — Validation Errors (multiple fields)")
    payload = {"amount": -50, "currency": "INVALID", "payment_method": "CASH"}
    resp = requests.post(f"{BASE_URL}/api/v2/payments", json=payload)
    _print_response(resp)


def test_v2_get_payment(transaction_id: str):
    _print_section("v2 GET /payments/<id> — Status Lookup")
    resp = requests.get(f"{BASE_URL}/api/v2/payments/{transaction_id}")
    _print_response(resp)


def test_idempotency():
    _print_section("v2 POST /payments — Idempotency Key")
    idempotency_key = f"req_unique_{int(time.time())}"
    headers = {"Idempotency-Key": idempotency_key}
    payload = {
        "amount": 500.00,
        "currency": "USD",
        "user_id": "usr_idempotent",
        "payment_method": "E_WALLET",
    }

    print(f"  Key: {idempotency_key}\n")

    print("  [Call 1 — should be MISS, status 201]")
    resp1 = requests.post(f"{BASE_URL}/api/v2/payments", json=payload, headers=headers)
    txn_id_1 = resp1.json()["data"]["transaction_id"]
    print(f"  Status : {resp1.status_code} | Cache: {resp1.headers.get('X-Idempotency-Cache')}")
    print(f"  TxnID  : {txn_id_1}")

    print("\n  [Call 2 — same key, should be HIT, status 200]")
    resp2 = requests.post(f"{BASE_URL}/api/v2/payments", json=payload, headers=headers)
    txn_id_2 = resp2.json()["data"]["transaction_id"]
    print(f"  Status : {resp2.status_code} | Cache: {resp2.headers.get('X-Idempotency-Cache')}")
    print(f"  TxnID  : {txn_id_2}")

    if txn_id_1 == txn_id_2:
        print("\n  => PASS: Idempotency is working correctly.")
    else:
        print("\n  => FAIL: Idempotency not working — transaction IDs differ.")


if __name__ == "__main__":
    try:
        time.sleep(1)

        # v1 tests
        test_v1_payment_success()
        test_v1_payment_invalid()
        test_v1_get_payment()

        # v2 tests
        txn_id = test_v2_payment_success()
        test_v2_payment_invalid()
        if txn_id:
            test_v2_get_payment(txn_id)
        test_idempotency()

        print(f"\n{'=' * 55}\n  All tests completed.\n{'=' * 55}\n")

    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to server. Run 'python server.py' first.\n")
