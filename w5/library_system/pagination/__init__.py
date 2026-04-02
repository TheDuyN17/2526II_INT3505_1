"""
Pagination package - 3 pagination strategies:
1. page_based    : ?page=1&per_page=10
2. offset_limit  : ?offset=0&limit=10
3. cursor_based  : ?cursor=<encoded>&limit=10
"""

from .page_based import PageBasedPagination
from .offset_limit import OffsetLimitPagination
from .cursor_based import CursorBasedPagination


def detect_pagination_type(args: dict) -> str:
    """
    Auto-detect pagination type from query params.
    Priority: cursor > page > offset
    """
    if "cursor" in args:
        return "cursor"
    if "page" in args:
        return "page"
    if "offset" in args:
        return "offset"
    return "page"  # default


__all__ = [
    "PageBasedPagination",
    "OffsetLimitPagination",
    "CursorBasedPagination",
    "detect_pagination_type",
]
