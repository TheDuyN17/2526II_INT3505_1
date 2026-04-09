/**
 * JWT Authentication Server
 * Features: Bearer Token, Refresh Token, Role-Based Access, Token Expiry, Security Audit
 */

const express = require("express");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const cors = require("cors");
const rateLimit = require("express-rate-limit");
const { v4: uuidv4 } = require("uuid");

const app = express();
app.use(express.json());
app.use(cors());

// ─────────────────────────────────────────────
// CONFIG
// ─────────────────────────────────────────────
const CONFIG = {
  ACCESS_TOKEN_SECRET: "super-secret-access-key-change-in-production",
  REFRESH_TOKEN_SECRET: "super-secret-refresh-key-change-in-production",
  ACCESS_TOKEN_EXPIRY: "5s",    // Very short for testing
  REFRESH_TOKEN_EXPIRY: "30s",   // Short for testing
};

// ─────────────────────────────────────────────
// IN-MEMORY STORES (use DB in production)
// ─────────────────────────────────────────────

// Users DB
const users = [
  {
    id: "1",
    username: "admin",
    // password: "admin123"
    password: bcrypt.hashSync("admin123", 10),
    role: "admin",
    email: "admin@example.com",
  },
  {
    id: "2",
    username: "editor",
    // password: "editor123"
    password: bcrypt.hashSync("editor123", 10),
    role: "editor",
    email: "editor@example.com",
  },
  {
    id: "3",
    username: "viewer",
    // password: "viewer123"
    password: bcrypt.hashSync("viewer123", 10),
    role: "viewer",
    email: "viewer@example.com",
  },
];

// Refresh token store: { token -> { userId, jti, createdAt } }
const refreshTokenStore = new Map();

// Token blacklist (revoked access tokens)
const tokenBlacklist = new Set();

// Audit log
const auditLog = [];

// ─────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────

function log(action, userId, ip, details = {}) {
  const entry = {
    id: uuidv4(),
    timestamp: new Date().toISOString(),
    action,
    userId: userId || "anonymous",
    ip,
    ...details,
  };
  auditLog.push(entry);
  console.log(`[AUDIT] ${entry.timestamp} | ${action} | user=${entry.userId} | ip=${ip}`);
  return entry;
}

function generateTokens(user) {
  const jti = uuidv4(); // Unique JWT ID for tracking

  const accessToken = jwt.sign(
    {
      sub: user.id,
      username: user.username,
      role: user.role,
      email: user.email,
      jti,
      type: "access",
    },
    CONFIG.ACCESS_TOKEN_SECRET,
    { expiresIn: CONFIG.ACCESS_TOKEN_EXPIRY }
  );

  const refreshJti = uuidv4();
  const refreshToken = jwt.sign(
    {
      sub: user.id,
      jti: refreshJti,
      type: "refresh",
    },
    CONFIG.REFRESH_TOKEN_SECRET,
    { expiresIn: CONFIG.REFRESH_TOKEN_EXPIRY }
  );

  // Store refresh token
  refreshTokenStore.set(refreshToken, {
    userId: user.id,
    jti: refreshJti,
    createdAt: new Date().toISOString(),
    username: user.username,
  });

  return { accessToken, refreshToken };
}

// ─────────────────────────────────────────────
// MIDDLEWARE
// ─────────────────────────────────────────────

// Rate limiting - prevent brute force
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, 
  max: 100,
  message: { error: "Too many requests, please try again later." },
});

// Verify access token
function authenticate(req, res, next) {
  const authHeader = req.headers["authorization"];

  // SECURITY CHECK: Detect token in wrong places
  const tokenInQuery = req.query.token || req.query.access_token;
  const tokenInBody = req.body && req.body.token;

  if (tokenInQuery) {
    log("SECURITY_ALERT", null, req.ip, {
      warning: "Token found in query string - URL exposure risk!",
      path: req.path,
    });
    return res.status(400).json({
      error: "Never send tokens in query strings - they appear in server logs and browser history!",
      hint: "Use Authorization: Bearer <token> header instead.",
    });
  }

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({
      error: "Missing or invalid Authorization header",
      hint: "Format: Authorization: Bearer <your-token>",
    });
  }

  const token = authHeader.split(" ")[1];

  // Check blacklist
  if (tokenBlacklist.has(token)) {
    log("BLOCKED_TOKEN", null, req.ip, { reason: "Token revoked/blacklisted" });
    return res.status(401).json({ error: "Token has been revoked" });
  }

  try {
    const decoded = jwt.verify(token, CONFIG.ACCESS_TOKEN_SECRET);

    if (decoded.type !== "access") {
      return res.status(401).json({ error: "Invalid token type" });
    }

    req.user = decoded;
    req.token = token;
    next();
  } catch (err) {
    if (err.name === "TokenExpiredError") {
      return res.status(401).json({
        error: "Access token expired",
        code: "TOKEN_EXPIRED",
        hint: "Use /auth/refresh with your refresh token to get a new access token",
      });
    }
    return res.status(401).json({ error: "Invalid token", detail: err.message });
  }
}

// Role-based authorization
function authorize(...roles) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      log("UNAUTHORIZED_ACCESS", req.user.sub, req.ip, {
        requiredRoles: roles,
        userRole: req.user.role,
        path: req.path,
      });
      return res.status(403).json({
        error: "Forbidden: insufficient permissions",
        yourRole: req.user.role,
        requiredRoles: roles,
      });
    }
    next();
  };
}

// ─────────────────────────────────────────────
// ROUTES: AUTH
// ─────────────────────────────────────────────

// POST /auth/login
app.post("/auth/login", authLimiter, async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: "Username and password required" });
  }

  const user = users.find((u) => u.username === username);

  if (!user || !(await bcrypt.compare(password, user.password))) {
    log("LOGIN_FAILED", null, req.ip, { username });
    return res.status(401).json({ error: "Invalid credentials" });
  }

  const { accessToken, refreshToken } = generateTokens(user);
  log("LOGIN_SUCCESS", user.id, req.ip, { username: user.username, role: user.role });

  res.json({
    message: "Login successful",
    accessToken,
    refreshToken,
    tokenType: "Bearer",
    expiresIn: CONFIG.ACCESS_TOKEN_EXPIRY,
    user: { id: user.id, username: user.username, role: user.role, email: user.email },
  });
});

// POST /auth/refresh
app.post("/auth/refresh", (req, res) => {
  const { refreshToken } = req.body;

  if (!refreshToken) {
    return res.status(400).json({ error: "Refresh token required" });
  }

  const stored = refreshTokenStore.get(refreshToken);
  if (!stored) {
    log("REFRESH_FAILED", null, req.ip, { reason: "Token not in store" });
    return res.status(401).json({ error: "Invalid or expired refresh token" });
  }

  try {
    const decoded = jwt.verify(refreshToken, CONFIG.REFRESH_TOKEN_SECRET);

    if (decoded.type !== "refresh") {
      return res.status(401).json({ error: "Invalid token type" });
    }

    const user = users.find((u) => u.id === decoded.sub);
    if (!user) {
      return res.status(401).json({ error: "User not found" });
    }

    // Rotate: invalidate old refresh token, issue new pair
    refreshTokenStore.delete(refreshToken);
    const tokens = generateTokens(user);

    log("TOKEN_REFRESHED", user.id, req.ip, { username: user.username });

    res.json({
      message: "Tokens refreshed",
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
      tokenType: "Bearer",
      expiresIn: CONFIG.ACCESS_TOKEN_EXPIRY,
    });
  } catch (err) {
    refreshTokenStore.delete(refreshToken); // Clean up expired token
    return res.status(401).json({ error: "Refresh token expired or invalid" });
  }
});

// POST /auth/logout
app.post("/auth/logout", authenticate, (req, res) => {
  const { refreshToken } = req.body;

  // Blacklist the current access token
  tokenBlacklist.add(req.token);

  // Remove refresh token
  if (refreshToken) {
    refreshTokenStore.delete(refreshToken);
  }

  log("LOGOUT", req.user.sub, req.ip, { username: req.user.username });

  res.json({ message: "Logged out successfully" });
});

// GET /auth/me - token introspection
app.get("/auth/me", authenticate, (req, res) => {
  res.json({
    user: {
      id: req.user.sub,
      username: req.user.username,
      role: req.user.role,
      email: req.user.email,
    },
    tokenInfo: {
      issuedAt: new Date(req.user.iat * 1000).toISOString(),
      expiresAt: new Date(req.user.exp * 1000).toISOString(),
      jti: req.user.jti,
    },
  });
});

// ─────────────────────────────────────────────
// ROUTES: PROTECTED APIs (role-based)
// ─────────────────────────────────────────────

// Public endpoint
app.get("/api/public", (req, res) => {
  res.json({ message: "This is public - no auth needed", timestamp: new Date().toISOString() });
});

// Any authenticated user
app.get("/api/profile", authenticate, (req, res) => {
  log("PROFILE_ACCESS", req.user.sub, req.ip);
  res.json({
    message: "Your profile",
    user: { id: req.user.sub, username: req.user.username, role: req.user.role },
  });
});

// Viewer + Editor + Admin
app.get("/api/data", authenticate, authorize("viewer", "editor", "admin"), (req, res) => {
  log("DATA_ACCESS", req.user.sub, req.ip);
  res.json({
    message: "Sensitive data - viewers and above",
    data: [
      { id: 1, value: "Record Alpha", secret: false },
      { id: 2, value: "Record Beta", secret: false },
    ],
    accessedBy: req.user.username,
  });
});

// Editor + Admin only
app.post("/api/data", authenticate, authorize("editor", "admin"), (req, res) => {
  log("DATA_WRITE", req.user.sub, req.ip, { body: req.body });
  res.json({
    message: "Data created - editors and above only",
    created: { id: uuidv4(), ...req.body, createdBy: req.user.username },
  });
});

// Admin only
app.get("/api/admin/users", authenticate, authorize("admin"), (req, res) => {
  log("ADMIN_USER_LIST", req.user.sub, req.ip);
  res.json({
    message: "All users - ADMIN ONLY",
    users: users.map((u) => ({ id: u.id, username: u.username, role: u.role, email: u.email })),
  });
});

app.delete("/api/admin/revoke-all", authenticate, authorize("admin"), (req, res) => {
  const count = refreshTokenStore.size;
  refreshTokenStore.clear();
  log("ADMIN_REVOKE_ALL", req.user.sub, req.ip, { tokensRevoked: count });
  res.json({ message: `Revoked all ${count} refresh tokens` });
});

// ─────────────────────────────────────────────
// SECURITY AUDIT ENDPOINT
// ─────────────────────────────────────────────

app.get("/api/admin/audit", authenticate, authorize("admin"), (req, res) => {
  const last50 = auditLog.slice(-50).reverse();
  res.json({
    total: auditLog.length,
    showing: last50.length,
    events: last50,
    activeRefreshTokens: refreshTokenStore.size,
    blacklistedTokens: tokenBlacklist.size,
  });
});

// ─────────────────────────────────────────────
// SECURITY TEST ENDPOINTS (demo purposes)
// ─────────────────────────────────────────────

// BAD PRACTICE demo: token in URL (will be rejected)
app.get("/api/insecure-demo", (req, res) => {
  const token = req.query.token;
  if (token) {
    log("SECURITY_ALERT", null, req.ip, {
      warning: "INSECURE: Token passed in URL query string!",
      exposure: "Token visible in: browser history, server logs, proxy logs, referrer headers",
    });
    return res.status(400).json({
      error: "SECURITY VIOLATION: Token in URL",
      issues: [
        "Token appears in browser history",
        "Token appears in server access logs",
        "Token appears in proxy/CDN logs",
        "Token sent in Referer header to third parties",
      ],
      fix: "Always use Authorization: Bearer <token> header",
    });
  }
  res.json({ message: "This endpoint demonstrates why tokens MUST NOT be in URLs" });
});

// ─────────────────────────────────────────────
// START
// ─────────────────────────────────────────────

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`\n🔐 JWT Demo Server running on http://localhost:${PORT}`);
  console.log("\n📋 Test Users:");
  console.log("  admin  / admin123  → role: admin");
  console.log("  editor / editor123 → role: editor");
  console.log("  viewer / viewer123 → role: viewer");
  console.log("\n📌 Key Endpoints:");
  console.log("  POST /auth/login     - Get tokens");
  console.log("  POST /auth/refresh   - Refresh tokens");
  console.log("  POST /auth/logout    - Revoke tokens");
  console.log("  GET  /auth/me        - Token introspection");
  console.log("  GET  /api/public     - No auth");
  console.log("  GET  /api/data       - viewer+");
  console.log("  POST /api/data       - editor+");
  console.log("  GET  /api/admin/*    - admin only");
  console.log("  GET  /api/admin/audit - Security audit log\n");
});
