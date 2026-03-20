# So sánh các chuẩn tài liệu hóa API

## Bài tập Buổi 4 - API Specification & OpenAPI

### Bảng so sánh

| Tiêu chí | OpenAPI (Swagger) | API Blueprint | RAML | TypeSpec |
|----------|------------------|---------------|------|----------|
| **Format** | YAML / JSON | Markdown | YAML | TypeScript-like |
| **Phiên bản mới nhất** | 3.1.0 | 1A9 | 1.0 | 0.x (đang phát triển) |
| **Cú pháp** | Khai báo (declarative) | Viết tự nhiên (narrative) | Khai báo (declarative) | Định kiểu (type-safe) |
| **Độ phổ biến** | Rất cao | Trung bình | Thấp | Đang tăng |
| **Hệ sinh thái tool** | Rất lớn (Swagger UI, Codegen, Editor) | Trung bình (Apiary, Aglio) | Nhỏ (API Console, Workbench) | Nhỏ (tsc, OpenAPI emit) |
| **Ưu điểm chính** | Chuẩn công nghiệp, nhiều tool hỗ trợ | Dễ đọc, dễ viết | Tái sử dụng tốt (traits, types) | Type-safe, sinh OpenAPI tự động |
| **Nhược điểm** | YAML dài dòng với API phức tạp | Ít tool, cộng đồng nhỏ | Gần như bị bỏ rơi | Còn mới, chưa ổn định |
| **Phù hợp cho** | Mọi dự án REST API | Tài liệu nội bộ, prototype | Dự án cần reuse pattern | Dự án TypeScript, Azure |
| **Maintainer** | OpenAPI Initiative (Linux Foundation) | Apiary (Oracle) | MuleSoft (Salesforce) | Microsoft |

### Chi tiết từng format

#### 1. OpenAPI (Swagger)
- Chuẩn phổ biến nhất hiện nay để mô tả REST API
- Viết bằng YAML hoặc JSON
- Hệ sinh thái tool phong phú: Swagger UI, Swagger Editor, Swagger Codegen
- Hỗ trợ generate code client/server, test, mock server

#### 2. API Blueprint
- Viết bằng Markdown, rất dễ đọc
- Tập trung vào tính narrative (kể chuyện) thay vì khai báo
- Dùng Apiary làm nền tảng chính
- Phù hợp cho prototype và tài liệu nội bộ

#### 3. RAML (RESTful API Modeling Language)
- Viết bằng YAML với cú pháp riêng
- Mạnh về tái sử dụng: traits, resource types, libraries
- Được MuleSoft phát triển nhưng cộng đồng đã thu hẹp
- Ít được dùng trong dự án mới

#### 4. TypeSpec
- Ngôn ngữ mới của Microsoft, cú pháp giống TypeScript
- Sinh ra OpenAPI spec tự động từ code
- Type-safe, phát hiện lỗi tại compile time
- Phù hợp cho dự án lớn cần quản lý API chặt chẽ

### Kết luận

| Trường hợp | Nên dùng |
|-----------|----------|
| Dự án mới, cần tool phong phú | **OpenAPI** |
| Viết tài liệu nhanh, dễ đọc | **API Blueprint** |
| Dự án cần reuse pattern nhiều | **RAML** |
| Dự án TypeScript/Azure lớn | **TypeSpec** |

### Cấu trúc thư mục
```
openapi-comparison/
├── openapi/          # OpenAPI 3.0 spec
├── api-blueprint/    # API Blueprint spec  
├── raml/             # RAML spec
├── typespec/         # TypeSpec spec
└── codegen-demo/     # Demo sinh code từ OpenAPI
```

### Hướng dẫn chạy

Xem README.md trong từng thư mục con để biết cách cài đặt và chạy.