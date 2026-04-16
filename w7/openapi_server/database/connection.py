# coding: utf-8
"""
Quản lý kết nối MongoDB.

Sử dụng singleton pattern: chỉ tạo một MongoClient duy nhất cho toàn app.
Có retry logic để xử lý trường hợp MongoDB chưa khởi động xong (đặc biệt khi dùng Docker).
"""

import os
import time
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# ── Cấu hình retry ──────────────────────────────────────────────────────────
MAX_RETRIES = 5       # Số lần thử kết nối tối đa
RETRY_DELAY = 2       # Giây chờ giữa các lần thử
CONN_TIMEOUT_MS = 5000  # Timeout mỗi lần thử (ms)

# ── Singleton state ──────────────────────────────────────────────────────────
_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def _extract_db_name(uri: str) -> str:
    """Lấy tên database từ URI. Fallback về 'product_db' nếu không có."""
    try:
        # mongodb://host:port/dbname?params  hoặc  mongodb+srv://...host/dbname
        path = uri.rsplit("/", 1)[-1]
        db_name = path.split("?")[0].strip()
        return db_name if db_name else "product_db"
    except Exception:
        return "product_db"


def _create_indexes(db: Database) -> None:
    """Tạo các index để tối ưu truy vấn phổ biến."""
    col = db["products"]
    col.create_index([("name", "text")])   # Full-text search theo tên
    col.create_index("category")            # Filter theo category
    col.create_index("is_active")           # Filter theo trạng thái
    col.create_index("price")               # Sort theo giá
    col.create_index([("created_at", -1)])  # Sort theo ngày tạo (mặc định)
    print("[DB] Indexes created/verified.")


def init_db() -> None:
    """
    Khởi tạo kết nối MongoDB với retry logic.

    Tự động thử lại tối đa MAX_RETRIES lần nếu kết nối thất bại.
    Raise RuntimeError nếu vẫn không kết nối được sau tất cả các lần thử.
    """
    global _client, _db

    uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/product_db")
    db_name = _extract_db_name(uri)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[DB] Connecting to MongoDB (attempt {attempt}/{MAX_RETRIES})...")
            client = MongoClient(uri, serverSelectionTimeoutMS=CONN_TIMEOUT_MS)

            # Kiểm tra kết nối thực sự bằng ping
            client.admin.command("ping")

            _client = client
            _db = _client[db_name]
            _create_indexes(_db)
            print(f"[DB] Connected successfully: {db_name}")
            return

        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            print(f"[DB] Attempt {attempt} failed: {exc}")
            if attempt < MAX_RETRIES:
                print(f"[DB] Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)

    raise RuntimeError(
        f"Cannot connect to MongoDB after {MAX_RETRIES} attempts. "
        f"Check MONGODB_URI: {uri}"
    )


def get_database() -> Database:
    """
    Trả về database instance hiện tại.

    Raise RuntimeError nếu init_db() chưa được gọi.
    """
    if _db is None:
        raise RuntimeError(
            "Database chưa được khởi tạo. Hãy gọi init_db() trước."
        )
    return _db


def close_db() -> None:
    """Đóng kết nối MongoDB (dùng khi shutdown hoặc trong tests)."""
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        print("[DB] Connection closed.")
