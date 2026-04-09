# TypeSpec — Library Management API

## TypeSpec là gì?

**TypeSpec** là ngôn ngữ mô tả API do **Microsoft** phát triển (trước đây gọi là CADL).
Cú pháp lấy cảm hứng từ **TypeScript** — type-safe, hỗ trợ kế thừa, decorator.
Workflow: viết `.tsp` → **compile ra** OpenAPI / JSON Schema / Protobuf.

> TypeSpec không phải là format cuối cùng — nó là **nguồn sinh ra** các format khác.

## Cấu trúc folder

```
typespec/
├── library_api.tsp        ← File spec (TypeSpec language)
├── tspconfig.yaml         ← Cấu hình compiler
├── package.json           ← Node.js dependencies
├── server.py              ← Flask server (serve OpenAPI đã compile)
├── requirements.txt       ← Python dependencies
├── tsp-output/            ← Output sau khi compile (git ignore)
│   └── @typespec/
│       └── openapi3/
│           └── openapi.yaml
└── README.md
```

## Bước 1: Compile TypeSpec → OpenAPI

TypeSpec compiler chạy trên **Node.js** (yêu cầu Node.js >= 18).

```bash
# Cài Node.js dependencies
npm install

# Compile file .tsp ra OpenAPI YAML
npx tsp compile library_api.tsp

# Output sẽ nằm tại: tsp-output/@typespec/openapi3/openapi.yaml
```

## Bước 2: Chạy Python server

```bash
# Cài Python dependencies
pip install -r requirements.txt

# Chạy server
python server.py
```

Mở trình duyệt tại:
- `http://localhost:8003/docs`   — Swagger UI (từ OpenAPI đã compile)
- `http://localhost:8003/source` — File .tsp gốc
- `http://localhost:8003/status` — Kiểm tra trạng thái compile

## Lý do TypeSpec khác với 3 format kia

| | OpenAPI | API Blueprint | RAML | TypeSpec |
|--|--|--|--|--|
| Viết trực tiếp | ✅ | ✅ | ✅ | ❌ (compile) |
| Type-safe | ⚠️ | ❌ | ⚠️ | ✅ |
| Kế thừa type | ❌ | ❌ | ✅ | ✅ |
| Output | YAML/JSON | HTML | YAML | OpenAPI / Protobuf / JSON Schema |
| Phù hợp | Mọi dự án | Tài liệu đơn giản | Enterprise (MuleSoft) | Large-scale / Microsoft ecosystem |

## Cú pháp cơ bản TypeSpec

```typespec
import "@typespec/http";
using TypeSpec.Http;

model User {
  id: int32;
  name: string;
  email: string;
}

@route("/users")
interface Users {
  @get list(): User[];
  @post create(@body user: User): User;

  @get @route("{id}") read(@path id: int32): User;
  @put @route("{id}") update(@path id: int32, @body user: User): User;
  @delete @route("{id}") remove(@path id: int32): void;
}
```
