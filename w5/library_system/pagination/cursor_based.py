"""
Cursor-Based Pagination (Keyset Pagination)
-------------------------------------------
Query params : ?cursor=<base64_encoded_id>&limit=10
SQL equiv    : WHERE id > cursor_id ORDER BY id LIMIT limit

Ưu điểm:
  - Hiệu suất O(log n) thay vì O(n) - dùng index
  - Không bị lệch dữ liệu khi có insert/delete (stable pagination)
  - Phù hợp cho infinite scroll, real-time feeds
  - Scalable với dataset lớn (millions of rows)

Nhược điểm:
  - Không thể nhảy đến trang bất kỳ (chỉ next/prev)
  - Cursor phải unique và ordered (thường dùng id hoặc timestamp)
  - Khó implement hơn hai loại kia
  - Không thể hiển thị "trang X / Y"
"""

import base64
from flask import url_for


class CursorBasedPagination:
    def __init__(self, items: list, limit: int, endpoint: str,
                 id_field: str = "id", **kwargs):
        self.items = items
        self.limit = max(1, min(limit, 100))
        self.endpoint = endpoint
        self.id_field = id_field
        self.extra_params = kwargs

    @staticmethod
    def encode_cursor(value) -> str:
        """Encode a value to opaque cursor string"""
        return base64.urlsafe_b64encode(str(value).encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str):
        """Decode cursor string back to value"""
        try:
            return base64.urlsafe_b64decode(cursor.encode()).decode()
        except Exception:
            return None

    @property
    def has_next(self) -> bool:
        return len(self.items) > self.limit

    @property
    def visible_items(self) -> list:
        """Return only limit items (fetch limit+1 to detect has_next)"""
        return self.items[:self.limit]

    @property
    def next_cursor(self) -> str | None:
        if self.has_next:
            last_item = self.items[self.limit - 1]
            val = last_item.get(self.id_field) if isinstance(last_item, dict) else getattr(last_item, self.id_field)
            return self.encode_cursor(val)
        return None

    def _build_url(self, cursor=None) -> str:
        params = {**self.extra_params, "limit": self.limit}
        if cursor:
            params["cursor"] = cursor
        return url_for(self.endpoint, **params, _external=True)

    def get_links(self) -> dict:
        links = {"self": self._build_url()}
        if self.has_next:
            links["next"] = self._build_url(self.next_cursor)
        return links

    def get_meta(self) -> dict:
        return {
            "pagination_type": "cursor-based",
            "limit": self.limit,
            "has_next": self.has_next,
            "next_cursor": self.next_cursor,
            "count": len(self.visible_items),
        }

    def sql_clause(self, cursor_value=None) -> str:
        """Return SQL WHERE clause (for documentation)"""
        if cursor_value:
            return f"WHERE {self.id_field} > {cursor_value} ORDER BY {self.id_field} LIMIT {self.limit + 1}"
        return f"ORDER BY {self.id_field} LIMIT {self.limit + 1}"
