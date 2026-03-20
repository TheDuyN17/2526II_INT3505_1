# Demo sinh code/test từ tài liệu API

## Giới thiệu

Một trong những lợi ích lớn nhất của OpenAPI là khả năng tự động sinh code và test từ file spec.

## 1. Sinh Python client từ OpenAPI

### Cài đặt
```bash
npm install -g @openapitools/openapi-generator-cli
```

### Sinh code
```bash
openapi-generator-cli generate \
  -i ../openapi/library-api.yaml \
  -g python \
  -o ./python-client
```

Kết quả: thư mục `python-client/` chứa Python SDK hoàn chỉnh để gọi API.

## 2. Sinh Flask server stub từ OpenAPI
```bash
openapi-generator-cli generate \
  -i ../openapi/library-api.yaml \
  -g python-flask \
  -o ./flask-server
```

Kết quả: thư mục `flask-server/` chứa skeleton Flask server với đầy đủ routes.

## 3. Sinh test từ OpenAPI bằng Schemathesis

### Cài đặt
```bash
pip install schemathesis
```

### Chạy test tự động
```bash
schemathesis run http://localhost:3000/api/openapi.yaml
```

Hoặc test từ file local:
```bash
schemathesis run ../openapi/library-api.yaml --base-url http://localhost:3000/api
```

Schemathesis sẽ tự động:
- Tạo request ngẫu nhiên dựa trên schema
- Kiểm tra response có đúng format không
- Tìm lỗi 500, timeout, schema mismatch

## 4. Sinh Postman Collection từ OpenAPI

### Cách 1: Import trong Postman

1. Mở Postman → Import → chọn file `library-api.yaml`
2. Postman tự động tạo collection với tất cả endpoints

### Cách 2: Dùng CLI
```bash
npm install -g openapi-to-postmanv2
openapi2postmanv2 -s ../openapi/library-api.yaml -o postman-collection.json
```

## So sánh khả năng sinh code của các format

| Tính năng | OpenAPI | API Blueprint | RAML | TypeSpec |
|----------|---------|--------------|------|----------|
| Sinh client code | Hỗ trợ 40+ ngôn ngữ | Hạn chế | Có (raml-client-generator) | Qua OpenAPI |
| Sinh server stub | Hỗ trợ 30+ framework | Không | Có (raml-server) | Qua OpenAPI |
| Sinh test tự động | Schemathesis, Dredd | Dredd | Không phổ biến | Qua OpenAPI |
| Sinh Postman collection | Có | Có (hạn chế) | Có (hạn chế) | Qua OpenAPI |

## Kết luận

OpenAPI có hệ sinh thái sinh code mạnh nhất. Các format khác (RAML, API Blueprint) có khả năng sinh code hạn chế hơn. TypeSpec giải quyết bằng cách sinh ra OpenAPI trước, rồi dùng tool của OpenAPI.