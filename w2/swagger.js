/**
 * Swagger / OpenAPI 3.0 Specification
 * REST API + JWT Authentication Demo — Buổi 2
 *
 * Code on Demand (V6): Server trả về Swagger UI — client render docs động
 */

const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'REST API + JWT Demo — Buổi 2',
      version: '4.0.0',
      description: `
## Kiến trúc REST và HTTP Fundamentals

Demo tích hợp **6 nguyên tắc REST** với JWT Authentication:

| Version | Nguyên tắc | Tính năng |
|---------|-----------|-----------|
| V1 | Client-Server | Express API, client/server tách biệt |
| V2 | Uniform Interface | HATEOAS, consistent format, PUT vs PATCH |
| V3 | Stateless | JWT token, server không lưu session |
| V4 | Cacheable | ETag, Cache-Control, 304 Not Modified |
| V5 | Layered System | Rate limiting, middleware pipeline |
| V6 | Code on Demand | Swagger UI served dynamically (trang này) |

### Auth Flow
1. \`POST /api/v1/auth/register\` hoặc \`POST /api/v1/auth/login\`
2. Copy **token** từ response
3. Click **Authorize** → nhập \`Bearer <token>\`
4. Gọi các protected endpoints

### Test Accounts
- **Admin**: \`a@example.com\` / \`admin123\`
- **User**: \`b@example.com\` / \`user123\`
      `.trim()
    },
    servers: [
      { url: 'http://localhost:3000', description: 'Local development server' }
    ],
    components: {
      securitySchemes: {
        BearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
          description: 'JWT token từ POST /api/v1/auth/login hoặc /register'
        }
      },
      schemas: {
        User: {
          type: 'object',
          properties: {
            id:         { type: 'integer', example: 1 },
            name:       { type: 'string',  example: 'Nguyễn Văn A' },
            email:      { type: 'string',  format: 'email', example: 'a@example.com' },
            role:       { type: 'string',  enum: ['admin', 'user'], example: 'admin' },
            created_at: { type: 'string',  format: 'date-time' },
            updated_at: { type: 'string',  format: 'date-time' },
            _links: {
              type: 'object',
              description: 'HATEOAS links — Uniform Interface (V2)',
              properties: {
                self:       { $ref: '#/components/schemas/HATEOASLink' },
                update:     { $ref: '#/components/schemas/HATEOASLink' },
                replace:    { $ref: '#/components/schemas/HATEOASLink' },
                delete:     { $ref: '#/components/schemas/HATEOASLink' },
                collection: { $ref: '#/components/schemas/HATEOASLink' }
              }
            }
          }
        },
        HATEOASLink: {
          type: 'object',
          properties: {
            href:   { type: 'string',  example: '/api/v1/users/1' },
            method: { type: 'string',  example: 'GET' }
          }
        },
        TokenResponse: {
          type: 'object',
          properties: {
            data: {
              type: 'object',
              properties: {
                token:         { type: 'string', description: 'JWT access token (1h)' },
                refresh_token: { type: 'string', description: 'Refresh token (7d)' },
                token_type:    { type: 'string', example: 'Bearer' },
                expires_in:    { type: 'integer', example: 3600 }
              }
            }
          }
        },
        ErrorResponse: {
          type: 'object',
          properties: {
            error: {
              type: 'object',
              properties: {
                code:      { type: 'integer', example: 400 },
                message:   { type: 'string',  example: 'Error description' },
                timestamp: { type: 'string',  format: 'date-time' },
                details:   { type: 'array',   items: { type: 'object' } }
              }
            }
          }
        },
        Pagination: {
          type: 'object',
          properties: {
            current_page: { type: 'integer', example: 1 },
            total_pages:  { type: 'integer', example: 3 },
            total_items:  { type: 'integer', example: 25 },
            limit:        { type: 'integer', example: 10 }
          }
        }
      }
    },
    tags: [
      { name: 'Auth',        description: 'Xác thực — JWT Register/Login/Refresh/Logout' },
      { name: 'Users',       description: 'Quản lý người dùng — CRUD được bảo vệ bởi JWT' },
      { name: 'Status Demo', description: 'Demo HTTP status codes (200→504)' },
      { name: 'System',      description: 'Health check và thông tin hệ thống' }
    ],
    paths: {
      // ─── AUTH ──────────────────────────────────────────────────────────────

      '/api/v1/auth/register': {
        post: {
          tags: ['Auth'],
          summary: 'Đăng ký tài khoản mới',
          description: `
Tạo tài khoản mới và nhận JWT token ngay lập tức.

**Status codes:**
- \`201 Created\` — Đăng ký thành công, kèm Location header
- \`400 Bad Request\` — Thiếu hoặc sai field
- \`409 Conflict\` — Email đã tồn tại
- \`500 Internal Server Error\` — Lỗi server
          `.trim(),
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  required: ['name', 'email', 'password'],
                  properties: {
                    name:     { type: 'string', example: 'Nguyễn Văn X' },
                    email:    { type: 'string', example: 'x@example.com' },
                    password: { type: 'string', minLength: 6, example: 'secret123' }
                  }
                }
              }
            }
          },
          responses: {
            201: { description: 'Đăng ký thành công', content: { 'application/json': { schema: { $ref: '#/components/schemas/TokenResponse' } } } },
            400: { description: 'Bad Request — thiếu field hoặc sai format', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            409: { description: 'Conflict — email đã tồn tại', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            500: { description: 'Internal Server Error', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } }
          }
        }
      },

      '/api/v1/auth/login': {
        post: {
          tags: ['Auth'],
          summary: 'Đăng nhập — nhận JWT token',
          description: `
Xác thực email/password, nhận **access token** (1h) và **refresh token** (7d).

**STATELESS (V3):** Server KHÔNG lưu session. Token tự chứa user_id, email, role.

**Status codes:**
- \`200 OK\` — Đăng nhập thành công
- \`400 Bad Request\` — Thiếu email hoặc password
- \`401 Unauthorized\` — Sai email hoặc password
          `.trim(),
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  required: ['email', 'password'],
                  properties: {
                    email:    { type: 'string', example: 'a@example.com' },
                    password: { type: 'string', example: 'admin123' }
                  }
                }
              }
            }
          },
          responses: {
            200: { description: 'Đăng nhập thành công', content: { 'application/json': { schema: { $ref: '#/components/schemas/TokenResponse' } } } },
            400: { description: 'Bad Request', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            401: { description: 'Unauthorized — sai credentials', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } }
          }
        }
      },

      '/api/v1/auth/refresh': {
        post: {
          tags: ['Auth'],
          summary: 'Làm mới access token (Token Rotation)',
          description: `
Đổi refresh token lấy access token mới. Refresh token cũ bị thu hồi ngay (Token Rotation).

**Status codes:**
- \`200 OK\` — Token mới đã được tạo
- \`400 Bad Request\` — Thiếu refresh_token
- \`401 Unauthorized\` — refresh_token hết hạn hoặc đã bị revoke
          `.trim(),
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  required: ['refresh_token'],
                  properties: {
                    refresh_token: { type: 'string', example: 'eyJhbGci...' }
                  }
                }
              }
            }
          },
          responses: {
            200: { description: 'Token mới', content: { 'application/json': { schema: { $ref: '#/components/schemas/TokenResponse' } } } },
            400: { description: 'Bad Request', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            401: { description: 'Unauthorized — refresh_token không hợp lệ', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } }
          }
        }
      },

      '/api/v1/auth/logout': {
        post: {
          tags: ['Auth'],
          summary: 'Đăng xuất — revoke refresh token',
          security: [{ BearerAuth: [] }],
          requestBody: {
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    refresh_token: { type: 'string', example: 'eyJhbGci...' }
                  }
                }
              }
            }
          },
          responses: {
            200: { description: 'Đăng xuất thành công' },
            401: { description: 'Unauthorized', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } }
          }
        }
      },

      '/api/v1/auth/me': {
        get: {
          tags: ['Auth'],
          summary: 'Xem profile từ JWT token (STATELESS)',
          description: `
Server decode token → biết ngay user là ai, không cần query DB bằng session.

**CACHEABLE (V4):** Trả ETag, hỗ trợ 304 Not Modified.

**Status codes:** 200, 304, 401, 404
          `.trim(),
          security: [{ BearerAuth: [] }],
          parameters: [{
            in: 'header',
            name: 'If-None-Match',
            schema: { type: 'string' },
            description: 'ETag từ response trước → 304 nếu data chưa đổi'
          }],
          responses: {
            200: { description: 'Profile', content: { 'application/json': { schema: { type: 'object', properties: { data: { $ref: '#/components/schemas/User' } } } } } },
            304: { description: 'Not Modified — data chưa đổi, dùng cache' },
            401: { description: 'Unauthorized', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            404: { description: 'Not Found', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } }
          }
        }
      },

      // ─── USERS ─────────────────────────────────────────────────────────────

      '/api/v1/users': {
        head: {
          tags: ['Users'],
          summary: 'HEAD — Metadata (không có body)',
          description: 'Kiểm tra X-Total-Count và ETag mà không download toàn bộ data.',
          security: [{ BearerAuth: [] }],
          responses: {
            200: {
              description: 'OK — headers only',
              headers: {
                'X-Total-Count': { schema: { type: 'integer' }, description: 'Tổng số users' },
                ETag: { schema: { type: 'string' }, description: 'Fingerprint của data' }
              }
            },
            401: { description: 'Unauthorized' }
          }
        },
        get: {
          tags: ['Users'],
          summary: 'Danh sách users — paginated, filterable, cacheable',
          description: `
Lấy danh sách users với **pagination**, **filtering**, **search**.

**CACHEABLE (V4):** ETag + Cache-Control: max-age=60.
**UNIFORM INTERFACE (V2):** HATEOAS pagination links.

**Status codes:** 200, 304, 401
          `.trim(),
          security: [{ BearerAuth: [] }],
          parameters: [
            { in: 'query', name: 'page',   schema: { type: 'integer', default: 1 },  description: 'Trang hiện tại' },
            { in: 'query', name: 'limit',  schema: { type: 'integer', default: 10 }, description: 'Số items/trang (max 100)' },
            { in: 'query', name: 'role',   schema: { type: 'string', enum: ['admin', 'user'] }, description: 'Lọc theo role' },
            { in: 'query', name: 'search', schema: { type: 'string' }, description: 'Tìm kiếm theo tên hoặc email' },
            { in: 'header', name: 'If-None-Match', schema: { type: 'string' }, description: 'ETag → 304 nếu chưa đổi' }
          ],
          responses: {
            200: {
              description: 'Danh sách users',
              headers: {
                ETag:            { schema: { type: 'string' } },
                'Cache-Control': { schema: { type: 'string' } },
                'X-Total-Count': { schema: { type: 'integer' } }
              },
              content: {
                'application/json': {
                  schema: {
                    type: 'object',
                    properties: {
                      data:       { type: 'array', items: { $ref: '#/components/schemas/User' } },
                      pagination: { $ref: '#/components/schemas/Pagination' },
                      _links:     { type: 'object' }
                    }
                  }
                }
              }
            },
            304: { description: 'Not Modified' },
            401: { description: 'Unauthorized', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } }
          }
        },
        post: {
          tags: ['Users'],
          summary: 'Tạo user mới [Admin Only]',
          description: `
Tạo user mới. **Chỉ Admin** có thể thực hiện.

**Status codes:** 201, 400, 401, 403, 409, 422, 500
          `.trim(),
          security: [{ BearerAuth: [] }],
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  required: ['name', 'email'],
                  properties: {
                    name:     { type: 'string', example: 'Nguyễn Văn X' },
                    email:    { type: 'string', example: 'x@example.com' },
                    password: { type: 'string', example: 'secret123' },
                    role:     { type: 'string', enum: ['admin', 'user'], default: 'user' }
                  }
                }
              }
            }
          },
          responses: {
            201: { description: 'Created', content: { 'application/json': { schema: { type: 'object', properties: { data: { $ref: '#/components/schemas/User' } } } } } },
            400: { description: 'Bad Request', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            401: { description: 'Unauthorized', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            403: { description: 'Forbidden — không phải admin', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            409: { description: 'Conflict — email đã tồn tại', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            422: { description: 'Unprocessable Entity — validation failed', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } }
          }
        }
      },

      '/api/v1/users/{id}': {
        get: {
          tags: ['Users'],
          summary: 'Chi tiết user — cacheable',
          security: [{ BearerAuth: [] }],
          parameters: [
            { in: 'path', name: 'id', required: true, schema: { type: 'integer' }, example: 1 },
            { in: 'header', name: 'If-None-Match', schema: { type: 'string' }, description: 'ETag → 304 nếu chưa đổi' }
          ],
          responses: {
            200: { description: 'User', content: { 'application/json': { schema: { type: 'object', properties: { data: { $ref: '#/components/schemas/User' } } } } } },
            304: { description: 'Not Modified' },
            401: { description: 'Unauthorized', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            404: { description: 'Not Found', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } }
          }
        },
        put: {
          tags: ['Users'],
          summary: 'Thay thế TOÀN BỘ user [Admin Only] — Idempotent',
          description: `
Full replacement. **Phải gửi đầy đủ tất cả fields**.

**Khác PATCH:** PATCH chỉ cần gửi field muốn sửa.
**Idempotent:** Gọi N lần → kết quả giống nhau.

**Status codes:** 200, 401, 403, 404, 422
          `.trim(),
          security: [{ BearerAuth: [] }],
          parameters: [
            { in: 'path', name: 'id', required: true, schema: { type: 'integer' }, example: 2 }
          ],
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  required: ['name', 'email', 'role'],
                  properties: {
                    name:  { type: 'string', example: 'Trần Thị B Updated' },
                    email: { type: 'string', example: 'b_new@example.com' },
                    role:  { type: 'string', enum: ['admin', 'user'], example: 'user' }
                  }
                }
              }
            }
          },
          responses: {
            200: { description: 'Replaced', content: { 'application/json': { schema: { type: 'object', properties: { data: { $ref: '#/components/schemas/User' } } } } } },
            401: { description: 'Unauthorized', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            403: { description: 'Forbidden', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            404: { description: 'Not Found', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            422: { description: 'Missing required fields', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } }
          }
        },
        patch: {
          tags: ['Users'],
          summary: 'Cập nhật MỘT PHẦN — chỉ gửi field muốn sửa',
          description: `
Partial update. Chỉ cần gửi fields muốn sửa.

**User thường:** Chỉ sửa được chính mình (403 nếu sửa người khác).
**Admin:** Sửa được tất cả, kể cả role.

**Status codes:** 200, 400, 401, 403, 404, 422
          `.trim(),
          security: [{ BearerAuth: [] }],
          parameters: [
            { in: 'path', name: 'id', required: true, schema: { type: 'integer' }, example: 2 }
          ],
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    name:  { type: 'string', example: 'Tên mới' },
                    email: { type: 'string', example: 'new@example.com' },
                    role:  { type: 'string', enum: ['admin', 'user'], description: 'Chỉ admin mới đổi được' }
                  }
                }
              }
            }
          },
          responses: {
            200: { description: 'Updated', content: { 'application/json': { schema: { type: 'object', properties: { data: { $ref: '#/components/schemas/User' } } } } } },
            400: { description: 'Bad Request', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            401: { description: 'Unauthorized', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            403: { description: 'Forbidden — sửa profile người khác', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            404: { description: 'Not Found', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } }
          }
        },
        delete: {
          tags: ['Users'],
          summary: 'Xóa user [Admin Only] — 204 No Content',
          security: [{ BearerAuth: [] }],
          parameters: [
            { in: 'path', name: 'id', required: true, schema: { type: 'integer' }, example: 5 }
          ],
          responses: {
            204: { description: 'No Content — xóa thành công, không có body' },
            401: { description: 'Unauthorized', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            403: { description: 'Forbidden — không phải admin', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } },
            404: { description: 'Not Found', content: { 'application/json': { schema: { $ref: '#/components/schemas/ErrorResponse' } } } }
          }
        }
      },

      // ─── ERROR DEMO ────────────────────────────────────────────────────────

      '/api/v1/error-demo/{code}': {
        get: {
          tags: ['Status Demo'],
          summary: 'Demo HTTP status codes',
          description: 'Trả về đúng HTTP status code được yêu cầu. Không cần authentication.',
          parameters: [{
            in: 'path',
            name: 'code',
            required: true,
            schema: { type: 'integer', enum: [200, 201, 400, 401, 403, 404, 409, 429, 500, 502, 503, 504] },
            example: 404
          }],
          responses: {
            200: { description: 'OK' },
            400: { description: 'Bad Request' },
            401: { description: 'Unauthorized' },
            403: { description: 'Forbidden' },
            404: { description: 'Not Found' },
            409: { description: 'Conflict' },
            429: { description: 'Too Many Requests' },
            500: { description: 'Internal Server Error' }
          }
        }
      },

      // ─── SYSTEM ────────────────────────────────────────────────────────────

      '/health': {
        get: {
          tags: ['System'],
          summary: 'Health check — danh sách endpoints và REST principles',
          responses: {
            200: { description: 'Server đang hoạt động' }
          }
        }
      }
    }
  },
  apis: []
};

const swaggerSpec = swaggerJsdoc(options);

module.exports = { swaggerSpec };
