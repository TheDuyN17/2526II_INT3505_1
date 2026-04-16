# coding: utf-8
# Được sinh tự động bởi OpenAPI Generator — do not edit manually.

from __future__ import absolute_import
from typing import Optional

from openapi_server.models.base_model import Model


class ProductCreate(Model):
    """
    Request body schema cho POST /api/products.
    Chỉ chứa các trường mà client được phép gửi khi tạo mới.
    """

    openapi_types = {
        "name": str,
        "description": str,
        "price": float,
        "category": str,
        "stock": int,
        "image_url": str,
        "is_active": bool,
    }

    attribute_map = {
        "name": "name",
        "description": "description",
        "price": "price",
        "category": "category",
        "stock": "stock",
        "image_url": "image_url",
        "is_active": "is_active",
    }

    VALID_CATEGORIES = ["Electronics", "Clothing", "Books", "Food", "Sports"]

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        category: Optional[str] = None,
        stock: int = 0,
        image_url: Optional[str] = None,
        is_active: bool = True,
    ):
        self._name = name
        self._description = description
        self._price = price
        self._category = category
        self._stock = stock
        self._image_url = image_url
        self._is_active = is_active

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: Optional[str]):
        if value is not None and not (2 <= len(value) <= 200):
            raise ValueError("name phải có độ dài từ 2 đến 200 ký tự")
        self._name = value

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value: Optional[str]):
        self._description = value

    @property
    def price(self) -> Optional[float]:
        return self._price

    @price.setter
    def price(self, value: Optional[float]):
        if value is not None and value < 0:
            raise ValueError("price phải >= 0")
        self._price = value

    @property
    def category(self) -> Optional[str]:
        return self._category

    @category.setter
    def category(self, value: Optional[str]):
        if value is not None and value not in self.VALID_CATEGORIES:
            raise ValueError(f"category phải là một trong: {self.VALID_CATEGORIES}")
        self._category = value

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, value: int):
        if value is not None and value < 0:
            raise ValueError("stock phải >= 0")
        self._stock = value

    @property
    def image_url(self) -> Optional[str]:
        return self._image_url

    @image_url.setter
    def image_url(self, value: Optional[str]):
        self._image_url = value

    @property
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool):
        self._is_active = value
