# TypeSpec

## Giới thiệu

TypeSpec là ngôn ngữ mới của Microsoft để mô tả API với cú pháp giống TypeScript. TypeSpec có thể tự động sinh ra file OpenAPI spec.

## Cài đặt & Chạy

### 1. Cài đặt TypeSpec CLI
```bash
npm install -g @typespec/compiler
```

### 2. Khởi tạo project
```bash
tsp init
```

Chọn template: Generic REST API

### 3. Cài dependencies
```bash
tsp install
```

### 4. Compile sang OpenAPI
```bash
tsp compile library-api.tsp
```

File OpenAPI sẽ được sinh ra trong thư mục `tsp-output/`

### 5. Xem kết quả

Mở file `tsp-output/@typespec/openapi3/openapi.yaml` trong Swagger Editor để xem.

## Đặc điểm

- **Format:** TypeScript-like (`.tsp`)
- **Ưu điểm:** Type-safe, phát hiện lỗi compile time, sinh OpenAPI tự động
- **Nhược điểm:** Còn mới, chưa ổn định, cần cài thêm tool
- **Lưu ý:** TypeSpec không phải format tài liệu trực tiếp mà là ngôn ngữ sinh ra tài liệu (OpenAPI)