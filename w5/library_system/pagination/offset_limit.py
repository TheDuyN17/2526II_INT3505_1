"""
Offset-Limit Pagination
-----------------------
Query params : ?offset=0&limit=10
SQL equiv    : LIMIT limit OFFSET offset

Ưu điểm:
  - Trực tiếp mapping với SQL OFFSET/LIMIT
  - Linh hoạt hơn page-based (có thể bắt đầu ở bất kỳ row nào)
  - Hữu ích cho data export, analytics

Nhược điểm:
  - Không thân thiện người dùng bằng page-based
  - Cùng vấn đề hiệu suất với page lớn (OFFSET lớn => full scan)
  - Dữ liệu lệch nếu có insert/delete trong lúc duyệt
"""

import math
from flask import url_for


class OffsetLimitPagination:
    def __init__(self, total: int, offset: int, limit: int, endpoint: str, **kwargs):
        self.total = total
        self.offset = max(0, offset)
        self.limit = max(1, min(limit, 100))
        self.endpoint = endpoint
        self.extra_params = kwargs

    @property
    def has_next(self) -> bool:
        return self.offset + self.limit < self.total

    @property
    def has_prev(self) -> bool:
        return self.offset > 0

    @property
    def next_offset(self) -> int:
        return self.offset + self.limit

    @property
    def prev_offset(self) -> int:
        return max(0, self.offset - self.limit)

    @property
    def total_pages(self) -> int:
        return math.ceil(self.total / self.limit) if self.total > 0 else 1

    @property
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1

    def _build_url(self, offset: int) -> str:
        params = {**self.extra_params, "offset": offset, "limit": self.limit}
        return url_for(self.endpoint, **params, _external=True)

    def get_links(self) -> dict:
        links = {
            "self": self._build_url(self.offset),
            "first": self._build_url(0),
            "last": self._build_url(max(0, (self.total_pages - 1) * self.limit)),
        }
        if self.has_next:
            links["next"] = self._build_url(self.next_offset)
        if self.has_prev:
            links["prev"] = self._build_url(self.prev_offset)
        return links

    def get_meta(self) -> dict:
        return {
            "pagination_type": "offset-limit",
            "offset": self.offset,
            "limit": self.limit,
            "total_items": self.total,
            "total_pages": self.total_pages,
            "current_page": self.current_page,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }

    def sql_clause(self) -> str:
        """Return SQL LIMIT/OFFSET clause (for documentation)"""
        return f"LIMIT {self.limit} OFFSET {self.offset}"
