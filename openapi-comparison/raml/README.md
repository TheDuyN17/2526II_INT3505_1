# RAML — Library Management API

## RAML là gì?

**RAML** (RESTful API Modeling Language) được phát triển bởi MuleSoft/Salesforce.
Cú pháp dựa trên **YAML**, tập trung vào việc tái sử dụng qua `types` và `traits`.
Ưu điểm: cú pháp gọn, hỗ trợ kế thừa type mạnh mẽ.
Nhược điểm: ít phổ biến hơn OpenAPI, community nhỏ hơn.

## Cấu trúc folder

```
raml/
├── library_api.raml   ← File spec (RAML 1.0 format)
├── server.py          ← Flask server render docs (dùng PyYAML parse)
├── requirements.txt
└── README.md
```

## Cài đặt & Chạy

```bash
# 1. Cài dependencies
pip install -r requirements.txt

# 2. Chạy server
python server.py
```

Mở trình duyệt tại:
- `http://localhost:8002/docs` — Trang tài liệu
- `http://localhost:8002/raml` — File .raml gốc

## Tool render thay thế (dùng api-console — Node.js)

```bash
# Cài api-designer của MuleSoft (yêu cầu Node.js)
npm install -g api-workbench

# Hoặc dùng online tool
# https://anypoint.mulesoft.com/apiplatform/
```

## Cú pháp cơ bản của RAML

```yaml
#%RAML 1.0
title: My API
baseUri: http://api.example.com/{version}
version: v1

types:
  User:
    type: object
    properties:
      id: integer
      name: string

/users:
  get:
    description: Lấy danh sách users
    responses:
      200:
        body:
          application/json:
            type: User[]
  post:
    body:
      application/json:
        type: User
    responses:
      201:
        body:
          application/json:
            type: User
```

## Điểm đặc biệt của RAML so với OpenAPI

- **`types`** = `components/schemas` nhưng hỗ trợ kế thừa (inheritance) mạnh hơn
- **`traits`** = patterns tái sử dụng cho nhiều endpoint (không có trong OpenAPI)
- **`resourceTypes`** = template cho cả resource (không có trong OpenAPI)
