/**
 * Buổi 2: REST API + JWT Authentication Demo
 * ============================================
 * Tích hợp đầy đủ 6 nguyên tắc REST từ v1_client_server.py → v4_cacheable.py
 *
 * HTTP Methods: GET, POST, PUT, PATCH, DELETE, HEAD
 * Status codes: 200, 201, 204, 304, 400, 401, 403, 404, 409, 429, 500
 * REST Principles:
 *   V1: Client-Server    — Express API, client/server tách biệt hoàn toàn
 *   V2: Uniform Interface — HATEOAS links, consistent format, PUT vs PATCH
 *   V3: Stateless        — JWT token, server không lưu session
 *   V4: Cacheable        — ETag, Cache-Control, 304 Not Modified
 *   V5: Layered System   — Rate limiting, middleware pipeline, request ID
 *   V6: Code on Demand   — Swagger UI served dynamically
 */

const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const crypto = require('crypto');
const swaggerUi = require('swagger-ui-express');
const { swaggerSpec } = require('./swagger');

const app = express();
const PORT = process.env.PORT || 3000;
const SECRET_KEY = process.env.JWT_SECRET || 'rest-jwt-demo-secret-key-2026';
const REFRESH_SECRET = process.env.JWT_REFRESH_SECRET || 'rest-jwt-refresh-secret-2026';

// ============================================================================
// MIDDLEWARE — Layered System (V5)
// ============================================================================

app.use(express.json());
app.use(cors());

// Request ID — tracking mỗi request (Layered System)
app.use((req, res, next) => {
  req.requestId = crypto.randomUUID().substring(0, 8);
  res.setHeader('X-Request-ID', req.requestId);
  next();
});

// Rate Limiting — 429 Too Many Requests (Cacheable V4 + Layered V5)
const apiLimiter = rateLimit({
  windowMs: 60 * 1000,      // 60 giây
  max: 30,                  // 30 requests/phút
  standardHeaders: true,
  legacyHeaders: false,
  message: (req) => ({
    error: {
      code: 429,
      message: 'Rate limit exceeded. Try again in 60 seconds.',
      request_id: req.requestId,
      retry_after: 60,
      timestamp: new Date().toISOString()
    }
  }),
  handler: (req, res, next, options) => {
    res.status(429).json(options.message(req));
  }
});

app.use('/api/', apiLimiter);

// ============================================================================
// DATABASE (in-memory)
// ============================================================================

// Lưu refresh tokens hợp lệ (trong production: Redis)
const validRefreshTokens = new Set();

let users = [
  {
    id: 1, name: 'Nguyễn Văn A', email: 'a@example.com', role: 'admin',
    password: bcrypt.hashSync('admin123', 10), created_at: '2026-01-15T08:00:00Z'
  },
  {
    id: 2, name: 'Trần Thị B', email: 'b@example.com', role: 'user',
    password: bcrypt.hashSync('user123', 10), created_at: '2026-02-01T10:30:00Z'
  },
  {
    id: 3, name: 'Lê Văn C', email: 'c@example.com', role: 'user',
    password: bcrypt.hashSync('user456', 10), created_at: '2026-02-15T14:00:00Z'
  },
  {
    id: 4, name: 'Phạm Thị D', email: 'd@example.com', role: 'admin',
    password: bcrypt.hashSync('admin456', 10), created_at: '2026-03-01T09:00:00Z'
  },
  {
    id: 5, name: 'Hoàng Văn E', email: 'e@example.com', role: 'user',
    password: bcrypt.hashSync('user789', 10), created_at: '2026-03-10T16:00:00Z'
  }
];

let nextId = 6;

// ============================================================================
// HELPERS — Uniform Interface (V2)
// ============================================================================

/**
 * Response thành công — cấu trúc thống nhất (Uniform Interface).
 * Luôn có { data }, optional: pagination, _links
 */
const successResponse = (data, options = {}) => {
  const { pagination, links } = options;
  const response = { data };
  if (pagination) response.pagination = pagination;
  if (links) response._links = links;
  return response;
};

/**
 * Response lỗi — cấu trúc thống nhất (Uniform Interface).
 * Luôn có { error: { code, message, timestamp } }
 */
const errorResponse = (code, message, details = null) => {
  const response = {
    error: {
      code,
      message,
      timestamp: new Date().toISOString()
    }
  };
  if (details) response.error.details = details;
  return response;
};

/**
 * HATEOAS links cho user (Uniform Interface — Level 3 REST).
 * Response tự mô tả action tiếp theo mà client có thể làm.
 */
const buildUserLinks = (userId) => ({
  self:       { href: `/api/v1/users/${userId}`, method: 'GET' },
  update:     { href: `/api/v1/users/${userId}`, method: 'PATCH' },
  replace:    { href: `/api/v1/users/${userId}`, method: 'PUT' },
  delete:     { href: `/api/v1/users/${userId}`, method: 'DELETE' },
  collection: { href: '/api/v1/users',           method: 'GET' }
});

/** Loại bỏ password trước khi trả về client */
const safeUser = (user) => {
  const { password, ...rest } = user;
  return { ...rest, _links: buildUserLinks(user.id) };
};

/**
 * Tạo ETag từ data — fingerprint để check 304 Not Modified.
 * Cacheable principle (V4).
 */
const generateETag = (data) =>
  '"' + crypto.createHash('md5').update(JSON.stringify(data)).digest('hex') + '"';

/** Set Cache-Control headers */
const setCacheHeaders = (res, { noStore = false, maxAge = 60 } = {}) => {
  if (noStore) {
    res.setHeader('Cache-Control', 'no-store');
  } else {
    res.setHeader('Cache-Control', `public, max-age=${maxAge}`);
    res.setHeader('Vary', 'Authorization, Accept');
  }
};

// ============================================================================
// JWT TOKEN FUNCTIONS — Stateless (V3)
// ============================================================================

/**
 * Tạo access token (1h) và refresh token (7d).
 * STATELESS: Token tự chứa user_id, email, role — server không cần lưu session.
 */
const generateTokens = (user) => {
  const payload = { user_id: user.id, email: user.email, role: user.role };
  const accessToken = jwt.sign(payload, SECRET_KEY, { expiresIn: '1h' });
  const refreshToken = jwt.sign({ user_id: user.id }, REFRESH_SECRET, { expiresIn: '7d' });
  validRefreshTokens.add(refreshToken);
  return { accessToken, refreshToken };
};

// ============================================================================
// JWT MIDDLEWARE — Stateless Authentication (V3)
// ============================================================================

/**
 * require_auth: Kiểm tra JWT token trong mỗi request.
 *
 * STATELESS (V3): Server không nhớ ai đã login.
 * Mỗi request tự gửi token → server decode → xong.
 * Không cần query database hay session store.
 *
 * 401 Unauthorized: Chưa xác thực → "Bạn là ai?"
 */
const requireAuth = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json(
      errorResponse(401, 'Missing Authorization header. Use: Bearer <token>')
    );
  }

  const parts = authHeader.split(' ');
  if (parts.length !== 2 || parts[0] !== 'Bearer') {
    return res.status(401).json(
      errorResponse(401, 'Invalid Authorization format. Use: Bearer <token>')
    );
  }

  try {
    const payload = jwt.verify(parts[1], SECRET_KEY);
    req.currentUser = {
      user_id: payload.user_id,
      email:   payload.email,
      role:    payload.role
    };
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return res.status(401).json(
        errorResponse(401, 'Token has expired. Use POST /api/v1/auth/refresh to get a new token.')
      );
    }
    return res.status(401).json(errorResponse(401, 'Invalid token.'));
  }
};

/**
 * require_admin: Kiểm tra quyền admin.
 *
 * 403 Forbidden: Đã xác thực nhưng không đủ quyền → "Tôi biết bạn, nhưng bạn không có quyền"
 * SO SÁNH 401 vs 403:
 *   401: Chưa xác thực (thiếu/sai token)
 *   403: Đã xác thực nhưng sai role
 */
const requireAdmin = (req, res, next) => {
  if (req.currentUser.role !== 'admin') {
    return res.status(403).json(
      errorResponse(403, 'Admin access required.', {
        required_role: 'admin',
        your_role: req.currentUser.role
      })
    );
  }
  next();
};

// ============================================================================
// SWAGGER — Code on Demand (V6)
// ============================================================================

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: 'REST API + JWT Demo'
}));

// ============================================================================
// AUTH ENDPOINTS
// ============================================================================

/**
 * POST /api/v1/auth/register
 * Đăng ký tài khoản mới — trả về JWT ngay
 * Status: 201 Created | 400 Bad Request | 409 Conflict | 500 Server Error
 */
app.post('/api/v1/auth/register', async (req, res) => {
  try {
    const { name, email, password } = req.body || {};

    // Validation — 400 Bad Request
    const errors = [];
    if (!name)     errors.push({ field: 'name',     message: 'Name is required' });
    if (!email)    errors.push({ field: 'email',    message: 'Email is required' });
    else if (!email.includes('@'))
                   errors.push({ field: 'email',    message: 'Invalid email format' });
    if (!password) errors.push({ field: 'password', message: 'Password is required' });
    else if (password.length < 6)
                   errors.push({ field: 'password', message: 'Password must be at least 6 characters' });

    if (errors.length) {
      return res.status(400).json(errorResponse(400, 'Validation failed', errors));
    }

    // 409 Conflict — email đã tồn tại
    if (users.find(u => u.email === email)) {
      return res.status(409).json(errorResponse(409, `Email ${email} already exists`));
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = {
      id:         nextId++,
      name,
      email,
      role:       'user',
      password:   hashedPassword,
      created_at: new Date().toISOString()
    };
    users.push(newUser);

    const { accessToken, refreshToken } = generateTokens(newUser);

    // 201 Created + Location header (Uniform Interface)
    setCacheHeaders(res, { noStore: true });
    return res.status(201)
      .setHeader('Location', `/api/v1/users/${newUser.id}`)
      .json(successResponse({
        token:         accessToken,
        refresh_token: refreshToken,
        token_type:    'Bearer',
        expires_in:    3600,
        user:          safeUser(newUser)
      }));
  } catch (err) {
    console.error('[register] Error:', err);
    return res.status(500).json(errorResponse(500, 'Internal server error'));
  }
});

/**
 * POST /api/v1/auth/login
 * Đăng nhập → nhận JWT access token + refresh token
 * STATELESS: Server KHÔNG lưu session — token tự chứa mọi thông tin
 * Status: 200 OK | 400 Bad Request | 401 Unauthorized | 500 Server Error
 */
app.post('/api/v1/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body || {};

    if (!email || !password) {
      return res.status(400).json(errorResponse(400, 'Email and password are required'));
    }

    const user = users.find(u => u.email === email);
    if (!user || !(await bcrypt.compare(password, user.password))) {
      // 401 Unauthorized — sai credentials
      return res.status(401).json(errorResponse(401, 'Invalid email or password'));
    }

    const { accessToken, refreshToken } = generateTokens(user);

    setCacheHeaders(res, { noStore: true });
    return res.status(200).json(successResponse({
      token:         accessToken,
      refresh_token: refreshToken,
      token_type:    'Bearer',
      expires_in:    3600,
      user:          { id: user.id, name: user.name, email: user.email, role: user.role },
      _links: {
        profile: { href: `/api/v1/users/${user.id}`, method: 'GET' },
        users:   { href: '/api/v1/users',             method: 'GET' }
      }
    }));
  } catch (err) {
    console.error('[login] Error:', err);
    return res.status(500).json(errorResponse(500, 'Internal server error'));
  }
});

/**
 * POST /api/v1/auth/refresh
 * Đổi refresh token → access token mới (Token Rotation)
 * Status: 200 OK | 400 Bad Request | 401 Unauthorized
 */
app.post('/api/v1/auth/refresh', (req, res) => {
  const { refresh_token } = req.body || {};

  if (!refresh_token) {
    return res.status(400).json(errorResponse(400, 'refresh_token is required'));
  }

  // Kiểm tra refresh token còn hợp lệ không (chưa bị revoke)
  if (!validRefreshTokens.has(refresh_token)) {
    return res.status(401).json(
      errorResponse(401, 'Invalid or revoked refresh token. Please login again.')
    );
  }

  try {
    const payload = jwt.verify(refresh_token, REFRESH_SECRET);
    const user = users.find(u => u.id === payload.user_id);

    if (!user) {
      return res.status(401).json(errorResponse(401, 'User no longer exists'));
    }

    // Token Rotation: thu hồi token cũ, cấp token mới
    validRefreshTokens.delete(refresh_token);
    const { accessToken, refreshToken: newRefreshToken } = generateTokens(user);

    setCacheHeaders(res, { noStore: true });
    return res.status(200).json(successResponse({
      token:         accessToken,
      refresh_token: newRefreshToken,
      token_type:    'Bearer',
      expires_in:    3600
    }));
  } catch (err) {
    validRefreshTokens.delete(refresh_token);
    return res.status(401).json(
      errorResponse(401, 'Refresh token expired or invalid. Please login again.')
    );
  }
});

/**
 * POST /api/v1/auth/logout
 * Đăng xuất — revoke refresh token
 * Status: 200 OK | 401 Unauthorized
 */
app.post('/api/v1/auth/logout', requireAuth, (req, res) => {
  const { refresh_token } = req.body || {};
  if (refresh_token) {
    validRefreshTokens.delete(refresh_token);
  }
  setCacheHeaders(res, { noStore: true });
  return res.status(200).json({ message: 'Logged out successfully' });
});

/**
 * GET /api/v1/auth/me
 * Xem thông tin user hiện tại từ token — không cần query DB bằng username
 * STATELESS: Server decode token → biết ngay user là ai
 * Status: 200 OK | 304 Not Modified | 401 Unauthorized | 404 Not Found
 */
app.get('/api/v1/auth/me', requireAuth, (req, res) => {
  const user = users.find(u => u.id === req.currentUser.user_id);
  if (!user) {
    return res.status(404).json(errorResponse(404, 'User not found'));
  }

  const data = safeUser(user);
  const etag = generateETag(data);

  // 304 Not Modified — Cacheable (V4)
  if (req.headers['if-none-match'] === etag) {
    return res.status(304).setHeader('ETag', etag).send();
  }

  setCacheHeaders(res, { maxAge: 30 });
  res.setHeader('ETag', etag);
  return res.status(200).json(successResponse(data));
});

// ============================================================================
// USER ENDPOINTS — Protected by JWT
// ============================================================================

/**
 * HEAD /api/v1/users
 * Lấy metadata (headers only) — không có body
 * HTTP Method: HEAD (kiểm tra số lượng users, cache validity)
 * Status: 200 OK | 401 Unauthorized
 */
app.head('/api/v1/users', requireAuth, (req, res) => {
  const etag = generateETag(users.map(u => u.id));
  res.setHeader('X-Total-Count', users.length.toString());
  res.setHeader('X-Resource', 'users');
  res.setHeader('ETag', etag);
  setCacheHeaders(res, { maxAge: 60 });
  return res.status(200).send();
});

/**
 * GET /api/v1/users
 * Danh sách users với pagination, filtering, search
 * CACHEABLE (V4): ETag + Cache-Control: max-age=60
 * UNIFORM INTERFACE (V2): Consistent format, HATEOAS pagination links
 * Status: 200 OK | 304 Not Modified | 401 Unauthorized
 */
app.get('/api/v1/users', requireAuth, (req, res) => {
  let filtered = [...users];

  // Filtering theo role
  const { role, search } = req.query;
  if (role) {
    filtered = filtered.filter(u => u.role === role);
  }

  // Search theo name hoặc email
  if (search) {
    const q = search.toLowerCase();
    filtered = filtered.filter(u =>
      u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    );
  }

  // Pagination
  const page  = Math.max(1, parseInt(req.query.page)  || 1);
  const limit = Math.min(100, Math.max(1, parseInt(req.query.limit) || 10));
  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const start = (page - 1) * limit;
  const paginated = filtered.slice(start, start + limit);

  const data = paginated.map(safeUser);

  // ETag — 304 Not Modified (Cacheable V4)
  const etag = generateETag(data);
  if (req.headers['if-none-match'] === etag) {
    return res.status(304).setHeader('ETag', etag).send();
  }

  // HATEOAS pagination links (Uniform Interface V2)
  const baseUrl = `/api/v1/users?limit=${limit}${role ? `&role=${role}` : ''}${search ? `&search=${search}` : ''}`;
  const paginationLinks = {
    self:  `${baseUrl}&page=${page}`,
    first: `${baseUrl}&page=1`,
    last:  `${baseUrl}&page=${totalPages}`
  };
  if (page > 1) paginationLinks.prev = `${baseUrl}&page=${page - 1}`;
  if (page < totalPages) paginationLinks.next = `${baseUrl}&page=${page + 1}`;

  setCacheHeaders(res, { maxAge: 60 });
  res.setHeader('ETag', etag);
  res.setHeader('X-Total-Count', total.toString());

  return res.status(200).json(successResponse(data, {
    pagination: {
      current_page: page,
      total_pages:  totalPages,
      total_items:  total,
      limit
    },
    links: paginationLinks
  }));
});

/**
 * GET /api/v1/users/:id
 * Chi tiết 1 user — cacheable 60s với ETag
 * Status: 200 OK | 304 Not Modified | 401 Unauthorized | 404 Not Found
 */
app.get('/api/v1/users/:id', requireAuth, (req, res) => {
  const id = parseInt(req.params.id);
  if (isNaN(id)) {
    return res.status(400).json(errorResponse(400, 'Invalid user ID'));
  }

  const user = users.find(u => u.id === id);
  if (!user) {
    return res.status(404).json(errorResponse(404, `User with id ${id} not found`));
  }

  const data = safeUser(user);
  const etag = generateETag(data);

  // 304 Not Modified (Cacheable V4)
  if (req.headers['if-none-match'] === etag) {
    return res.status(304).setHeader('ETag', etag).send();
  }

  setCacheHeaders(res, { maxAge: 60 });
  res.setHeader('ETag', etag);
  return res.status(200).json(successResponse(data));
});

/**
 * POST /api/v1/users
 * Tạo user mới — chỉ admin (403 nếu không phải admin)
 * Status: 201 Created | 400 Bad Request | 401 Unauthorized | 403 Forbidden | 409 Conflict | 422 Unprocessable | 500 Error
 */
app.post('/api/v1/users', requireAuth, requireAdmin, async (req, res) => {
  try {
    const { name, email, password, role } = req.body || {};

    // Validation chi tiết — 422 Unprocessable Entity (Uniform Interface)
    const errors = [];
    if (!name)  errors.push({ field: 'name',  message: 'Name is required' });
    if (!email) errors.push({ field: 'email', message: 'Email is required' });
    else if (!email.includes('@'))
                errors.push({ field: 'email', message: 'Invalid email format' });

    if (errors.length) {
      return res.status(422).json(errorResponse(422, 'Validation failed', errors));
    }

    // 409 Conflict — email trùng
    if (users.find(u => u.email === email)) {
      return res.status(409).json(errorResponse(409, `Email ${email} already exists`));
    }

    const hashedPassword = await bcrypt.hash(password || 'default123', 10);
    const newUser = {
      id:         nextId++,
      name,
      email,
      role:       role || 'user',
      password:   hashedPassword,
      created_at: new Date().toISOString()
    };
    users.push(newUser);

    // 201 Created + Location header (Uniform Interface — chuẩn REST cho POST)
    setCacheHeaders(res, { noStore: true });
    return res.status(201)
      .setHeader('Location', `/api/v1/users/${newUser.id}`)
      .json(successResponse(safeUser(newUser)));
  } catch (err) {
    console.error('[POST /users] Error:', err);
    return res.status(500).json(errorResponse(500, 'Internal server error'));
  }
});

/**
 * PUT /api/v1/users/:id
 * Thay thế TOÀN BỘ resource — chỉ admin
 * UNIFORM INTERFACE (V2): PUT cần đầy đủ fields, thiếu 1 field → 422
 * Idempotent: gọi N lần kết quả giống nhau
 * Status: 200 OK | 400 | 401 | 403 | 404 | 422 Unprocessable Entity
 */
app.put('/api/v1/users/:id', requireAuth, requireAdmin, (req, res) => {
  const id = parseInt(req.params.id);
  const user = users.find(u => u.id === id);

  if (!user) {
    return res.status(404).json(errorResponse(404, `User with id ${id} not found`));
  }

  const { name, email, role } = req.body || {};

  // PUT yêu cầu ĐẦY ĐỦ fields — khác PATCH
  const errors = [];
  if (!name)  errors.push({ field: 'name',  message: 'Name is required for full replacement' });
  if (!email) errors.push({ field: 'email', message: 'Email is required for full replacement' });
  if (!role)  errors.push({ field: 'role',  message: 'Role is required for full replacement' });

  if (errors.length) {
    return res.status(422).json(errorResponse(422, 'PUT requires all fields', errors));
  }

  // Full replacement (idempotent)
  user.name       = name;
  user.email      = email;
  user.role       = role;
  user.updated_at = new Date().toISOString();

  setCacheHeaders(res, { noStore: true });
  return res.status(200).json(successResponse(safeUser(user)));
});

/**
 * PATCH /api/v1/users/:id
 * Cập nhật MỘT PHẦN — user chỉ sửa được chính mình, admin sửa được tất cả
 * UNIFORM INTERFACE (V2): PATCH chỉ cần gửi field muốn sửa (khác PUT)
 * Status: 200 OK | 400 | 401 | 403 Forbidden | 404 | 422
 */
app.patch('/api/v1/users/:id', requireAuth, (req, res) => {
  const id = parseInt(req.params.id);

  // 403 Forbidden — user thường chỉ sửa chính mình
  if (req.currentUser.role !== 'admin' && req.currentUser.user_id !== id) {
    return res.status(403).json(
      errorResponse(403, 'You can only update your own profile', {
        your_id:     req.currentUser.user_id,
        requested_id: id
      })
    );
  }

  const user = users.find(u => u.id === id);
  if (!user) {
    return res.status(404).json(errorResponse(404, `User with id ${id} not found`));
  }

  if (!req.body || Object.keys(req.body).length === 0) {
    return res.status(400).json(errorResponse(400, 'Request body is required'));
  }

  if (req.body.email && !req.body.email.includes('@')) {
    return res.status(422).json(errorResponse(422, 'Validation failed', [
      { field: 'email', message: 'Invalid email format' }
    ]));
  }

  // User thường không được tự đổi role
  const allowedFields = req.currentUser.role === 'admin'
    ? ['name', 'email', 'role']
    : ['name', 'email'];

  allowedFields.forEach(field => {
    if (req.body[field] !== undefined) {
      user[field] = req.body[field];
    }
  });

  user.updated_at = new Date().toISOString();

  setCacheHeaders(res, { noStore: true });
  return res.status(200).json(successResponse(safeUser(user)));
});

/**
 * DELETE /api/v1/users/:id
 * Xóa user — chỉ admin
 * Status: 204 No Content | 401 | 403 | 404 Not Found
 */
app.delete('/api/v1/users/:id', requireAuth, requireAdmin, (req, res) => {
  const id = parseInt(req.params.id);
  const index = users.findIndex(u => u.id === id);

  if (index === -1) {
    return res.status(404).json(errorResponse(404, `User with id ${id} not found`));
  }

  users.splice(index, 1);

  // 204 No Content — không cần body khi delete thành công
  setCacheHeaders(res, { noStore: true });
  return res.status(204).send();
});

// ============================================================================
// ERROR DEMO — Demo các HTTP status codes
// ============================================================================

/**
 * GET /api/v1/error-demo/:code
 * Demo các mã lỗi HTTP để học và test
 * Không cần authentication — public endpoint
 */
app.get('/api/v1/error-demo/:code', (req, res) => {
  const code = parseInt(req.params.code);
  const errorMap = {
    200: 'OK — Request thành công',
    201: 'Created — Resource mới đã được tạo thành công',
    400: 'Bad Request — Request sai cú pháp hoặc thiếu tham số bắt buộc',
    401: 'Unauthorized — Chưa xác thực: thiếu token, token hết hạn, hoặc sai token',
    403: 'Forbidden — Đã xác thực nhưng không đủ quyền truy cập resource này',
    404: 'Not Found — Resource không tồn tại hoặc URL sai',
    409: 'Conflict — Xung đột dữ liệu: email đã tồn tại, resource đã bị tạo',
    429: 'Too Many Requests — Vượt quá rate limit (30 req/phút)',
    500: 'Internal Server Error — Lỗi không xác định phía server',
    502: 'Bad Gateway — Proxy nhận response không hợp lệ từ upstream',
    503: 'Service Unavailable — Server tạm thời không khả dụng (bảo trì/quá tải)',
    504: 'Gateway Timeout — Upstream server không phản hồi trong thời gian cho phép'
  };

  if (errorMap[code]) {
    return res.status(code).json(errorResponse(code, errorMap[code]));
  }
  return res.status(400).json(errorResponse(400, `Unknown HTTP status code: ${code}`));
});

// ============================================================================
// HEALTH CHECK
// ============================================================================

app.get('/health', (req, res) => {
  return res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime_seconds: Math.floor(process.uptime()),
    users_count: users.length,
    active_refresh_tokens: validRefreshTokens.size,
    endpoints: {
      auth: {
        'POST /api/v1/auth/register': 'Đăng ký tài khoản → 201 + JWT',
        'POST /api/v1/auth/login':    'Đăng nhập → 200 + JWT + refresh_token',
        'POST /api/v1/auth/refresh':  'Làm mới token → 200 + new tokens',
        'POST /api/v1/auth/logout':   'Đăng xuất → 200, revoke refresh_token',
        'GET  /api/v1/auth/me':       'Xem profile từ token → 200 (cacheable)'
      },
      users: {
        'HEAD   /api/v1/users':     'Metadata (số lượng, ETag) → 200',
        'GET    /api/v1/users':     'Danh sách → 200 (paginated, cacheable)',
        'GET    /api/v1/users/:id': 'Chi tiết 1 user → 200 (cacheable)',
        'POST   /api/v1/users':     'Tạo user → 201 [admin only]',
        'PUT    /api/v1/users/:id': 'Thay thế toàn bộ → 200 [admin only]',
        'PATCH  /api/v1/users/:id': 'Cập nhật một phần → 200',
        'DELETE /api/v1/users/:id': 'Xóa → 204 [admin only]'
      },
      demo: {
        'GET /api/v1/error-demo/:code': 'Demo HTTP status codes',
        'GET /api-docs':                'Swagger UI documentation'
      }
    },
    rest_principles: {
      'V1_client_server':    '✅ Client-Server: Express API tách biệt khỏi client',
      'V2_uniform_interface': '✅ Uniform Interface: HATEOAS, consistent format, PUT vs PATCH',
      'V3_stateless':        '✅ Stateless: JWT token, server không lưu session',
      'V4_cacheable':        '✅ Cacheable: ETag, Cache-Control, 304 Not Modified',
      'V5_layered_system':   '✅ Layered System: Rate limiting, middleware pipeline',
      'V6_code_on_demand':   '✅ Code on Demand: Swagger UI served dynamically'
    }
  });
});

// ============================================================================
// 404 và ERROR HANDLERS
// ============================================================================

// 404 — Route không tồn tại
app.use((req, res) => {
  res.status(404).json(
    errorResponse(404, `Route ${req.method} ${req.path} not found. See /health for available endpoints.`)
  );
});

// 500 — Unhandled error
app.use((err, req, res, next) => {
  console.error('[Unhandled Error]', err.stack);
  res.status(500).json(errorResponse(500, 'Internal server error'));
});

// ============================================================================
// START SERVER
// ============================================================================

app.listen(PORT, () => {
  console.log('='.repeat(65));
  console.log('  Buổi 2: REST API + JWT Authentication Demo');
  console.log('='.repeat(65));
  console.log(`  Server:  http://localhost:${PORT}`);
  console.log(`  Swagger: http://localhost:${PORT}/api-docs`);
  console.log(`  Health:  http://localhost:${PORT}/health`);
  console.log('');
  console.log('  6 REST Principles:');
  console.log('  V1: ✅ Client-Server   — Express API, client/server tách biệt');
  console.log('  V2: ✅ Uniform Interface — HATEOAS, consistent format, PUT/PATCH');
  console.log('  V3: ✅ Stateless        — JWT, server không lưu session');
  console.log('  V4: ✅ Cacheable        — ETag, Cache-Control, 304 Not Modified');
  console.log('  V5: ✅ Layered System   — Rate limit, middleware, request ID');
  console.log('  V6: ✅ Code on Demand   — Swagger UI served dynamically');
  console.log('');
  console.log('  Test accounts (default):');
  console.log('  Admin: a@example.com / admin123');
  console.log('  User:  b@example.com / user123');
  console.log('');
  console.log('  Auth flow:');
  console.log('  1. POST /api/v1/auth/register  → Tạo tài khoản mới');
  console.log('  2. POST /api/v1/auth/login     → Lấy token');
  console.log('  3. Authorization: Bearer <token> → Gọi protected APIs');
  console.log('  4. POST /api/v1/auth/refresh   → Làm mới token');
  console.log('='.repeat(65));
});

module.exports = app;
