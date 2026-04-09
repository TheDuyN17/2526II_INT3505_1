# openapi-comparison

So sánh 4 format tài liệu hóa API qua cùng một ứng dụng: **Library Management API**.

## Cấu trúc

```
openapi-comparison/
├── api-blueprint/      ← Markdown-based (.apib) — Port 8001
├── raml/               ← YAML-based (.raml)      — Port 8002
├── typespec/           ← TypeScript-like (.tsp)  — Port 8003
└── README.md
```

> **OpenAPI** đã có tại `Lecture_4/` — xem ở đó.

## So sánh nhanh

| Tiêu chí | OpenAPI | API Blueprint | RAML | TypeSpec |
|--|--|--|--|--|
| **Cú pháp** | YAML / JSON | Markdown | YAML | TypeScript-like |
| **File extension** | `.yaml` / `.json` | `.apib` | `.raml` | `.tsp` |
| **Phát triển bởi** | OpenAPI Initiative | Apiary | MuleSoft | Microsoft |
| **Render tool** | Swagger UI | Aglio | API Console | → compile ra OpenAPI |
| **Tái sử dụng** | `$ref` | Data Structures | `types` + `traits` | `model` + kế thừa |
| **Type safety** | ⚠️ manual | ❌ | ⚠️ | ✅ compiler check |
| **Tooling** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ (growing) |
| **Độ phổ biến 2024** | Chuẩn ngành | Ít dùng | Enterprise | Tăng mạnh |

## Chạy từng format

```bash
# API Blueprint (port 8001)
cd api-blueprint && pip install -r requirements.txt && python server.py

# RAML (port 8002)
cd raml && pip install -r requirements.txt && python server.py

# TypeSpec (port 8003) — cần compile trước
cd typespec && npm install && npx tsp compile library_api.tsp
pip install -r requirements.txt && python server.py
```

## Khi nào dùng cái nào?

- **OpenAPI** — mặc định cho mọi dự án, hệ sinh thái lớn nhất
- **API Blueprint** — khi team thích viết tài liệu dạng Markdown thuần
- **RAML** — khi dùng MuleSoft/Anypoint Platform
- **TypeSpec** — khi xây dựng API lớn, cần type safety, hoặc trong Microsoft ecosystem
