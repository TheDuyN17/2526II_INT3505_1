"""
JWT Python Client
Demonstrates: login, token usage, auto-refresh, role-based calls, security audit
"""

import time
import json
import threading
from datetime import datetime, timezone
from typing import Optional
import urllib.request
import urllib.error
import urllib.parse
import base64

BASE_URL = "http://localhost:3000"


# ─────────────────────────────────────────────
# Token decoder (without library, just base64)
# ─────────────────────────────────────────────

def decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verifying signature (client-side inspection)."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        payload_b64 = parts[1]
        # Add padding
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_bytes)
    except Exception:
        return {}


def token_expires_in(token: str) -> float:
    """Return seconds until token expires. Negative = already expired."""
    payload = decode_jwt_payload(token)
    exp = payload.get("exp", 0)
    return exp - time.time()


# ─────────────────────────────────────────────
# HTTP Helper
# ─────────────────────────────────────────────

def http_request(method: str, path: str, data: dict = None, headers: dict = None) -> dict:
    url = BASE_URL + path
    body = json.dumps(data).encode() if data else None
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return {"status": resp.status, "body": json.loads(resp.read())}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": json.loads(e.read())}
    except Exception as ex:
        return {"status": 0, "body": {"error": str(ex)}}


# ─────────────────────────────────────────────
# JWT Client with auto-refresh
# ─────────────────────────────────────────────

class JWTClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_info: dict = {}
        self._lock = threading.Lock()

    def _auth_header(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}"}

    def login(self, username: str, password: str) -> bool:
        print(f"\n{'='*50}")
        print(f"🔑 LOGIN: {username}")
        resp = http_request("POST", "/auth/login", {"username": username, "password": password})

        if resp["status"] == 200:
            body = resp["body"]
            self.access_token = body["accessToken"]
            self.refresh_token = body["refreshToken"]
            self.user_info = body["user"]

            payload = decode_jwt_payload(self.access_token)
            exp_in = token_expires_in(self.access_token)

            print(f"  ✅ Login OK | Role: {self.user_info['role']}")
            print(f"  📦 Access Token (JWT):")
            print(f"     Header:  alg=HS256, typ=JWT")
            print(f"     Payload: sub={payload.get('sub')}, role={payload.get('role')}")
            print(f"     Expires: in {exp_in:.0f}s  ({datetime.fromtimestamp(payload.get('exp',0)).strftime('%H:%M:%S')})")
            print(f"  🔄 Refresh Token: {self.refresh_token[:40]}...")
            return True
        else:
            print(f"  ❌ Login FAILED: {resp['body']}")
            return False

    def refresh(self) -> bool:
        """Exchange refresh token for new access + refresh tokens (rotation)."""
        print(f"\n  🔄 Refreshing tokens...")
        resp = http_request("POST", "/auth/refresh", {"refreshToken": self.refresh_token})

        if resp["status"] == 200:
            body = resp["body"]
            self.access_token = body["accessToken"]
            self.refresh_token = body["refreshToken"]  # Rotated!

            exp_in = token_expires_in(self.access_token)
            print(f"  ✅ Tokens refreshed | New access token expires in {exp_in:.0f}s")
            print(f"  ℹ️  Refresh token ROTATED (old one is now invalid)")
            return True
        else:
            print(f"  ❌ Refresh FAILED: {resp['body']}")
            self.access_token = None
            self.refresh_token = None
            return False

    def ensure_valid_token(self, refresh_threshold: float = 3.0) -> bool:
        """Auto-refresh if access token expires within threshold seconds."""
        if not self.access_token:
            return False
        exp_in = token_expires_in(self.access_token)
        if exp_in < refresh_threshold:
            print(f"\n  ⚠️  Token expires in {exp_in:.0f}s — auto-refreshing...")
            return self.refresh()
        return True

    def logout(self) -> None:
        print(f"\n  🚪 Logging out...")
        resp = http_request(
            "POST", "/auth/logout",
            {"refreshToken": self.refresh_token},
            self._auth_header()
        )
        print(f"  {'✅' if resp['status'] == 200 else '❌'} {resp['body'].get('message', resp['body'])}")
        self.access_token = None
        self.refresh_token = None

    def get(self, path: str) -> dict:
        self.ensure_valid_token()
        return http_request("GET", path, headers=self._auth_header())

    def post(self, path: str, data: dict) -> dict:
        self.ensure_valid_token()
        return http_request("POST", path, data=data, headers=self._auth_header())

    def introspect(self) -> None:
        """Show token details."""
        resp = http_request("GET", "/auth/me", headers=self._auth_header())
        if resp["status"] == 200:
            b = resp["body"]
            print(f"\n  🔍 Token Introspection:")
            print(f"     User:      {b['user']['username']} ({b['user']['role']})")
            print(f"     Issued:    {b['tokenInfo']['issuedAt']}")
            print(f"     Expires:   {b['tokenInfo']['expiresAt']}")
            print(f"     JTI:       {b['tokenInfo']['jti']}")


# ─────────────────────────────────────────────
# Demo Scenarios
# ─────────────────────────────────────────────

def print_result(label: str, resp: dict) -> None:
    icon = "✅" if resp["status"] < 400 else "❌"
    print(f"\n  {icon} [{resp['status']}] {label}")
    body = resp["body"]
    if "error" in body:
        print(f"     Error: {body['error']}")
        if "hint" in body:
            print(f"     Hint:  {body['hint']}")
        if "yourRole" in body:
            print(f"     Your role: {body['yourRole']} | Required: {body.get('requiredRoles')}")
    elif "message" in body:
        print(f"     {body['message']}")


def demo_role_based_access():
    print("\n" + "━"*60)
    print("📋 DEMO 1: Role-Based Access Control")
    print("━"*60)

    # Test each role
    for username, password, role in [
        ("viewer", "viewer123", "viewer"),
        ("editor", "editor123", "editor"),
        ("admin", "admin123", "admin"),
    ]:
        client = JWTClient()
        if not client.login(username, password):
            continue

        print(f"\n  Testing API access as [{role.upper()}]:")
        print_result("GET /api/public (no auth)",
                     http_request("GET", "/api/public"))
        print_result("GET /api/data (viewer+)",
                     client.get("/api/data"))
        print_result("POST /api/data (editor+)",
                     client.post("/api/data", {"name": "Test Item"}))
        print_result("GET /api/admin/users (admin only)",
                     client.get("/api/admin/users"))


def demo_full_lifecycle_expiration():
    print("\n" + "━"*60)
    print("⏳ DEMO 2 (UPGRADE): Full Expiration Lifecycle")
    print("━"*60)
    print("  (Server keys: Access=5s, Refresh=30s)")

    client = JWTClient()
    client.login("editor", "editor123")
    
    # 1. Test Auto-refresh
    print(f"\n  [1] Testing AUTO-REFRESH:")
    print(f"      Waiting 3s (token will have < 2s left)...")
    time.sleep(3)
    # The get() call internally calls ensure_valid_token(3.0)
    resp = client.get("/api/profile")
    print_result("GET /api/profile (expected auto-refresh triggered)", resp)

    # 2. Test Hard Expiration (Force failure)
    print(f"\n  [2] Testing HARD EXPIRATION (bypassing auto-refresh):")
    print(f"      Waiting 6s...")
    time.sleep(6)
    # Use direct http_request to avoid auto-refresh logic
    resp = http_request("GET", "/api/profile", headers=client._auth_header())
    print_result("GET /api/profile (bypassing client logic)", resp)
    if resp["status"] == 401:
        print(f"      CORRECT: Server rejected expired token!")

    # 3. Test Refreshing after hard expiry
    print(f"\n  [3] Testing manual REFRESH after access token expired:")
    if client.refresh():
        print_result("GET /api/profile (with brand new tokens)", client.get("/api/profile"))

    # 4. Test Refresh Token Expiration
    print(f"\n  [4] Testing REFRESH TOKEN EXPIRY:")
    print(f"      Waiting 31s (Refresh token set to 30s)...")
    time.sleep(31) 
    print(f"      Attempting to refresh after 31s delay:")
    client.refresh() # Should fail now as refresh token is expired on server



def demo_security_audit():
    print("\n" + "━"*60)
    print("🛡️  DEMO 3: Security Audit - Token Exposure")
    print("━"*60)

    print("\n  ❌ BAD PRACTICE: Sending token in URL query string...")
    resp = http_request("GET", "/api/insecure-demo?token=fake-token-in-url")
    print(f"  Server response [{resp['status']}]:")
    body = resp["body"]
    if "issues" in body:
        print(f"  Security issues detected:")
        for issue in body["issues"]:
            print(f"    ⚠️  {issue}")
    print(f"  Fix: {body.get('fix', '')}")

    print("\n  ✅ GOOD PRACTICE: Token in Authorization header")
    client = JWTClient()
    client.login("admin", "admin123")
    print_result("GET /api/data (with proper Bearer header)", client.get("/api/data"))


def demo_logout_and_revoke():
    print("\n" + "━"*60)
    print("🚪 DEMO 4: Logout & Token Revocation")
    print("━"*60)

    client = JWTClient()
    client.login("viewer", "viewer123")

    print("\n  Accessing profile before logout:")
    print_result("GET /api/profile", client.get("/api/profile"))

    old_access_token = client.access_token
    client.logout()

    print("\n  Trying to use old access token after logout:")
    resp = http_request("GET", "/api/profile",
                        headers={"Authorization": f"Bearer {old_access_token}"})
    print_result("GET /api/profile (with revoked token)", resp)


def demo_audit_log():
    print("\n" + "━"*60)
    print("📊 DEMO 5: Security Audit Log (Admin view)")
    print("━"*60)

    client = JWTClient()
    client.login("admin", "admin123")

    resp = client.get("/api/admin/audit")
    if resp["status"] == 200:
        body = resp["body"]
        print(f"\n  Total audit events: {body['total']}")
        print(f"  Active refresh tokens: {body['activeRefreshTokens']}")
        print(f"  Blacklisted tokens: {body['blacklistedTokens']}")
        print(f"\n  Last 10 events:")
        for event in body["events"][:10]:
            ts = event["timestamp"][11:19]  # HH:MM:SS
            print(f"    [{ts}] {event['action']:<25} user={event['userId']:<5} ip={event['ip']}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  🔐 JWT Authentication Demo - Python Client")
    print("=" * 60)
    print(f"  Server: {BASE_URL}")
    print(f"  Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Quick connectivity check
        resp = http_request("GET", "/api/public")
        if resp["status"] != 200:
            raise ConnectionError()
        print(f"  ✅ Server reachable\n")
    except Exception:
        print(f"\n  ❌ Cannot connect to server at {BASE_URL}")
        print(f"  Run: cd server && node index.js")
        exit(1)

    demo_role_based_access()
    demo_full_lifecycle_expiration()
    demo_security_audit()
    demo_logout_and_revoke()
    demo_audit_log()

    print("\n" + "="*60)
    print("  ✅ All demos complete!")
    print("="*60)
