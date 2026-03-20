# OpenAPI Specification

## Giới thiệu

OpenAPI (trước đây là Swagger) là chuẩn phổ biến nhất để mô tả REST API. File được viết bằng YAML hoặc JSON.

## Cài đặt & Chạy

### Cách 1: Swagger Editor Online

1. Mở [editor.swagger.io](https://editor.swagger.io)
2. Paste nội dung file `library-api.yaml` vào bên trái
3. Swagger UI tự động render bên phải

### Cách 2: Chạy Swagger UI local

1. Tạo file `index.html` cùng thư mục:
```html
<!DOCTYPE html>
<html>
<head>
  <title>Library API - OpenAPI</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({ url: './library-api.yaml', dom_id: '#swagger-ui' });
  </script>
</body>
</html>
```

2. Chạy server:
```bash
npx http-server . -p 8080 -c-1
```

3. Mở http://localhost:8080/index.html

## Đặc điểm

- **Format:** YAML / JSON
- **Ưu điểm:** Chuẩn công nghiệp, hệ sinh thái tool rất lớn
- **Nhược điểm:** File YAML có thể dài dòng với API phức tạp