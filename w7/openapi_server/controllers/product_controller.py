# coding: utf-8
"""
Product Controller — xử lý business logic cho 6 endpoints của Product resource.

Mỗi function được Connexion tự động gọi dựa trên operationId trong openapi.yaml.
Flow: HTTP Request -> Connexion validate -> Controller -> Repository -> MongoDB
"""

import math
from typing import Optional, Tuple

import connexion

from openapi_server.database.connection import get_database
from openapi_server.database.product_repository import ProductRepository

# ── Helper: lấy repository instance ─────────────────────────────────────────


def _repo() -> ProductRepository:
    """Tạo repository instance mới với database connection hiện tại."""
    return ProductRepository(get_database())


def _error(message: str, status: int, errors: Optional[list] = None) -> Tuple[dict, int]:
    """Tạo error response theo chuẩn API."""
    body = {"success": False, "message": message}
    if errors:
        body["errors"] = errors
    return body, status


def _ok(data, status: int = 200) -> Tuple[dict, int]:
    """Tạo success response."""
    return {"success": True, "data": data}, status


# ── Validation helpers ────────────────────────────────────────────────────────

VALID_CATEGORIES = ["Electronics", "Clothing", "Books", "Food", "Sports"]


def _validate_create(data: dict) -> list:
    """Kiểm tra dữ liệu khi tạo mới (POST, PUT) — tất cả required fields phải có."""
    errors = []

    name = data.get("name")
    if not name:
        errors.append({"field": "name", "message": "name là bắt buộc"})
    elif not (2 <= len(str(name)) <= 200):
        errors.append({"field": "name", "message": "name phải có 2-200 ký tự"})

    price = data.get("price")
    if price is None:
        errors.append({"field": "price", "message": "price là bắt buộc"})
    elif not isinstance(price, (int, float)) or price < 0:
        errors.append({"field": "price", "message": "price phải là số không âm"})

    category = data.get("category")
    if not category:
        errors.append({"field": "category", "message": "category là bắt buộc"})
    elif category not in VALID_CATEGORIES:
        errors.append({"field": "category", "message": f"category phải là một trong: {VALID_CATEGORIES}"})

    stock = data.get("stock", 0)
    if not isinstance(stock, int) or stock < 0:
        errors.append({"field": "stock", "message": "stock phải là số nguyên không âm"})

    return errors


def _validate_patch(data: dict) -> list:
    """Kiểm tra dữ liệu khi cập nhật một phần (PATCH) — chỉ validate trường nào có mặt."""
    errors = []

    if "name" in data:
        name = data["name"]
        if not name or not (2 <= len(str(name)) <= 200):
            errors.append({"field": "name", "message": "name phải có 2-200 ký tự"})

    if "price" in data:
        price = data["price"]
        if not isinstance(price, (int, float)) or price < 0:
            errors.append({"field": "price", "message": "price phải là số không âm"})

    if "category" in data and data["category"] not in VALID_CATEGORIES:
        errors.append({"field": "category", "message": f"category phải là một trong: {VALID_CATEGORIES}"})

    if "stock" in data:
        stock = data["stock"]
        if not isinstance(stock, int) or stock < 0:
            errors.append({"field": "stock", "message": "stock phải là số nguyên không âm"})

    return errors


# ── Endpoint handlers ─────────────────────────────────────────────────────────

def get_products(
    page: int = 1,
    limit: int = 10,
    sort: str = "created_at:desc",
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
) -> Tuple[dict, int]:
    """
    GET /api/products — Lấy danh sách products có phân trang.

    Connexion tự động inject các query params từ openapi.yaml.
    """
    try:
        # Đảm bảo giá trị hợp lệ
        page = max(1, int(page))
        limit = min(100, max(1, int(limit)))

        # Gom filters lại để truyền vào repository
        filters = {
            "category": category,
            "is_active": is_active,
            "search": search,
        }

        products, total = _repo().find_all(
            page=page, limit=limit, sort=sort, filters=filters
        )

        return _ok({
            "products": products,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": math.ceil(total / limit) if limit else 0,
            },
        })

    except Exception as exc:
        return _error(f"Lỗi server: {exc}", 500)


def get_product_by_id(id: str) -> Tuple[dict, int]:
    """
    GET /api/products/{id} — Lấy thông tin chi tiết một product.
    """
    if not ProductRepository.is_valid_id(id):
        return _error("ID không hợp lệ — phải là MongoDB ObjectId (24 ký tự hex)", 400)

    try:
        product = _repo().find_by_id(id)
        if product is None:
            return _error("Không tìm thấy product", 404)
        return _ok(product)
    except Exception as exc:
        return _error(f"Lỗi server: {exc}", 500)


def create_product(body: Optional[dict] = None) -> Tuple[dict, int]:
    """
    POST /api/products — Tạo product mới.

    Connexion tự động parse request body và truyền vào tham số 'body'.
    """
    data = body or connexion.request.get_json(silent=True)
    if not data:
        return _error("Request body là bắt buộc", 400)

    errors = _validate_create(data)
    if errors:
        return _error("Dữ liệu không hợp lệ", 400, errors)

    try:
        product = _repo().create(data)
        return _ok(product, 201)
    except Exception as exc:
        return _error(f"Lỗi server: {exc}", 500)


def replace_product(id: str, body: Optional[dict] = None) -> Tuple[dict, int]:
    """
    PUT /api/products/{id} — Thay thế hoàn toàn product.

    Tất cả required fields phải có trong request body.
    """
    if not ProductRepository.is_valid_id(id):
        return _error("ID không hợp lệ", 400)

    data = body or connexion.request.get_json(silent=True)
    if not data:
        return _error("Request body là bắt buộc", 400)

    errors = _validate_create(data)
    if errors:
        return _error("Dữ liệu không hợp lệ", 400, errors)

    try:
        product = _repo().update(id, data)
        if product is None:
            return _error("Không tìm thấy product", 404)
        return _ok(product)
    except Exception as exc:
        return _error(f"Lỗi server: {exc}", 500)


def update_product(id: str, body: Optional[dict] = None) -> Tuple[dict, int]:
    """
    PATCH /api/products/{id} — Cập nhật một phần product.

    Chỉ các trường được gửi trong body mới bị thay đổi.
    """
    if not ProductRepository.is_valid_id(id):
        return _error("ID không hợp lệ", 400)

    data = body or connexion.request.get_json(silent=True)
    if not data:
        return _error("Request body không được rỗng", 400)

    errors = _validate_patch(data)
    if errors:
        return _error("Dữ liệu không hợp lệ", 400, errors)

    try:
        product = _repo().partial_update(id, data)
        if product is None:
            return _error("Không tìm thấy product", 404)
        return _ok(product)
    except Exception as exc:
        return _error(f"Lỗi server: {exc}", 500)


def delete_product(id: str) -> Tuple[dict, int]:
    """
    DELETE /api/products/{id} — Xóa vĩnh viễn một product.
    """
    if not ProductRepository.is_valid_id(id):
        return _error("ID không hợp lệ", 400)

    try:
        deleted = _repo().delete(id)
        if not deleted:
            return _error("Không tìm thấy product", 404)
        return {"success": True, "message": "Xóa product thành công"}, 200
    except Exception as exc:
        return _error(f"Lỗi server: {exc}", 500)
