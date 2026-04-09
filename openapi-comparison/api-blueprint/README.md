# API Blueprint — Library Management API

## API Blueprint là gì?

API Blueprint là ngôn ngữ mô tả API dựa trên **Markdown** (cú pháp `.apib`).
Ưu điểm: dễ đọc, viết như viết tài liệu thông thường.
Nhược điểm: ít tool hỗ trợ hơn OpenAPI, không còn được maintain tích cực.

## Cấu trúc folder

```
api-blueprint/
├── library_api.apib   ← File spec (API Blueprint format)
├── server.py          ← Flask server render docs
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
- `http://localhost:8001/docs` — Trang tài liệu
- `http://localhost:8001/raw`  — File .apib gốc

## Tool render thay thế (dùng aglio — Node.js)

Nếu muốn render HTML tĩnh đẹp hơn:

```bash
# Cài aglio (yêu cầu Node.js)
npm install -g aglio

# Render ra file HTML
aglio -i library_api.apib -o docs.html

# Hoặc chạy live server
aglio -i library_api.apib -s
```

## Cú pháp cơ bản của API Blueprint

```apib
FORMAT: 1A
HOST: http://api.example.com

# Tên API

# Group TênNhóm

## Tên Resource [/path]

### Tên Action [GET]

+ Response 200 (application/json)

        { "key": "value" }
```
