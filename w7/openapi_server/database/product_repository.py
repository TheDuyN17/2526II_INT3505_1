# coding: utf-8
"""
Repository layer cho Product resource.

Tách biệt hoàn toàn logic truy vấn MongoDB khỏi controller,
theo pattern Repository (Data Access Object).
"""

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database


class ProductRepository:
    """
    Thực hiện tất cả các thao tác CRUD với collection 'products'.

    Mỗi method nhận/trả dicts thuần Python (không phải Mongo documents).
    _id của MongoDB được chuyển thành 'id' (string) khi trả về.
    """

    COLLECTION = "products"

    def __init__(self, db: Database):
        self.col = db[self.COLLECTION]

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def is_valid_id(oid: str) -> bool:
        """Kiểm tra chuỗi có phải MongoDB ObjectId hợp lệ không."""
        try:
            ObjectId(oid)
            return True
        except (InvalidId, TypeError):
            return False

    @staticmethod
    def _doc_to_dict(doc: Optional[dict]) -> Optional[dict]:
        """Chuyển MongoDB document -> API dict (thay _id bằng id string)."""
        if doc is None:
            return None
        result = dict(doc)
        result["id"] = str(result.pop("_id"))
        # Chuyển datetime -> ISO string cho JSON serialization
        for field in ("created_at", "updated_at"):
            if isinstance(result.get(field), datetime):
                result[field] = result[field].isoformat()
        return result

    @staticmethod
    def _build_sort(sort_str: str) -> Tuple[str, int]:
        """
        Chuyển chuỗi 'field:direction' thành tuple (field, direction).
        Ví dụ: 'price:asc' -> ('price', ASCENDING)
        """
        parts = sort_str.split(":")
        field = parts[0].strip() if parts[0].strip() else "created_at"
        direction = ASCENDING if len(parts) > 1 and parts[1].strip() == "asc" else DESCENDING
        return field, direction

    # ── CRUD methods ─────────────────────────────────────────────────────────

    def find_all(
        self,
        page: int = 1,
        limit: int = 10,
        sort: str = "created_at:desc",
        filters: Optional[Dict] = None,
    ) -> Tuple[List[dict], int]:
        """
        Lấy danh sách products với pagination, sorting, và filtering.

        Args:
            page: Số trang (bắt đầu từ 1)
            limit: Số items mỗi trang
            sort: Chuỗi sort theo format 'field:asc|desc'
            filters: Dict chứa các điều kiện lọc bổ sung

        Returns:
            Tuple (danh sách products, tổng số documents khớp)
        """
        query: Dict = {}

        # Áp dụng filters từ query params
        if filters:
            if "category" in filters and filters["category"]:
                query["category"] = filters["category"]
            if "is_active" in filters and filters["is_active"] is not None:
                query["is_active"] = filters["is_active"]
            if "search" in filters and filters["search"]:
                # Sử dụng MongoDB text search (cần text index trên 'name')
                query["$text"] = {"$search": filters["search"]}

        sort_field, sort_dir = self._build_sort(sort)
        skip = (max(1, page) - 1) * limit

        # Đếm tổng để tính pagination (chạy song song với query chính)
        total = self.col.count_documents(query)
        cursor = self.col.find(query).sort(sort_field, sort_dir).skip(skip).limit(limit)

        products = [self._doc_to_dict(doc) for doc in cursor]
        return products, total

    def find_by_id(self, product_id: str) -> Optional[dict]:
        """
        Tìm một product theo ObjectId.

        Returns:
            Product dict hoặc None nếu không tìm thấy
        """
        doc = self.col.find_one({"_id": ObjectId(product_id)})
        return self._doc_to_dict(doc)

    def create(self, data: dict) -> dict:
        """
        Tạo product mới.

        Tự động thêm created_at, updated_at và giá trị mặc định.

        Returns:
            Product dict đã được lưu (bao gồm id)
        """
        now = datetime.now(timezone.utc)

        # Lọc bỏ các trường read-only nếu client vô tình gửi lên
        doc = {k: v for k, v in data.items() if k not in ("id", "created_at", "updated_at")}

        # Áp dụng giá trị mặc định theo OpenAPI spec
        doc.setdefault("stock", 0)
        doc.setdefault("is_active", True)
        doc["created_at"] = now
        doc["updated_at"] = now

        result = self.col.insert_one(doc)
        return self._doc_to_dict(self.col.find_one({"_id": result.inserted_id}))

    def update(self, product_id: str, data: dict) -> Optional[dict]:
        """
        Thay thế hoàn toàn một product (PUT — full replacement).

        Giữ lại created_at gốc, cập nhật updated_at mới.

        Returns:
            Product dict sau khi cập nhật, hoặc None nếu không tìm thấy
        """
        existing = self.col.find_one({"_id": ObjectId(product_id)})
        if existing is None:
            return None

        now = datetime.now(timezone.utc)
        doc = {k: v for k, v in data.items() if k not in ("id", "created_at", "updated_at")}
        doc.setdefault("stock", 0)
        doc.setdefault("is_active", True)
        # Giữ nguyên created_at của document gốc
        doc["created_at"] = existing.get("created_at", now)
        doc["updated_at"] = now

        self.col.replace_one({"_id": ObjectId(product_id)}, doc)
        return self._doc_to_dict(self.col.find_one({"_id": ObjectId(product_id)}))

    def partial_update(self, product_id: str, data: dict) -> Optional[dict]:
        """
        Cập nhật một phần product (PATCH — chỉ các trường được gửi lên).

        Returns:
            Product dict sau khi cập nhật, hoặc None nếu không tìm thấy
        """
        patch = {k: v for k, v in data.items() if k not in ("id", "created_at", "updated_at")}
        if not patch:
            # Không có gì để cập nhật, trả về document hiện tại
            return self.find_by_id(product_id)

        patch["updated_at"] = datetime.now(timezone.utc)

        updated_doc = self.col.find_one_and_update(
            {"_id": ObjectId(product_id)},
            {"$set": patch},
            return_document=True,  # Trả về document SAU khi update
        )
        return self._doc_to_dict(updated_doc)

    def delete(self, product_id: str) -> bool:
        """
        Xóa một product.

        Returns:
            True nếu xóa thành công, False nếu không tìm thấy
        """
        result = self.col.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count == 1
