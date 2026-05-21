# Mẫu thiết kế CRUD

## Mô tả
CRUD (Create, Read, Update, Delete) là pattern cơ bản nhất trong thiết kế API RESTful. Nó ánh xạ các phương thức HTTP tới các hành động tương ứng trên cơ sở dữ liệu.

## Ánh xạ HTTP Methods
- `POST /users` -> Create
- `GET /users` -> Read (List)
- `GET /users/{id}` -> Read (Single)
- `PUT /users/{id}` -> Update (Toàn bộ object) hoặc `PATCH` (Cập nhật một phần)
- `DELETE /users/{id}` -> Delete

## Chạy thử
```bash
python app.py
```

```bash
# Tạo user
curl -X POST http://localhost:5001/users -H "Content-Type: application/json" -d '{"name": "Charlie"}'
```
