# coding: utf-8
"""
Entry point để chạy server bằng lệnh: python -m openapi_server

Quy trình khởi động:
1. Load biến môi trường từ file .env
2. Khởi tạo Connexion app + load openapi.yaml
3. Kết nối MongoDB (có retry logic)
4. Chạy server trên PORT (mặc định 8080)
"""

import os

# Load .env TRƯỚC khi import app để đảm bảo env vars đã sẵn sàng
from dotenv import load_dotenv

load_dotenv()

from openapi_server.main import app  # noqa: E402 — phải import sau load_dotenv


def main():
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_ENV") == "development"
    print(f"[Server] Starting on http://0.0.0.0:{port}")
    print(f"[Server] Swagger UI: http://localhost:{port}/api/ui/")
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
