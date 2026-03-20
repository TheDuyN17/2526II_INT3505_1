# RAML (RESTful API Modeling Language)

## Giới thiệu

RAML là ngôn ngữ mô tả API được phát triển bởi MuleSoft. Điểm mạnh là khả năng tái sử dụng cao với traits và resource types.

## Cài đặt & Chạy

### Cách 1: API Console Online

1. Mở [anypoint.mulesoft.com](https://anypoint.mulesoft.com)
2. Tạo API mới, paste nội dung file `library-api.raml`

### Cách 2: Chạy local với API Console

1. Cài đặt:
```bash
npm install -g api-console-cli
```

2. Chạy:
```bash
api-console-cli serve library-api.raml
```

### Cách 3: Preview trong VS Code

1. Cài extension **RAML** từ marketplace
2. Mở file `.raml` để xem syntax highlighting

## Đặc điểm

- **Format:** YAML (cú pháp riêng)
- **Ưu điểm:** Tái sử dụng tốt với traits, resource types, libraries
- **Nhược điểm:** Cộng đồng thu hẹp, ít tool mới
- **Lưu ý:** Trong ví dụ trên, `traits: searchable` được dùng để tái sử dụng query parameters cho nhiều endpoint