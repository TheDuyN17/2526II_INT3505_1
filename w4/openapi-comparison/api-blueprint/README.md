# API Blueprint

## Giới thiệu

API Blueprint là format mô tả API dựa trên Markdown, rất dễ đọc và viết. Được phát triển bởi Apiary (nay thuộc Oracle).

## Cài đặt & Chạy

### Cách 1: Apiary Online

1. Mở [apiary.io](https://apiary.io)
2. Tạo tài khoản, tạo API mới
3. Paste nội dung file `library-api.apib`

### Cách 2: Render bằng Aglio (local)

1. Cài đặt Aglio:
```bash
npm install -g aglio
```

2. Render HTML:
```bash
aglio -i library-api.apib -o output.html
```

3. Mở file `output.html` trong trình duyệt

### Cách 3: Preview trong VS Code

1. Cài extension **API Blueprint Viewer**
2. Mở file `.apib` → Ctrl+Shift+P → "API Blueprint: Preview"

## Codegen Demo: Sinh Python client từ .apib

### Bước 1: Sinh Python client

```bash
cd w4/openapi-comparison/api-blueprint
python generate_client.py
```

Output:
```
Reading: library-api.apib
  HOST: http://localhost:3000/api
  Found 5 endpoints:
    [GET] /books - Lấy danh sách sách
    [POST] /books - Thêm sách mới
    [GET] /books/{id} - Lấy sách theo ID
    [PUT] /books/{id} - Cập nhật sách
    [DELETE] /books/{id} - Xóa sách

Generated: generated_client.py
```

### Bước 2: Chạy backend Flask (terminal riêng)

```bash
cd w4/openapi-comparison/openapi
python app.py
```

### Bước 3: Chạy demo client

```bash
cd w4/openapi-comparison/api-blueprint
python generated_client.py
```

Demo sẽ tự động gọi toàn bộ 5 endpoints: GET list, POST, GET by ID, PUT, DELETE.

### Cấu trúc file

```
api-blueprint/
├── library-api.apib      # API Blueprint spec
├── generate_client.py    # Script sinh Python client từ .apib
├── generated_client.py   # Python client được sinh ra (auto-generated)
└── README.md
```

## Đặc điểm

- **Format:** Markdown
- **Ưu điểm:** Rất dễ đọc, viết tự nhiên như viết tài liệu
- **Nhược điểm:** Ít tool hỗ trợ, cộng đồng nhỏ, codegen hạn chế hơn OpenAPI