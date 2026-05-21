# Mẫu thiết kế Query Pattern

## Mô tả
Query Pattern được áp dụng cho các API lấy danh sách dữ liệu (`GET`). Nó cung cấp cho Client sự linh hoạt để lấy chính xác dữ liệu họ cần, tránh việc Over-fetching (tải quá nhiều) hoặc Under-fetching (tải không đủ).

## Các thành phần chính
1. **Filtering**: `?category=A&min_price=50`
2. **Sorting**: `?sort=-price` (dấu `-` thể hiện giảm dần)
3. **Pagination**: `?page=2&limit=20`

## Chạy thử
```bash
python app.py
```

```bash
# Lấy trang 2, mỗi trang 5 sản phẩm, thuộc category A, sắp xếp giá giảm dần
curl "http://localhost:5002/products?category=A&sort=-price&page=2&limit=5"
```
