"""
Page-Based Pagination
---------------------
Query params : ?page=1&per_page=10
SQL equiv    : LIMIT per_page OFFSET (page-1)*per_page

Ưu điểm:
  - Thân thiện với người dùng (trang 1, trang 2, ...)
  - Dễ implement trên UI (page numbers)
  - Dễ cache từng trang

Nhược điểm:
  - Dữ liệu có thể bị lặp/bỏ sót nếu có insert/delete trong lúc duyệt
  - Hiệu suất giảm khi page lớn (OFFSET lớn)
"""

import math
from flask import request, url_for


class PageBasedPagination:
    def __init__(self, total: int, page: int, per_page: int, endpoint: str, **kwargs):
        self.total = total
        self.page = max(1, page)
        self.per_page = max(1, min(per_page, 100))
        self.total_pages = math.ceil(total / self.per_page) if total > 0 else 1
        self.endpoint = endpoint
        self.extra_params = kwargs

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    def _build_url(self, page: int) -> str:
        params = {**self.extra_params, "page": page, "per_page": self.per_page}
        return url_for(self.endpoint, **params, _external=True)

    def get_links(self) -> dict:
        links = {
            "self": self._build_url(self.page),
            "first": self._build_url(1),
            "last": self._build_url(self.total_pages),
        }
        if self.has_next:
            links["next"] = self._build_url(self.page + 1)
        if self.has_prev:
            links["prev"] = self._build_url(self.page - 1)
        return links

    def get_meta(self) -> dict:
        return {
            "pagination_type": "page-based",
            "page": self.page,
            "per_page": self.per_page,
            "total_items": self.total,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }

    def sql_clause(self) -> str:
        """Return SQL LIMIT/OFFSET clause (for documentation)"""
        return f"LIMIT {self.per_page} OFFSET {self.offset}"
