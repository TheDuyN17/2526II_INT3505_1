#!/usr/bin/env python3
"""
Script seed dữ liệu mẫu cho Product Management API.

Chèn 12 sản phẩm mẫu thuộc đủ 5 categories: Electronics, Clothing, Books, Food, Sports.
Tự động bỏ qua nếu collection đã có dữ liệu (idempotent).

Cách chạy:
    python seed/seed.py
    # Hoặc với URI khác:
    MONGODB_URI=mongodb+srv://... python seed/seed.py
"""

import os
import sys
from datetime import datetime, timezone

# Hỗ trợ chạy từ thư mục gốc hoặc từ thư mục seed/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/product_db")

# ── Dữ liệu mẫu — 12 sản phẩm, 5 categories ─────────────────────────────────

SAMPLE_PRODUCTS = [
    # Electronics (4)
    {
        "name": "MacBook Pro 16",
        "description": "Apple M3 Pro chip, 18GB unified memory, 512GB SSD. Lý tưởng cho lập trình viên và designer.",
        "price": 2499.99,
        "category": "Electronics",
        "stock": 25,
        "image_url": "https://example.com/macbook-pro-16.jpg",
        "is_active": True,
    },
    {
        "name": "iPhone 15 Pro Max",
        "description": "A17 Pro chip, 256GB, khung Titanium. Camera 48MP với zoom quang 5x.",
        "price": 1199.99,
        "category": "Electronics",
        "stock": 60,
        "image_url": "https://example.com/iphone-15-pro-max.jpg",
        "is_active": True,
    },
    {
        "name": "Sony WH-1000XM5",
        "description": "Tai nghe không dây chống ồn hàng đầu. Pin 30h, kết nối multipoint.",
        "price": 349.99,
        "category": "Electronics",
        "stock": 45,
        "image_url": "https://example.com/sony-xm5.jpg",
        "is_active": True,
    },
    {
        "name": "Samsung 4K OLED TV 55\"",
        "description": "Smart TV 55 inch OLED 4K, 120Hz, HDR10+, tích hợp Google TV.",
        "price": 1599.99,
        "category": "Electronics",
        "stock": 15,
        "image_url": "https://example.com/samsung-oled-55.jpg",
        "is_active": False,  # Hết hàng tạm thời
    },
    # Clothing (2)
    {
        "name": "Levi's 501 Original Jeans",
        "description": "Quần jeans classic straight fit, 100% cotton denim, size 32x32.",
        "price": 79.99,
        "category": "Clothing",
        "stock": 150,
        "image_url": "https://example.com/levis-501.jpg",
        "is_active": True,
    },
    {
        "name": "Uniqlo Ultra Light Down Jacket",
        "description": "Áo phao siêu nhẹ, gấp gọn vào túi, giữ ấm đến -10°C. Size L.",
        "price": 89.99,
        "category": "Clothing",
        "stock": 80,
        "image_url": "https://example.com/uniqlo-down-jacket.jpg",
        "is_active": True,
    },
    # Books (2)
    {
        "name": "Clean Code",
        "description": "A Handbook of Agile Software Craftsmanship — Robert C. Martin. Must-read cho mọi lập trình viên.",
        "price": 39.99,
        "category": "Books",
        "stock": 200,
        "image_url": "https://example.com/clean-code.jpg",
        "is_active": True,
    },
    {
        "name": "Designing Data-Intensive Applications",
        "description": "The Big Ideas Behind Reliable, Scalable, and Maintainable Systems — Martin Kleppmann.",
        "price": 49.99,
        "category": "Books",
        "stock": 120,
        "image_url": "https://example.com/ddia.jpg",
        "is_active": True,
    },
    # Food (2)
    {
        "name": "Matcha Organic Green Tea 200g",
        "description": "Matcha Nhật Bản ceremonial grade, 100% organic, không chất bảo quản.",
        "price": 24.99,
        "category": "Food",
        "stock": 300,
        "image_url": "https://example.com/matcha-organic.jpg",
        "is_active": True,
    },
    {
        "name": "Premium Dark Chocolate 85% 500g",
        "description": "Socola đen cao cấp 85% cacao từ Ecuador, không đường tinh luyện.",
        "price": 18.99,
        "category": "Food",
        "stock": 250,
        "image_url": "https://example.com/dark-chocolate.jpg",
        "is_active": True,
    },
    # Sports (2)
    {
        "name": "Nike Air Zoom Pegasus 41",
        "description": "Giày chạy bộ đa năng, đệm React Foam, trọng lượng 280g, size 42.",
        "price": 129.99,
        "category": "Sports",
        "stock": 95,
        "image_url": "https://example.com/nike-pegasus-41.jpg",
        "is_active": True,
    },
    {
        "name": "Yoga Mat Pro 6mm TPE",
        "description": "Thảm yoga chống trượt 6mm, chất liệu TPE thân thiện môi trường, kèm dây buộc.",
        "price": 49.99,
        "category": "Sports",
        "stock": 70,
        "image_url": "https://example.com/yoga-mat-pro.jpg",
        "is_active": True,
    },
]


def seed():
    """Kết nối MongoDB và chèn dữ liệu mẫu."""
    print(f"[Seed] Connecting to: {MONGODB_URI[:40]}...")

    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")  # Kiểm tra kết nối
    except Exception as exc:
        print(f"[Seed] ERROR: Không thể kết nối MongoDB — {exc}")
        sys.exit(1)

    # Lấy tên database từ URI
    db_name = MONGODB_URI.rsplit("/", 1)[-1].split("?")[0].strip() or "product_db"
    db = client[db_name]
    col = db["products"]

    # Kiểm tra nếu đã có dữ liệu thì bỏ qua
    existing = col.count_documents({})
    if existing > 0:
        print(f"[Seed] Collection '{db_name}.products' đã có {existing} documents — bỏ qua.")
        client.close()
        return

    # Thêm timestamps
    now = datetime.now(timezone.utc)
    docs = [{**p, "created_at": now, "updated_at": now} for p in SAMPLE_PRODUCTS]

    result = col.insert_many(docs)
    print(f"[Seed] Đã chèn {len(result.inserted_ids)} products vào '{db_name}.products'.")

    # Tạo text index cho search
    col.create_index([("name", "text")])
    print("[Seed] Text index đã được tạo.")

    client.close()
    print("[Seed] Hoàn tất!")


if __name__ == "__main__":
    seed()
