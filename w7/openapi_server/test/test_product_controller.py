# coding: utf-8
"""
Unit tests cho Product Controller.

Sử dụng unittest.mock để mock MongoDB — tests chạy không cần MongoDB thật.
"""

from __future__ import absolute_import
import json
import unittest
from unittest.mock import MagicMock, patch

# Mock init_db trước khi import app để tránh kết nối MongoDB thật
with patch("openapi_server.database.connection.init_db"):
    from openapi_server.main import create_app


# ── Dữ liệu mẫu dùng trong tests ─────────────────────────────────────────────

SAMPLE_ID = "64a7b2c3d4e5f6789012345a"

SAMPLE_PRODUCT = {
    "id": SAMPLE_ID,
    "name": "Gaming Laptop",
    "description": "High-performance laptop",
    "price": 1299.99,
    "category": "Electronics",
    "stock": 50,
    "image_url": "https://example.com/laptop.jpg",
    "is_active": True,
    "created_at": "2024-01-15T10:00:00+00:00",
    "updated_at": "2024-01-15T10:00:00+00:00",
}

VALID_CREATE_PAYLOAD = {
    "name": "Test Product",
    "price": 99.99,
    "category": "Books",
    "stock": 10,
}


# ── Base test class ───────────────────────────────────────────────────────────

class BaseTestCase(unittest.TestCase):
    """Setup chung: tạo Flask test client và mock database."""

    def setUp(self):
        # Mock init_db để không cần MongoDB thật khi chạy test
        patcher = patch("openapi_server.database.connection.init_db")
        patcher.start()
        self.addCleanup(patcher.stop)

        connexion_app = create_app()
        self.client = connexion_app.app.test_client()
        self.app_ctx = connexion_app.app.app_context()
        self.app_ctx.push()

    def tearDown(self):
        self.app_ctx.pop()

    def _repo_mock(self, method_name, return_value):
        """Helper: tạo mock cho method của ProductRepository."""
        return patch(
            f"openapi_server.controllers.product_controller.ProductRepository.{method_name}",
            return_value=return_value,
        )


# ── Tests: GET /api/products ──────────────────────────────────────────────────

class TestGetProducts(BaseTestCase):

    @patch("openapi_server.controllers.product_controller._repo")
    def test_200_returns_paginated_list(self, mock_repo):
        mock_repo.return_value.find_all.return_value = ([SAMPLE_PRODUCT], 1)
        resp = self.client.get("/api/products")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]["products"]), 1)
        self.assertEqual(data["data"]["pagination"]["total"], 1)

    @patch("openapi_server.controllers.product_controller._repo")
    def test_200_empty_list_when_no_products(self, mock_repo):
        mock_repo.return_value.find_all.return_value = ([], 0)
        resp = self.client.get("/api/products")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["data"]["pagination"]["total"], 0)

    @patch("openapi_server.controllers.product_controller._repo")
    def test_200_pagination_params_reflected(self, mock_repo):
        mock_repo.return_value.find_all.return_value = ([], 0)
        resp = self.client.get("/api/products?page=3&limit=5")
        data = json.loads(resp.data)
        self.assertEqual(data["data"]["pagination"]["page"], 3)
        self.assertEqual(data["data"]["pagination"]["limit"], 5)

    @patch("openapi_server.controllers.product_controller._repo")
    def test_200_filter_by_category(self, mock_repo):
        mock_repo.return_value.find_all.return_value = ([SAMPLE_PRODUCT], 1)
        resp = self.client.get("/api/products?category=Electronics")
        self.assertEqual(resp.status_code, 200)
        # Kiểm tra repository được gọi với filter đúng
        call_kwargs = mock_repo.return_value.find_all.call_args[1]
        self.assertEqual(call_kwargs["filters"]["category"], "Electronics")


# ── Tests: GET /api/products/{id} ─────────────────────────────────────────────

class TestGetProductById(BaseTestCase):

    @patch("openapi_server.controllers.product_controller._repo")
    def test_200_found(self, mock_repo):
        mock_repo.return_value.find_by_id.return_value = SAMPLE_PRODUCT
        resp = self.client.get(f"/api/products/{SAMPLE_ID}")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["name"], "Gaming Laptop")

    @patch("openapi_server.controllers.product_controller._repo")
    def test_404_not_found(self, mock_repo):
        mock_repo.return_value.find_by_id.return_value = None
        resp = self.client.get(f"/api/products/{SAMPLE_ID}")
        self.assertEqual(resp.status_code, 404)
        data = json.loads(resp.data)
        self.assertFalse(data["success"])

    def test_400_invalid_id_format(self):
        resp = self.client.get("/api/products/not-an-object-id")
        self.assertEqual(resp.status_code, 400)


# ── Tests: POST /api/products ─────────────────────────────────────────────────

class TestCreateProduct(BaseTestCase):

    @patch("openapi_server.controllers.product_controller._repo")
    def test_201_created(self, mock_repo):
        mock_repo.return_value.create.return_value = {**SAMPLE_PRODUCT, **VALID_CREATE_PAYLOAD}
        resp = self.client.post(
            "/api/products",
            data=json.dumps(VALID_CREATE_PAYLOAD),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])

    def test_400_missing_required_name(self):
        payload = {"price": 10.0, "category": "Books"}
        resp = self.client.post(
            "/api/products",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        fields = [e["field"] for e in data.get("errors", [])]
        self.assertIn("name", fields)

    def test_400_missing_required_price(self):
        payload = {"name": "Test", "category": "Books"}
        resp = self.client.post(
            "/api/products",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_400_invalid_category(self):
        payload = {**VALID_CREATE_PAYLOAD, "category": "InvalidCategory"}
        resp = self.client.post(
            "/api/products",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_400_negative_price(self):
        payload = {**VALID_CREATE_PAYLOAD, "price": -1}
        resp = self.client.post(
            "/api/products",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_400_name_too_short(self):
        payload = {**VALID_CREATE_PAYLOAD, "name": "X"}
        resp = self.client.post(
            "/api/products",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)


# ── Tests: PUT /api/products/{id} ─────────────────────────────────────────────

class TestReplaceProduct(BaseTestCase):

    @patch("openapi_server.controllers.product_controller._repo")
    def test_200_replaced(self, mock_repo):
        mock_repo.return_value.update.return_value = SAMPLE_PRODUCT
        resp = self.client.put(
            f"/api/products/{SAMPLE_ID}",
            data=json.dumps(VALID_CREATE_PAYLOAD),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    @patch("openapi_server.controllers.product_controller._repo")
    def test_404_not_found(self, mock_repo):
        mock_repo.return_value.update.return_value = None
        resp = self.client.put(
            f"/api/products/{SAMPLE_ID}",
            data=json.dumps(VALID_CREATE_PAYLOAD),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)

    def test_400_invalid_id(self):
        resp = self.client.put(
            "/api/products/bad-id",
            data=json.dumps(VALID_CREATE_PAYLOAD),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)


# ── Tests: PATCH /api/products/{id} ──────────────────────────────────────────

class TestUpdateProduct(BaseTestCase):

    @patch("openapi_server.controllers.product_controller._repo")
    def test_200_patched(self, mock_repo):
        mock_repo.return_value.partial_update.return_value = SAMPLE_PRODUCT
        resp = self.client.patch(
            f"/api/products/{SAMPLE_ID}",
            data=json.dumps({"price": 999.99}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    @patch("openapi_server.controllers.product_controller._repo")
    def test_404_not_found(self, mock_repo):
        mock_repo.return_value.partial_update.return_value = None
        resp = self.client.patch(
            f"/api/products/{SAMPLE_ID}",
            data=json.dumps({"price": 1.0}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)

    def test_400_empty_body(self):
        resp = self.client.patch(
            f"/api/products/{SAMPLE_ID}",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)


# ── Tests: DELETE /api/products/{id} ─────────────────────────────────────────

class TestDeleteProduct(BaseTestCase):

    @patch("openapi_server.controllers.product_controller._repo")
    def test_200_deleted(self, mock_repo):
        mock_repo.return_value.delete.return_value = True
        resp = self.client.delete(f"/api/products/{SAMPLE_ID}")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])

    @patch("openapi_server.controllers.product_controller._repo")
    def test_404_not_found(self, mock_repo):
        mock_repo.return_value.delete.return_value = False
        resp = self.client.delete(f"/api/products/{SAMPLE_ID}")
        self.assertEqual(resp.status_code, 404)

    def test_400_invalid_id(self):
        resp = self.client.delete("/api/products/invalid")
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
