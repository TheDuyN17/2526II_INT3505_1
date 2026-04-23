# 🧪 API Testing - Buổi 8

Test suite cho **JSONPlaceholder API** sử dụng Postman Collection + Newman.

---

## 🚀 Giới thiệu

Dự án thực hành **API Testing & Quality Assurance** buổi 8:

- **Postman Collection** (`product_api_tests.json`): 5 endpoints, mỗi endpoint có ≥3 test scripts
- **Newman**: Chạy collection tự động từ CLI, lặp 10 lần để đo hiệu năng
- **HTML Report**: Báo cáo đẹp qua `newman-reporter-htmlextra`

**API:** [JSONPlaceholder](https://jsonplaceholder.typicode.com) — Free fake REST API, không cần đăng ký.

---

## 📋 Yêu cầu hệ thống

| Công cụ | Phiên bản | Bắt buộc |
|---------|-----------|----------|
| Node.js | >= 16.0 | ✅ |
| npm | >= 8.0 | ✅ |
| Newman | >= 6.0 | ✅ |
| Git Bash | Bất kỳ | ✅ Windows |
| Postman | Bất kỳ | Chỉ để xem/sửa |

---

## ⚙️ Cài đặt

**Bước 1 — Cài Node.js** (nếu chưa có): https://nodejs.org → chọn **LTS**

```bash
node --version   # Kiểm tra: phải >= v16
npm --version
```

**Bước 2 — Cài Newman và reporter:**

```bash
npm install -g newman
npm install -g newman-reporter-htmlextra
```

**Bước 3 — Cấp quyền script** (Linux/macOS):

```bash
chmod +x run_tests.sh
```

---

## ▶️ Cách chạy

### Chạy bằng script (khuyến nghị)

```bash
./run_tests.sh
# hoặc
bash run_tests.sh
```

Script sẽ tự động: kiểm tra môi trường → chạy 10 iterations → tạo HTML/JSON report → in tóm tắt.

### Chạy Newman trực tiếp

```bash
# Chạy đơn giản
newman run product_api_tests.json

# Chạy 10 lần + HTML report
newman run product_api_tests.json \
  --iteration-count 10 \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export reports/report.html
```

### Xem report

```bash
open reports/report.html        # macOS
xdg-open reports/report.html   # Linux
start reports\report.html       # Windows
```

---

## 📁 Cấu trúc dự án

```
w8/
├── product_api_tests.json   # Postman Collection v2.1.0
├── run_tests.sh             # Script tự động chạy Newman
├── README.md                # File này
└── reports/                 # Output (tạo tự động)
    ├── report.html          # HTML report (mở bằng browser)
    └── report.json          # JSON report (dùng cho CI/CD)
```

---

## 🧪 Danh sách 5 endpoints được test

| # | Method | Endpoint | Mô tả | Status |
|---|--------|----------|-------|--------|
| 1 | `GET` | `/posts` | Lấy 100 bài viết | 200 |
| 2 | `GET` | `/posts/1` | Chi tiết bài viết ID=1 | 200 |
| 3 | `POST` | `/posts` | Tạo bài viết mới | 201 |
| 4 | `PUT` | `/posts/1` | Cập nhật toàn bộ bài viết | 200 |
| 5 | `DELETE` | `/posts/1` | Xóa bài viết | 200 |

**Mỗi endpoint có 5 test scripts:**

| Assert | Nội dung |
|--------|----------|
| ✅ Status code | 200 hoặc 201 đúng method |
| ✅ Response time | < 500ms |
| ✅ Body structure | Có đủ các field bắt buộc |
| ✅ Data type | userId là number, title là string... |
| ✅ Giá trị cụ thể | id=1, id=101 sau POST... |

---

## 📊 Ví dụ output

```
========================================
   API TESTING - JSONPlaceholder
   Iterations: 10
========================================

[1/4] Kiểm tra Newman...
[OK] Newman: 6.1.0

[2/4] Kiểm tra htmlextra reporter...
[OK] newman-reporter-htmlextra đã cài

[3/4] Chuẩn bị thư mục reports...
[OK] Thư mục reports/ sẵn sàng

[4/4] Chạy Newman (10 iterations)...
----------------------------------------

→ JSONPlaceholder API Tests

  GET All Posts ✓ (187ms)
  GET Single Post ✓ (143ms)
  POST Create Post ✓ (201ms)
  PUT Update Post ✓ (178ms)
  DELETE Post ✓ (156ms)

  ┌─────────────────────┬────────────────────────┐
  │ total requests      │ 50                     │
  │ total assertions    │ 250                    │
  │ failed assertions   │ 0                      │
  └─────────────────────┴────────────────────────┘

=== TÓM TẮT KẾT QUẢ ===
  Tổng assertions : 250
  Passed          : 250
  Failed          : 0
  Error rate      : 0.0%
  Avg response    : 173 ms

HTML Report: reports/report.html
JSON Report: reports/report.json

✓ TẤT CẢ TESTS ĐÃ PASS!
```

---

## 🔧 Troubleshooting

### ❌ `newman: command not found`

```bash
npm install -g newman
# Nếu vẫn lỗi, thêm npm bin vào PATH:
export PATH="$(npm prefix -g)/bin:$PATH"
```

### ❌ `Permission denied` khi chạy `.sh`

```bash
chmod +x run_tests.sh
bash run_tests.sh   # Hoặc dùng bash trực tiếp
```

### ❌ Lỗi trên Windows CMD / PowerShell

File `.sh` không chạy được trong CMD hoặc PowerShell.

**Giải pháp:** Dùng **Git Bash**:
1. Cài Git for Windows: https://git-scm.com
2. Chuột phải vào thư mục → **"Git Bash Here"**
3. Chạy: `bash run_tests.sh`

Hoặc chạy Newman trực tiếp trong PowerShell:
```powershell
mkdir -Force reports
newman run product_api_tests.json --iteration-count 10 --reporters cli,htmlextra --reporter-htmlextra-export reports/report.html
```

### ❌ Một số test fail do timeout

```bash
# Tăng ngưỡng timeout trong script (dòng --timeout-request)
# Hoặc chạy thẳng newman với timeout cao hơn:
newman run product_api_tests.json --timeout-request 15000
```

---

## 📚 Tài liệu tham khảo

| Tài liệu | Link |
|----------|------|
| JSONPlaceholder | https://jsonplaceholder.typicode.com |
| Postman | https://www.postman.com |
| Newman CLI | https://learning.postman.com/docs/collections/using-newman-cli |
| newman-reporter-htmlextra | https://github.com/DannyDainton/newman-reporter-htmlextra |
| Node.js | https://nodejs.org |
